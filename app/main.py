from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy import Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
from . import auth, models, schemas
from app.auto_reply import generate_reply
from app.database import engine, SessionLocal
from app.auth import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_password_hash
from app.ai_moderation import contains_profanity
import asyncio

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/posts/", response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db),
                current_user: models.User = Depends(auth.get_current_user)):
    is_blocked = contains_profanity(post.title) or contains_profanity(post.content)

    db_post = models.Post(**post.dict(), owner_id=current_user.id, is_blocked=is_blocked)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    if is_blocked:
        raise HTTPException(status_code=400, detail="Post contains inappropriate content.")

    return db_post


@app.get("/posts/", response_model=List[schemas.Post])
def read_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    posts = db.query(models.Post).offset(skip).limit(limit).all()
    return posts


@app.post("/comments/", response_model=schemas.Comment)
def create_comment(comment: schemas.CommentCreate, post_id: int, db: Session = Depends(get_db),
                   # background_tasks: BackgroundTasks,
                   current_user: models.User = Depends(auth.get_current_user)):
    is_blocked = contains_profanity(comment.content)

    db_comment = models.Comment(
        **comment.dict(),
        author_id=current_user.id,
        post_id=post_id,
        is_blocked=is_blocked
    )

    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)

    if is_blocked:
        raise HTTPException(status_code=400, detail="Comment contains inappropriate content.")

    # post = db.query(models.Post).filter(models.Post.id == post_id).first()
    # if post.owner.auto_reply_enabled:
    #     delay_seconds = post.owner.auto_reply_delay.total_seconds()
    #     background_tasks.add_task(schedule_auto_reply, delay_seconds, db_comment.id, db)

    return db_comment


@app.get("/comments/", response_model=List[schemas.Comment])
def read_comments(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    comments = db.query(models.Comment).offset(skip).limit(limit).all()
    return comments


@app.get("/api/comments-daily-breakdown", response_model=List[schemas.CommentDailyBreakdown])
def get_comments_daily_breakdown(date_from: str, date_to: str, db: Session = Depends(get_db)):
    try:
        start_date = datetime.strptime(date_from, "%Y-%m-%d")
        end_date = datetime.strptime(date_to, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date must be before end date.")

    results = (
        db.query(
            func.date(models.Comment.created_at).label("date"),
            func.count().label("total_comments"),
            func.sum(func.cast(models.Comment.is_blocked, Integer)).label("blocked_comments")
        )
        .filter(models.Comment.created_at >= start_date, models.Comment.created_at <= end_date)
        .group_by(func.date(models.Comment.created_at))
        .all()
    )
    daily_breakdown = [
        schemas.CommentDailyBreakdown(
            date=row.date,
            total_comments=row.total_comments,
            blocked_comments=row.blocked_comments
        )
        for row in results
    ]

    return daily_breakdown


def schedule_auto_reply(delay_seconds: float, comment_id: int, db: Session):
    asyncio.sleep(delay_seconds)

    db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not db_comment:
        return

    post = db.query(models.Post).filter(models.Post.id == db_comment.post_id).first()
    if not post:
        return

    reply_content = generate_reply(post.content, db_comment.content)
    reply = models.Comment(content=reply_content, post_id=post.id, author_id=post.owner_id)
    db.add(reply)
    db.commit()
    db.refresh(reply)
