import asyncio
import asyncpg
import os
from datetime import datetime
from dotenv import load_dotenv
import logging
from typing import List, Optional

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class AdminTools:
    def __init__(self):
        self.pool = None

    async def connect(self):
        """Establish database connection"""
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

async def print_user_table(users: List[dict]):
    """Print formatted user table"""
    print("\nUser ID\t\tLanguage\tDemo Access\tAccess Date\t\tCreated At")
    print("-" * 100)
    for user in users:
        print(f"{user['user_id']}\t{user['language']}\t\t"
              f"{'Yes' if user['has_demo_access'] else 'No'}\t\t"
              f"{user['demo_access_granted_at'] or 'N/A'}\t"
              f"{user['created_at']}")

async def main():
    admin = AdminTools()
    await admin.connect()

    while True:
        print("\nAdmin Tools Menu:")
        print("1. Show all users")
        print("2. Show users with demo access")
        print("3. Delete user")
        print("4. Reset user's demo access")
        print("5. Show statistics")
        print("6. Exit")

        choice = input("\nEnter your choice (1-6): ")

        try:
            if choice == "1":
                users = await admin.get_all_users()
                await print_user_table(users)
            elif choice == "2":
                users = await admin.get_users_with_demo()
                await print_user_table(users)
            elif choice == "3":
                user_id = int(input("Enter user ID to delete: "))
                if await admin.delete_user(user_id):
                    print(f"User {user_id} deleted successfully")
                else:
                    print("Failed to delete user")
            elif choice == "4":
                user_id = int(input("Enter user ID to reset demo access: "))
                if await admin.reset_demo_access(user_id):
                    print(f"Demo access reset for user {user_id}")
                else:
                    print("Failed to reset demo access")
            elif choice == "5":
                stats = await admin.get_user_stats()
                print("\nStatistics:")
                print(f"Total users: {stats['total_users']}")
                print(f"Users with active demo: {stats['active_demo_users']}")
                print(f"Inactive users: {stats['inactive_users']}")
            elif choice == "6":
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except Exception as e:
            print(f"An error occurred: {e}")

    await admin.close()

if __name__ == "__main__":
    asyncio.run(main()) 