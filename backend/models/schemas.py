from pydantic import BaseModel
from typing import Optional


class Recipe(BaseModel):
    """Schema for a recipe stored in Supabase."""
    id: Optional[int] = None
    name: str
    description: str = ""
    category: str = "other"
    prep_time: str = ""
    cook_time: str = ""
    servings: int = 1
    ingredients: list[str] = []
    instructions: list[str] = []
    image_url: Optional[str] = None
    source: str = "manual"
    external_id: str = ""
    allergens: list[str] = []
    diet_labels: list[str] = []


class RecipeCreate(BaseModel):
    """Schema for creating a recipe in Supabase (no id)."""
    name: str
    description: str = ""
    category: str = "other"
    prep_time: str = ""
    cook_time: str = ""
    servings: int = 1
    ingredients: list[str] = []
    instructions: list[str] = []
    image_url: Optional[str] = None
    source: str = "manual"
    external_id: str = ""
    allergens: list[str] = []
    diet_labels: list[str] = []


class Category(BaseModel):
    """Schema for a recipe category."""
    name: str
    description: str = ""
    recipe_count: int = 0


class UserProfile(BaseModel):
    """Schema for user profile with dietary info."""
    uid: str
    email: Optional[str] = None
    name: Optional[str] = None
    picture: Optional[str] = None
    dietary_preferences: list[str] = []
    allergies: list[str] = []
    fcm_token: Optional[str] = None


class UserProfileUpdate(BaseModel):
    """Schema for updating user profile."""
    name: Optional[str] = None
    picture: Optional[str] = None


class DietaryPreferencesUpdate(BaseModel):
    """Schema for setting dietary preferences."""
    preferences: list[str] = []


class AllergyAction(BaseModel):
    """Schema for adding an allergy."""
    allergen: str


class FavoriteAction(BaseModel):
    """Schema for adding/removing a favorite."""
    recipe_id: int


class SearchRequest(BaseModel):
    """Schema for advanced recipe search."""
    query: str = ""
    ingredients: list[str] = []
    category: Optional[str] = None
    diet_filter: list[str] = []
    exclude_allergens: list[str] = []


class FCMTokenUpdate(BaseModel):
    """Schema for updating FCM token."""
    token: str


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
