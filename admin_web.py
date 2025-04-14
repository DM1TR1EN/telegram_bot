from fastapi import FastAPI, Request, HTTPException, Depends, status, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import asyncpg
import os
from dotenv import load_dotenv
import logging
from typing import List, Optional, Union
import asyncio
from pathlib import Path
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Security settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(
    title="Telegram Bot Admin Panel",
    docs_url=None,  # Disable docs in production
    redoc_url=None,  # Disable redoc in production
    openapi_url=None  # Disable openapi in production
)

# Configure templates
templates_dir = Path("/app/templates")
logging.info(f"Templates directory: {templates_dir}")
if not templates_dir.exists():
    logging.error(f"Templates directory does not exist: {templates_dir}")
    raise RuntimeError(f"Templates directory does not exist: {templates_dir}")
templates = Jinja2Templates(directory=str(templates_dir))

# Mount static files if directory exists
static_dir = Path("/app/static")
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    logging.info(f"Static directory mounted: {static_dir}")

# Trust proxy headers
app.trusted_hosts = ["*"]

@app.middleware("http")
async def add_proxy_headers(request: Request, call_next):
    response = await call_next(request)
    if "x-forwarded-proto" in request.headers:
        response.headers["X-Forwarded-Proto"] = request.headers["x-forwarded-proto"]
    return response

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None

class User(BaseModel):
    username: str
    disabled: Union[bool, None] = None

class UserInDB(User):
    hashed_password: str

# Hardcoded admin user (in production, this should be stored in the database)
admin_username = os.getenv("ADMIN_USERNAME", "admin")
admin_password = os.getenv("ADMIN_PASSWORD", "admin")
password_hash = pwd_context.hash(admin_password)
logging.info(f"Admin credentials: {admin_username}/{admin_password} (hash: {password_hash[:10]}...)")

fake_users_db = {
    admin_username: {
        "username": admin_username,
        "hashed_password": password_hash,
        "disabled": False,
    }
}

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        logging.warning(f"User not found: {username}")
        return False
    if not verify_password(password, user.hashed_password):
        logging.warning(f"Invalid password for user: {username}")
        return False
    logging.info(f"Authentication successful for user: {username}")
    return user

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(request: Request):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = request.cookies.get("access_token")
        if not token:
            raise credentials_exception
        
        # Remove 'Bearer ' prefix if present
        if token.startswith("Bearer "):
            token = token[7:]
            
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

class AdminTools:
    def __init__(self):
        self.pool = None

    async def connect(self):
        """Establish database connection"""
        if self.pool is None:
            self.pool = await asyncpg.create_pool(
                user=os.getenv("POSTGRES_USER", "postgres"),
                password=os.getenv("POSTGRES_PASSWORD", "postgres"),
                database=os.getenv("POSTGRES_DB", "telegram_bot"),
                host=os.getenv("POSTGRES_HOST", "localhost"),
                port=os.getenv("POSTGRES_PORT", "5432")
            )

    async def close(self):
        """Close database connection"""
        if self.pool:
            await self.pool.close()
            self.pool = None

    async def get_all_users(self) -> List[dict]:
        """Get all users with their demo access information"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT user_id, language, has_demo_access, demo_access_granted_at, created_at
                FROM users
                ORDER BY created_at DESC
            """)
            return [dict(row) for row in rows]

    async def get_users_with_demo(self) -> List[dict]:
        """Get only users who have demo access"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT user_id, language, has_demo_access, demo_access_granted_at, created_at
                FROM users
                WHERE has_demo_access = true
                ORDER BY demo_access_granted_at DESC
            """)
            return [dict(row) for row in rows]

    async def delete_user(self, user_id: int) -> bool:
        """Delete specific user from database"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("DELETE FROM users WHERE user_id = $1", user_id)
                return True
        except Exception as e:
            logging.error(f"Error deleting user {user_id}: {e}")
            return False

    async def reset_demo_access(self, user_id: int) -> bool:
        """Reset demo access for specific user"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    UPDATE users
                    SET has_demo_access = false,
                        demo_access_granted_at = NULL
                    WHERE user_id = $1
                """, user_id)
                return True
        except Exception as e:
            logging.error(f"Error resetting demo access for user {user_id}: {e}")
            return False

    async def get_user_stats(self) -> dict:
        """Get statistics about users"""
        async with self.pool.acquire() as conn:
            total_users = await conn.fetchval("SELECT COUNT(*) FROM users")
            active_demo = await conn.fetchval("SELECT COUNT(*) FROM users WHERE has_demo_access = true")
            return {
                "total_users": total_users,
                "active_demo_users": active_demo,
                "inactive_users": total_users - active_demo
            }

admin = AdminTools()

@app.on_event("startup")
async def startup():
    await admin.connect()

@app.on_event("shutdown")
async def shutdown():
    await admin.close()

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/")
async def index(request: Request):
    try:
        current_user = await get_current_user(request)
        stats = await admin.get_user_stats()
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "stats": stats, "current_user": current_user}
        )
    except HTTPException as e:
        if e.status_code == 401:
            return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
        raise e

@app.get("/login")
async def login_page(request: Request):
    logging.info("Accessing login page")
    try:
        # Check if user is already authenticated
        await get_current_user(request)
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    except HTTPException:
        try:
            return templates.TemplateResponse("login.html", {"request": request})
        except Exception as e:
            logging.error(f"Error rendering login template: {e}")
            raise HTTPException(status_code=500, detail="Error rendering login page")

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    logging.info(f"Login attempt for user: {username}")
    user = authenticate_user(fake_users_db, username, password)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid username or password"}
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=False,  # Set to False for local development
        samesite="lax",
        max_age=1800,  # 30 minutes in seconds
        path="/"  # Explicitly set path
    )
    return response

@app.get("/users")
async def users(request: Request, current_user: User = Depends(get_current_active_user)):
    users_list = await admin.get_all_users()
    return templates.TemplateResponse(
        "users.html",
        {"request": request, "users": users_list, "current_user": current_user}
    )

@app.get("/users/demo")
async def users_demo(request: Request, current_user: User = Depends(get_current_active_user)):
    users_list = await admin.get_users_with_demo()
    return templates.TemplateResponse(
        "users.html",
        {"request": request, "users": users_list, "demo_only": True, "current_user": current_user}
    )

@app.post("/api/delete_user/{user_id}")
async def api_delete_user(user_id: int, current_user: User = Depends(get_current_active_user)):
    success = await admin.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete user")
    return JSONResponse(content={"success": True})

@app.post("/api/reset_demo/{user_id}")
async def api_reset_demo(user_id: int, current_user: User = Depends(get_current_active_user)):
    success = await admin.reset_demo_access(user_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to reset demo access")
    return JSONResponse(content={"success": True})

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token", path="/")
    return response

# Print all registered routes
@app.on_event("startup")
async def startup_event():
    logging.info("Registered routes:")
    for route in app.routes:
        logging.info(f"{route.methods} {route.path}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000) 