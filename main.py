from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Annotated
from datetime import datetime, timedelta, timezone

import jwt
import models
import schemas
import os


app = FastAPI()
SECRETY_KEY = "JUSEKEY"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/users")
def create_user(user: schemas.UserCreate) -> dict:
    db = models.Session()

    new_user = models.User(username=user.username, password=user.password)

    db.add(new_user)
    db.commit()

    return {"message": "success"}


@app.post("/token")
def create_token(
    form_data: schemas.UserCreate,
) -> dict:
    db = models.Session()

    stmt = select(models.User).filter_by(
        username=form_data.username, password=form_data.password
    )

    user = db.execute(stmt).scalar()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=30)

    token = jwt.encode(
        {"sub": user.id, "exp": datetime.now(timezone.utc) + access_token_expires},
        SECRETY_KEY,
    )

    return {"access_token": token, "token_type": "bearer"}


def verify_token(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRETY_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    db = models.Session()
    stmt = select(models.User).filter_by(id=payload["sub"])
    user = db.execute(stmt).scalar()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user


@app.get("/users/me")
def read_user(user: Annotated[models.User, Depends(verify_token)]) -> dict:
    return {"username": user.username}


@app.get("/artists")
def get_artists() -> list[schemas.Artist]:
    db = models.Session()

    stmt = select(models.Artist)

    return db.execute(stmt).scalars().all()


@app.get("/artists/{artist_id}")
def get_artist(artist_id: int) -> schemas.Artist:
    db: Session = models.Session()

    stmt = select(models.Artist).filter_by(id=artist_id)

    return db.execute(stmt).scalar()


@app.post("/artists")
def create_artist(artist: schemas.ArtistCreate) -> dict:
    db = models.Session()

    new_artist = models.Artist(name=artist.name)

    db.add(new_artist)
    db.commit()

    return {"message": "success"}


@app.put("/artists/{artist_id}")
def update_artist(artist_id: int, artist: schemas.ArtistModify) -> dict:
    db = models.Session()

    stmt = select(models.Artist).filter_by(id=artist_id)
    artist_db = db.execute(stmt).scalar()

    artist_db.name = artist.name

    db.commit()

    return {"message": "success"}


@app.delete("/artists/{artist_id}")
def delete_artist(airtist_id: int) -> dict:
    db = models.Session()

    stmt = select(models.Artist).filter_by(id=airtist_id)
    artist = db.execute(stmt).scalar()

    db.delete(artist)
    db.commit()

    return {"message": "success"}


@app.post("/albums")
def create_album(album: schemas.AlbumCreate) -> dict:
    db = models.Session()

    new_album = models.Album(title=album.title, artist_id=album.artist_id)

    db.add(new_album)
    db.commit()

    return schemas.Album.model_validate(new_album)
