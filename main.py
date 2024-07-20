from fastapi import FastAPI
from sqlalchemy import select
from sqlalchemy.orm import Session

import models
import schemas


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


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
