from pydantic import BaseModel
from typing import Optional


class Recipe(BaseModel):
    """Schema for a recipe."""
    id: int
    name: str
    description: str
    category: str
    prep_time: str
    cook_time: str
    servings: int
    ingredients: list[str]
    instructions: list[str]
    image_url: Optional[str] = None


class Category(BaseModel):
    """Schema for a recipe category."""
    name: str
    description: str
    recipe_count: int


class UserProfile(BaseModel):
    """Schema for user profile info returned from Firebase token."""
    uid: str
    email: Optional[str] = None
    name: Optional[str] = None
    picture: Optional[str] = None


class FavoriteAction(BaseModel):
    """Schema for adding/removing a favorite."""
    recipe_id: int


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
