"""
routes/blog.py — Blog / articles.

Two routes:
  /blog/        → list all articles
  /blog/<slug>  → read a single article
"""

from flask import Blueprint, render_template, abort
from models import BlogPost

blog_bp = Blueprint("blog", __name__)


@blog_bp.route("/")
def index():
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template("blog/index.html", posts=posts)


@blog_bp.route("/<slug>")
def article(slug: str):
    # get_or_404 returns the post if found, or automatically returns a 404 page
    post = BlogPost.query.filter_by(slug=slug).first_or_404()

    # Related posts: same tag, excluding this one, limit 2
    related = (
        BlogPost.query
        .filter(BlogPost.tag == post.tag, BlogPost.id != post.id)
        .limit(2)
        .all()
    )
    return render_template("blog/article.html", post=post, related=related)
