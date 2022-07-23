import os
from typing import List

import pandas
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from tsuki.database import *
from tsuki.models import PostResponse, User
from tsuki.oauth import get_current_user

explore = APIRouter(prefix="/explore")
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(parent_dir, "templates"))
limit = 10


@explore.get("/", response_class=HTMLResponse)
async def get_explore_feed(
    request: Request, user: User = Depends(get_current_user), more: bool = False
):
    global limit
    if not user:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "401 Unauthorized",
                "message": "User not logged in.",
            },
        )
    if more:
        limit += 5
    else:
        limit = 10
    posts = await recommend_posts(user.username, limit)
    return templates.TemplateResponse(
        "explore.html", {"request": request, "posts": posts}
    )


async def recommend_posts(username: str, limit: int) -> List[PostResponse]:
    """Get recommended posts for the current user based on their
    likes. (Experimental)

    Args:
        username (str): User to fetch posts for.
        limit (int): Limit of posts to fetch.

    Returns:
        List[PostResponse]: List of posts.
    """
    # Get recent 100 liked posts of user
    liked_posts = await read_liked_posts(username)
    if not liked_posts:
        return []
    # Get recent 1000 posts made
    all_recent_posts = await read_explore_posts(username)
    if not all_recent_posts:
        return []
    user_df = pandas.DataFrame(liked_posts, columns=["id", "body"])
    post_df = pandas.DataFrame(all_recent_posts, columns=["id", "body"])
    # Transform the body column in the vector form to
    # compute similarity
    tf = TfidfVectorizer(
        analyzer="word", ngram_range=(1, 3), min_df=0, stop_words="english"
    )
    matrix = tf.fit_transform(post_df["body"].values.astype("U"))
    # Compute cosine similarity to check what all posts are
    # of similar content on the basis of the body column
    cosine_similarities = linear_kernel(matrix, matrix)
    _id = post_df["id"]

    indices = pandas.Series(user_df.index, index=user_df["id"])
    posts = []
    # Get recommended posts for each liked post
    for data in liked_posts:
        try:
            index = indices[data[0]]
            sim_scores = list(enumerate(cosine_similarities[index]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            sim_scores = sim_scores[1:31]
            _indices = [i[0] for i in sim_scores]
            recommended_ids = _id.iloc[_indices].head(limit)
            for post_id in recommended_ids:
                post = await read_post(post_id)
                if post not in posts:
                    posts.append(post)
        except:
            ...
    return posts
