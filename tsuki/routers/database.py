from typing import Any, List, Mapping

import psycopg
from psycopg import sql

from tsuki.config import secrets
from tsuki.routers.models import Post, PostResponse, User


async def initdb():
    connection = await psycopg.AsyncConnection.connect(
        secrets.POSTGRES_URI, autocommit=True
    )
    async with connection:
        async with connection.cursor() as cursor:
            await cursor.execute(
                """CREATE TABLE IF NOT EXISTS t_users (
                    email       VARCHAR(320)    UNIQUE NOT NULL,
                    username    VARCHAR(32)     PRIMARY KEY,
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
            await cursor.execute(
                """CREATE TABLE IF NOT EXISTS posts (
                    username    VARCHAR(32)     NOT NULL,
                    id          CHAR(32)        PRIMARY KEY,
                    body        VARCHAR(320)    NOT NULL,
                    created_at  TIMESTAMPTZ     NOT NULL,
                    CONSTRAINT fk_username
                        FOREIGN KEY(username)
                            REFERENCES t_users(username)
                            ON DELETE CASCADE
                )"""
            )
            await cursor.execute(
                """CREATE TABLE IF NOT EXISTS follows (
                    username    VARCHAR(32)     NOT NULL,
                    following   VARCHAR(32)     NOT NULL,
                    CONSTRAINT fk_username
                        FOREIGN KEY(username)
                            REFERENCES t_users(username)
                            ON DELETE CASCADE
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
                    """INSERT INTO t_users
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
                    "SELECT * FROM t_users WHERE username = %s", (username,)
                )
                result = await cursor.fetchone()
                user = User(
                    **{
                        key: result[index]
                        for index, key in enumerate(User.__fields__.keys())
                    }
                )
                user.created_at = user.created_at.strftime("%d %B %Y, %H:%M:%S")
                return user
    except:
        return None


async def read_users(username: str) -> List[User]:
    connection = await psycopg.AsyncConnection.connect(
        secrets.POSTGRES_URI, autocommit=True
    )
    try:
        async with connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    """SELECT * FROM t_users WHERE username LIKE %s
                    ORDER BY username
                    LIMIT 10""",
                    (f"%{username}%",),
                )
                results = await cursor.fetchall()
                users = []
                for data in results:
                    user = User(
                        **{
                            key: data[index]
                            for index, key in enumerate(User.__fields__.keys())
                        }
                    )
                    user.created_at = user.created_at.strftime("%d %B %Y, %H:%M:%S")
                    users.append(user)
                return users
    except:
        return []


async def update_user(username: str, updates: Mapping[str, Any]) -> bool:
    connection = await psycopg.AsyncConnection.connect(
        secrets.POSTGRES_URI, autocommit=True
    )
    try:
        async with connection:
            async with connection.cursor() as cursor:
                for column in updates:
                    await cursor.execute(
                        sql.SQL(
                            "UPDATE t_users SET {} = {} WHERE username = {}"
                        ).format(
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
                    "DELETE FROM t_users WHERE username = %s", (username,)
                )
                return True
    except:
        return False


async def create_post(username: str, post: Post) -> bool:
    connection = await psycopg.AsyncConnection.connect(
        secrets.POSTGRES_URI, autocommit=True
    )
    try:
        async with connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "INSERT INTO posts VALUES (%s, %s, %s, %s)",
                    (username, post.id, post.body, post.created_at),
                )
                return True
    except:
        return False


async def read_post(_id: str) -> PostResponse | None:
    connection = await psycopg.AsyncConnection.connect(
        secrets.POSTGRES_URI, autocommit=True
    )
    try:
        async with connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT * FROM posts WHERE id = %s", (_id,))
                result = await cursor.fetchone()
                post = PostResponse(
                    **{
                        key: result[index]
                        for index, key in enumerate(PostResponse.__fields__.keys())
                    }
                )
                post.created_at = post.created_at.strftime("%d %B %Y, %H:%M:%S")
                return post
    except:
        return None


async def read_recent_posts(username: str) -> List[PostResponse]:
    connection = await psycopg.AsyncConnection.connect(
        secrets.POSTGRES_URI, autocommit=True
    )
    try:
        async with connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    """SELECT * FROM posts WHERE username = %s
                ORDER BY created_at DESC
                LIMIT 5""",
                    (username,),
                )
                results = await cursor.fetchall()
                posts = []
                for data in results:
                    post = PostResponse(
                        **{
                            key: data[index]
                            for index, key in enumerate(PostResponse.__fields__.keys())
                        }
                    )
                    post.created_at = post.created_at.strftime("%d %B %Y, %H:%M:%S")
                    posts.append(post)
                return posts
    except:
        return []


async def read_feed_posts(username: str) -> List[PostResponse]:
    connection = await psycopg.AsyncConnection.connect(
        secrets.POSTGRES_URI, autocommit=True
    )
    try:
        async with connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    """SELECT * FROM posts WHERE username IN
                (SELECT following FROM follows WHERE username = %s)
                ORDER BY created_at DESC
                LIMIT 10""",
                    (username,),
                )
                results = await cursor.fetchall()
                posts = []
                for data in results:
                    post = PostResponse(
                        **{
                            key: data[index]
                            for index, key in enumerate(PostResponse.__fields__.keys())
                        }
                    )
                    post.created_at = post.created_at.strftime("%d %B %Y, %H:%M:%S")
                    posts.append(post)
                return posts
    except:
        return []


async def toggle_follow(username: str, to_toggle: str):
    connection = await psycopg.AsyncConnection.connect(
        secrets.POSTGRES_URI, autocommit=True
    )
    async with connection:
        async with connection.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM follows where username = %s AND following = %s",
                (username, to_toggle),
            )
            following = await cursor.fetchone()
            if not following:
                await cursor.execute(
                    "INSERT INTO follows VALUES (%s, %s)", (username, to_toggle)
                )
                return
            await cursor.execute(
                "DELETE FROM follows WHERE username = %s AND following = %s",
                (username, to_toggle),
            )


async def follows(username: str, following: str) -> bool | None:
    if username == following:
        return None
    connection = await psycopg.AsyncConnection.connect(
        secrets.POSTGRES_URI, autocommit=True
    )
    async with connection:
        async with connection.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM follows where username = %s AND following = %s",
                (username, following),
            )
            following = await cursor.fetchone()
            if not following:
                return False
            return True


async def read_followers(username: str) -> List[str]:
    connection = await psycopg.AsyncConnection.connect(
        secrets.POSTGRES_URI, autocommit=True
    )
    async with connection:
        async with connection.cursor() as cursor:
            await cursor.execute(
                "SELECT username FROM follows where following = %s",
                (username,),
            )
            followers = await cursor.fetchall()
            return list(followers)


async def read_following(username: str) -> List[str]:
    connection = await psycopg.AsyncConnection.connect(
        secrets.POSTGRES_URI, autocommit=True
    )
    async with connection:
        async with connection.cursor() as cursor:
            await cursor.execute(
                "SELECT following FROM follows where username = %s",
                (username,),
            )
            following = await cursor.fetchall()
            return list(following)
