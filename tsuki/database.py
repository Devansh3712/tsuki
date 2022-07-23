import os
from typing import Any, List, Mapping, Tuple

import psycopg
from psycopg import sql

from tsuki.config import secrets
from tsuki.models import Comment, Post, PostResponse, User


async def initdb():
    connection = await psycopg.AsyncConnection.connect(
        secrets.POSTGRES_URI, autocommit=True
    )
    async with connection:
        async with connection.cursor() as cursor:
            current_dir = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(current_dir, "resources", "init.sql")) as sql_file:
                await cursor.execute(sql_file.read())


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


async def read_users(username: str, limit: int = 10) -> List[User]:
    connection = await psycopg.AsyncConnection.connect(
        secrets.POSTGRES_URI, autocommit=True
    )
    try:
        async with connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    """SELECT * FROM t_users WHERE username LIKE %s
                    ORDER BY username
                    LIMIT %s""",
                    ("%" + username + "%", limit),
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


async def read_avatar(username: str) -> str | None:
    connection = await psycopg.AsyncConnection.connect(
        secrets.POSTGRES_URI, autocommit=True
    )
    try:
        async with connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "SELECT url FROM avatars WHERE username = %s", (username,)
                )
                url = await cursor.fetchone()
                return url[0]
    except:
        return None


async def update_avatar(username: str, url: str) -> bool:
    connection = await psycopg.AsyncConnection.connect(
        secrets.POSTGRES_URI, autocommit=True
    )
    try:
        async with connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    """INSERT INTO avatars (username, url)
                    VALUES (%s, %s)
                    ON CONFLICT (username) DO UPDATE
                    SET url = EXCLUDED.url""",
                    (username, url),
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


async def read_post_count(username: str) -> int:
    connection = await psycopg.AsyncConnection.connect(
        secrets.POSTGRES_URI, autocommit=True
    )
    try:
        async with connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "SELECT COUNT(*) FROM posts WHERE username = %s", (username,)
                )
                result = await cursor.fetchone()
                return result[0]
    except:
        return 0


async def read_recent_posts(username: str, limit: int = 5) -> List[PostResponse]:
    connection = await psycopg.AsyncConnection.connect(
        secrets.POSTGRES_URI, autocommit=True
    )
    try:
        async with connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    """SELECT * FROM posts WHERE username = %s
                ORDER BY created_at DESC
                LIMIT %s""",
                    (username, limit),
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


async def read_feed_posts(username: str, limit: int = 10) -> List[PostResponse]:
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
                LIMIT %s""",
                    (username, limit),
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


async def read_explore_posts(username: str) -> List[Tuple[str, ...]]:
    connection = await psycopg.AsyncConnection.connect(
        secrets.POSTGRES_URI, autocommit=True
    )
    try:
        async with connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    """SELECT id, body FROM posts
                    WHERE username != %s
                    ORDER BY created_at desc
                    LIMIT 1000""",
                    (username,),
                )
                posts = await cursor.fetchall()
                return list(posts)
    except:
        []


async def read_liked_posts(username: str) -> List[Tuple[str, ...]]:
    connection = await psycopg.AsyncConnection.connect(
        secrets.POSTGRES_URI, autocommit=True
    )
    try:
        async with connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    """SELECT id, body FROM posts WHERE id IN
                    (SELECT id FROM votes WHERE username = %s)
                    LIMIT 100""",
                    (username,),
                )
                posts = await cursor.fetchall()
                return list(posts)
    except:
        []


async def delete_post(_id: str) -> bool:
    connection = await psycopg.AsyncConnection.connect(
        secrets.POSTGRES_URI, autocommit=True
    )
    try:
        async with connection:
            async with connection.cursor() as cursor:
                await cursor.execute("DELETE FROM posts WHERE id = %s", (_id,))
                return True
    except:
        return False


async def toggle_follow(username: str, to_toggle: str):
    connection = await psycopg.AsyncConnection.connect(
        secrets.POSTGRES_URI, autocommit=True
    )
    async with connection:
        async with connection.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM follows WHERE username = %s AND following = %s",
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
                "SELECT * FROM follows WHERE username = %s AND following = %s",
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
                "SELECT username FROM follows WHERE following = %s",
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
                "SELECT following FROM follows WHERE username = %s",
                (username,),
            )
            following = await cursor.fetchall()
            return list(following)


async def toggle_vote(username: str, _id: str):
    connection = await psycopg.AsyncConnection.connect(
        secrets.POSTGRES_URI, autocommit=True
    )
    async with connection:
        async with connection.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM votes WHERE username = %s AND id = %s",
                (username, _id),
            )
            voted = await cursor.fetchone()
            if not voted:
                await cursor.execute(
                    "INSERT INTO votes VALUES (%s, %s)", (_id, username)
                )
                return
            await cursor.execute(
                "DELETE FROM votes WHERE username = %s AND id = %s",
                (username, _id),
            )


async def voted(username: str, _id: str) -> bool:
    connection = await psycopg.AsyncConnection.connect(
        secrets.POSTGRES_URI, autocommit=True
    )
    async with connection:
        async with connection.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM votes WHERE username = %s AND id = %s",
                (username, _id),
            )
            voted = await cursor.fetchone()
            if not voted:
                return False
            return True


async def read_votes(_id: str) -> List[str]:
    connection = await psycopg.AsyncConnection.connect(
        secrets.POSTGRES_URI, autocommit=True
    )
    try:
        async with connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "SELECT username FROM votes WHERE id = %s",
                    (_id,),
                )
                votes = await cursor.fetchall()
                return list(votes)
    except:
        []


async def create_comment(comment: Comment) -> bool:
    connection = await psycopg.AsyncConnection.connect(
        secrets.POSTGRES_URI, autocommit=True
    )
    try:
        async with connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    """INSERT INTO comments
                VALUES (%(post_id)s, %(id)s, %(username)s, %(body)s, %(created_at)s)""",
                    comment.dict(),
                )
                return True
    except:
        return False


async def read_comments(_id: str, limit: int = 10) -> List[Comment]:
    connection = await psycopg.AsyncConnection.connect(
        secrets.POSTGRES_URI, autocommit=True
    )
    try:
        async with connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    """SELECT * FROM comments WHERE post_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s""",
                    (_id, limit),
                )
                results = await cursor.fetchall()
                comments = []
                for data in results:
                    comment = Comment(
                        **{
                            key: data[index]
                            for index, key in enumerate(Comment.__fields__.keys())
                        }
                    )
                    comment.created_at = comment.created_at.strftime(
                        "%d %B %Y, %H:%M:%S"
                    )
                    comments.append(comment)
                return comments
    except:
        []


async def delete_comment(_id: str) -> bool:
    connection = await psycopg.AsyncConnection.connect(
        secrets.POSTGRES_URI, autocommit=True
    )
    try:
        async with connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "DELETE FROM comments WHERE comment_id = %s", (_id,)
                )
                return True
    except:
        return False
