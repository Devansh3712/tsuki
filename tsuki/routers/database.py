from typing import Any, Mapping

import psycopg
from psycopg import sql

from tsuki.config import secrets
from tsuki.routers.models import User


async def initdb():
    connection = await psycopg.AsyncConnection.connect(
        secrets.POSTGRES_URI, autocommit=True
    )
    async with connection:
        async with connection.cursor() as cursor:
            await cursor.execute(
                """CREATE TABLE IF NOT EXISTS users (
                    email       VARCHAR(320)    PRIMARY KEY,
                    username    VARCHAR(32)     UNIQUE NOT NULL,
                    password    VARCHAR(64)     NOT NULL,
                    verified    BOOL            NOT NULL,
                    created_at  TIMESTAMPTZ     NOT NULL
                )"""
            )
            await cursor.execute(
                """CREATE TABLE IF NOT EXISTS shorturl (
                    token       VARCHAR(320)    PRIMARY KEY,
                    id          CHAR(32)        UNIQUE NOT NULL
                )"""
            )


# TODO:
# Use Redis for storing shortened URLs for 48 hours.
async def create_short_url(token: Any, _id: str) -> bool:
    connection = await psycopg.AsyncConnection.connect(
        secrets.POSTGRES_URI, autocommit=True
    )
    try:
        async with connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "INSERT INTO shorturl VALUES (%s, %s)", (token, _id)
                )
                return True
    except:
        return False


async def read_short_url(_id: str) -> str | None:
    connection = await psycopg.AsyncConnection.connect(
        secrets.POSTGRES_URI, autocommit=True
    )
    try:
        async with connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT token FROM shorturl WHERE id = %s", (_id,))
                result = await cursor.fetchone()
                return result[0]
    except:
        return None


async def delete_short_url(_id: str):
    connection = await psycopg.AsyncConnection.connect(
        secrets.POSTGRES_URI, autocommit=True
    )
    async with connection:
        async with connection.cursor() as cursor:
            await cursor.execute("DELETE FROM shorturl WHERE id = %s", (_id,))


async def create_user(user: User) -> bool:
    connection = await psycopg.AsyncConnection.connect(
        secrets.POSTGRES_URI, autocommit=True
    )
    try:
        async with connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    """INSERT INTO users
                VALUES (%(email)s, %(username)s, %(password)s, %(verified)s, %(created_at)s)""",
                    user.dict(),
                )
                return True
    except:
        return False


async def read_user(username: str) -> User | None:
    connection = await psycopg.AsyncConnection.connect(
        secrets.POSTGRES_URI, autocommit=True
    )
    try:
        async with connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "SELECT * FROM users WHERE username = %s", (username,)
                )
                result = await cursor.fetchone()
                return User(
                    **{
                        key: result[index]
                        for index, key in enumerate(User.__fields__.keys())
                    }
                )
    except:
        return None


async def update_user(username: str, updates: Mapping[str, Any]) -> bool:
    connection = await psycopg.AsyncConnection.connect(
        secrets.POSTGRES_URI, autocommit=True
    )
    try:
        async with connection:
            async with connection.cursor() as cursor:
                for column in updates:
                    await cursor.execute(
                        sql.SQL("UPDATE users SET {} = {} WHERE username = {}").format(
                            sql.Identifier(column),
                            updates[column],
                            username,
                        )
                    )
                return True
    except:
        return False


async def delete_user(username: str) -> bool:
    connection = await psycopg.AsyncConnection.connect(
        secrets.POSTGRES_URI, autocommit=True
    )
    try:
        async with connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "DELETE FROM users WHERE username = %s", (username,)
                )
                return True
    except:
        return False
