from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import asyncpg
import os
from datetime import datetime
from dotenv import load_dotenv
import logging
from typing import List, Optional
import asyncio
from pathlib import Path

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

app = FastAPI(title="Telegram Bot Admin Panel")

# Configure templates
templates = Jinja2Templates(directory="templates")

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

@app.get("/")
async def index(request: Request):
    stats = await admin.get_user_stats()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "stats": stats}
    )

@app.get("/users")
async def users(request: Request):
    users_list = await admin.get_all_users()
    return templates.TemplateResponse(
        "users.html",
        {"request": request, "users": users_list}
    )

@app.get("/users/demo")
async def users_demo(request: Request):
    users_list = await admin.get_users_with_demo()
    return templates.TemplateResponse(
        "users.html",
        {"request": request, "users": users_list, "demo_only": True}
    )

@app.post("/api/delete_user/{user_id}")
async def api_delete_user(user_id: int):
    success = await admin.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete user")
    return JSONResponse(content={"success": True})

@app.post("/api/reset_demo/{user_id}")
async def api_reset_demo(user_id: int):
    success = await admin.reset_demo_access(user_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to reset demo access")
    return JSONResponse(content={"success": True})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000) 