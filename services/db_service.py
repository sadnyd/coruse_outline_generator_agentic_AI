from utils.flow_logger import function_logger
"""
Database Service Abstraction Layer

Centralizes all database interactions. Swap providers here without touching business logic.
Supports: PostgreSQL, MongoDB, SQLite, Firebase, Supabase, etc.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from enum import Enum
from dataclasses import dataclass
import os
from datetime import datetime


class DatabaseProvider(str, Enum):
    """Supported database providers."""
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"
    SQLITE = "sqlite"
    MYSQL = "mysql"
    DYNAMODB = "dynamodb"
    FIRESTORE = "firestore"
    SUPABASE = "supabase"


@dataclass
class DatabaseConfig:
    """Database Configuration."""
    provider: DatabaseProvider
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    database: str = "course_ai"
    timeout: int = 30
    pool_size: int = 10
    extra_params: Optional[Dict[str, Any]] = None


class BaseDatabase(ABC):
    """Abstract base class for database services."""

    @function_logger("Handle __init__")
    @function_logger("Handle __init__")
    def __init__(self, config: DatabaseConfig):
        """Initialize database service."""
        self.config = config
        self.provider = config.provider.value
        self.connected = False

    @abstractmethod
    async def connect(self) -> None:
        """Establish database connection."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close database connection."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if database is healthy."""
        pass

    # ====== Course Operations ======

    @abstractmethod
    async def save_course(
        self,
        user_id: str,
        course_data: Dict[str, Any],
        session_id: str
    ) -> str:
        """
        Save course to database.
        
        Args:
            user_id: User identifier
            course_data: Course outline dict (from CourseOutlineSchema)
            session_id: Session identifier
            
        Returns:
            course_id (UUID or DB record ID)
        """
        pass

    @abstractmethod
    async def get_course(self, course_id: str) -> Optional[Dict[str, Any]]:
        """Get course by ID."""
        pass

    @abstractmethod
    async def list_user_courses(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List all courses for a user."""
        pass

    @abstractmethod
    async def update_course(
        self,
        course_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update course data."""
        pass

    @abstractmethod
    async def delete_course(self, course_id: str) -> bool:
        """Delete course."""
        pass

    # ====== Session Operations ======

    @abstractmethod
    async def save_session(
        self,
        session_id: str,
        user_id: str,
        session_data: Dict[str, Any]
    ) -> None:
        """Save session data."""
        pass

    @abstractmethod
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data."""
        pass

    @abstractmethod
    async def delete_session(self, session_id: str) -> None:
        """Delete session data."""
        pass

    # ====== User Operations ======

    @abstractmethod
    async def create_user(
        self,
        user_id: str,
        email: str,
        profile: Dict[str, Any]
    ) -> None:
        """Create user profile."""
        pass

    @abstractmethod
    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile."""
        pass

    @abstractmethod
    async def update_user(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update user profile."""
        pass

    # ====== Analytics Operations ======

    @abstractmethod
    async def log_activity(
        self,
        user_id: str,
        action: str,
        metadata: Dict[str, Any]
    ) -> None:
        """Log user activity."""
        pass

    @abstractmethod
    async def get_activity_logs(
        self,
        user_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get activity logs for user."""
        pass


class PostgreSQLDatabase(BaseDatabase):
    """PostgreSQL implementation."""

    @function_logger("Handle __init__")
    @function_logger("Handle __init__")
    def __init__(self, config: DatabaseConfig):
        """Initialize PostgreSQL service."""
        super().__init__(config)
        try:
            import asyncpg
            self.asyncpg = asyncpg
        except ImportError:
            raise ImportError("asyncpg required: pip install asyncpg")
        self.pool = None

    async def connect(self) -> None:
        """Connect to PostgreSQL."""
        if self.connected:
            return
        
        dsn = (
            f"postgresql://{self.config.username}:{self.config.password}@"
            f"{self.config.host}:{self.config.port}/{self.config.database}"
        )
        
        self.pool = await self.asyncpg.create_pool(
            dsn,
            min_size=1,
            max_size=self.config.pool_size,
            command_timeout=self.config.timeout
        )
        self.connected = True

    async def disconnect(self) -> None:
        """Close PostgreSQL connection."""
        if self.pool:
            await self.pool.close()
        self.connected = False

    async def health_check(self) -> bool:
        """Check PostgreSQL health."""
        try:
            if not self.connected:
                await self.connect()
            async with self.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except Exception as e:
            print(f"PostgreSQL health check failed: {e}")
            return False

    async def save_course(
        self,
        user_id: str,
        course_data: Dict[str, Any],
        session_id: str
    ) -> str:
        """Save course to PostgreSQL."""
        import json
        async with self.pool.acquire() as conn:
            course_id = await conn.fetchval(
                """
                INSERT INTO courses (user_id, session_id, course_data, created_at)
                VALUES ($1, $2, $3, $4)
                RETURNING id
                """,
                user_id,
                session_id,
                json.dumps(course_data),
                datetime.utcnow()
            )
        return str(course_id)

    async def get_course(self, course_id: str) -> Optional[Dict[str, Any]]:
        """Get course from PostgreSQL."""
        import json
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT course_data FROM courses WHERE id = $1",
                int(course_id)
            )
        return json.loads(row["course_data"]) if row else None

    async def list_user_courses(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List user courses from PostgreSQL."""
        import json
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, course_data, created_at FROM courses
                WHERE user_id = $1
                ORDER BY created_at DESC
                LIMIT $2 OFFSET $3
                """,
                user_id,
                limit,
                offset
            )
        return [
            {
                "id": str(row["id"]),
                **json.loads(row["course_data"]),
                "created_at": row["created_at"].isoformat()
            }
            for row in rows
        ]

    async def update_course(
        self,
        course_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update course in PostgreSQL."""
        import json
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE courses
                SET course_data = jsonb_set(course_data, '{}'::text[], $1)
                WHERE id = $2
                """,
                json.dumps(updates),
                int(course_id)
            )
        return result != "UPDATE 0"

    async def delete_course(self, course_id: str) -> bool:
        """Delete course from PostgreSQL."""
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM courses WHERE id = $1",
                int(course_id)
            )
        return result != "DELETE 0"

    async def save_session(
        self,
        session_id: str,
        user_id: str,
        session_data: Dict[str, Any]
    ) -> None:
        """Save session to PostgreSQL."""
        import json
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO sessions (session_id, user_id, session_data, created_at)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (session_id) DO UPDATE
                SET session_data = $3
                """,
                session_id,
                user_id,
                json.dumps(session_data),
                datetime.utcnow()
            )

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session from PostgreSQL."""
        import json
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT session_data FROM sessions WHERE session_id = $1",
                session_id
            )
        return json.loads(row["session_data"]) if row else None

    async def delete_session(self, session_id: str) -> None:
        """Delete session from PostgreSQL."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM sessions WHERE session_id = $1",
                session_id
            )

    async def create_user(
        self,
        user_id: str,
        email: str,
        profile: Dict[str, Any]
    ) -> None:
        """Create user in PostgreSQL."""
        import json
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO users (user_id, email, profile, created_at)
                VALUES ($1, $2, $3, $4)
                """,
                user_id,
                email,
                json.dumps(profile),
                datetime.utcnow()
            )

    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user from PostgreSQL."""
        import json
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT email, profile FROM users WHERE user_id = $1",
                user_id
            )
        return {
            "user_id": user_id,
            "email": row["email"],
            **(json.loads(row["profile"]) if row else {})
        } if row else None

    async def update_user(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update user in PostgreSQL."""
        import json
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE users
                SET profile = jsonb_set(profile, '{}'::text[], $1)
                WHERE user_id = $2
                """,
                json.dumps(updates),
                user_id
            )
        return result != "UPDATE 0"

    async def log_activity(
        self,
        user_id: str,
        action: str,
        metadata: Dict[str, Any]
    ) -> None:
        """Log activity in PostgreSQL."""
        import json
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO activity_logs (user_id, action, metadata, created_at)
                VALUES ($1, $2, $3, $4)
                """,
                user_id,
                action,
                json.dumps(metadata),
                datetime.utcnow()
            )

    async def get_activity_logs(
        self,
        user_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get activity logs from PostgreSQL."""
        import json
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT action, metadata, created_at FROM activity_logs
                WHERE user_id = $1
                ORDER BY created_at DESC
                LIMIT $2
                """,
                user_id,
                limit
            )
        return [
            {
                "action": row["action"],
                **(json.loads(row["metadata"]) if row["metadata"] else {}),
                "timestamp": row["created_at"].isoformat()
            }
            for row in rows
        ]


class MockDatabase(BaseDatabase):
    """In-memory mock database for testing."""

    @function_logger("Handle __init__")
    @function_logger("Handle __init__")
    def __init__(self, config: DatabaseConfig):
        """Initialize mock database."""
        super().__init__(config)
        self.courses = {}
        self.sessions = {}
        self.users = {}
        self.activities = []

    async def connect(self) -> None:
        """Mock connect."""
        self.connected = True

    async def disconnect(self) -> None:
        """Mock disconnect."""
        self.connected = False

    async def health_check(self) -> bool:
        """Mock health check."""
        return True

    async def save_course(
        self,
        user_id: str,
        course_data: Dict[str, Any],
        session_id: str
    ) -> str:
        """Mock save course."""
        import uuid
        course_id = str(uuid.uuid4())
        self.courses[course_id] = {
            "user_id": user_id,
            "session_id": session_id,
            **course_data
        }
        return course_id

    async def get_course(self, course_id: str) -> Optional[Dict[str, Any]]:
        """Mock get course."""
        return self.courses.get(course_id)

    async def list_user_courses(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Mock list courses."""
        courses = [
            {"id": cid, **data}
            for cid, data in self.courses.items()
            if data.get("user_id") == user_id
        ]
        return courses[offset:offset + limit]

    async def update_course(
        self,
        course_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Mock update course."""
        if course_id in self.courses:
            self.courses[course_id].update(updates)
            return True
        return False

    async def delete_course(self, course_id: str) -> bool:
        """Mock delete course."""
        if course_id in self.courses:
            del self.courses[course_id]
            return True
        return False

    async def save_session(
        self,
        session_id: str,
        user_id: str,
        session_data: Dict[str, Any]
    ) -> None:
        """Mock save session."""
        self.sessions[session_id] = {"user_id": user_id, **session_data}

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Mock get session."""
        return self.sessions.get(session_id)

    async def delete_session(self, session_id: str) -> None:
        """Mock delete session."""
        if session_id in self.sessions:
            del self.sessions[session_id]

    async def create_user(
        self,
        user_id: str,
        email: str,
        profile: Dict[str, Any]
    ) -> None:
        """Mock create user."""
        self.users[user_id] = {"email": email, **profile}

    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Mock get user."""
        if user_id in self.users:
            return {"user_id": user_id, **self.users[user_id]}
        return None

    async def update_user(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Mock update user."""
        if user_id in self.users:
            self.users[user_id].update(updates)
            return True
        return False

    async def log_activity(
        self,
        user_id: str,
        action: str,
        metadata: Dict[str, Any]
    ) -> None:
        """Mock log activity."""
        self.activities.append({
            "user_id": user_id,
            "action": action,
            **metadata,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def get_activity_logs(
        self,
        user_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Mock get activity logs."""
        logs = [log for log in self.activities if log.get("user_id") == user_id]
        return logs[-limit:]


class DatabaseFactory:
    """Factory for creating database service instances."""

    _providers = {
        DatabaseProvider.POSTGRESQL: PostgreSQLDatabase,
        DatabaseProvider.SQLITE: MockDatabase,  # Placeholder
    }

    @classmethod
    @function_logger("Create database")
    @function_logger("Create database")
    def create_database(cls, config: DatabaseConfig) -> BaseDatabase:
        """
        Create database service based on config.
        
        Args:
            config: DatabaseConfig with provider and connection details
            
        Returns:
            Appropriate BaseDatabase subclass instance
            
        Raises:
            ValueError: If provider not supported
        """
        service_class = cls._providers.get(config.provider, MockDatabase)
        return service_class(config)

    @classmethod
    @function_logger("Execute register provider")
    @function_logger("Execute register provider")
    def register_provider(
        cls,
        provider: DatabaseProvider,
        service_class: type
    ):
        """Register custom database provider."""
        cls._providers[provider] = service_class


# Global singleton instance (lazy-loaded)
_db_service: Optional[BaseDatabase] = None


@function_logger("Get db service")
@function_logger("Get db service")
def get_db_service() -> BaseDatabase:
    """Get or create global database service instance."""
    global _db_service
    
    if _db_service is None:
        # Load configuration from environment
        provider_str = os.getenv("DB_PROVIDER", "sqlite").lower()
        provider = DatabaseProvider(provider_str)
        
        config = DatabaseConfig(
            provider=provider,
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")) if os.getenv("DB_PORT") else None,
            username=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME", "course_ai"),
            timeout=int(os.getenv("DB_TIMEOUT", "30")),
            pool_size=int(os.getenv("DB_POOL_SIZE", "10"))
        )
        
        _db_service = DatabaseFactory.create_database(config)
    
    return _db_service


@function_logger("Set db service")
@function_logger("Set db service")
def set_db_service(service: BaseDatabase) -> None:
    """Override global database service instance (useful for testing)."""
    global _db_service
    _db_service = service


@function_logger("Execute reset db service")
@function_logger("Execute reset db service")
def reset_db_service() -> None:
    """Reset global database service (useful for testing)."""
    global _db_service
    _db_service = None
