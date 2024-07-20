from pydantic import BaseModel
from datetime import datetime


class ArtistBase(BaseModel):
    name: str


class ArtistCreate(ArtistBase):
    pass


class Artist(ArtistBase):
    id: int
    created_at: datetime
    updated_at: datetime

    albums: list["Album"]

    class Config:
        from_attributes = True


class AlbumBase(BaseModel):
    title: str
    artist_id: int


class AlbumCreate(AlbumBase):
    pass


class Album(AlbumBase):
    id: int
    created_at: datetime
    updated_at: datetime

    artist: Artist

    class Config:
        from_attributes = True
