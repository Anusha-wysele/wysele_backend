from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

# Common properties
class BlogBase(BaseModel):
    title: str
    content: str
    category: str
    image_url: Optional[str] = None
    image_urls: Optional[List[str]] = []
    read_time: Optional[str] = "5 MIN READ"
    status: Optional[str] = "ACTIVE"

# Properties to receive on blog creation
class BlogCreate(BlogBase):
    pass

# Properties to receive on blog update
class BlogUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    image_urls: Optional[List[str]] = None
    read_time: Optional[str] = None
    status: Optional[str] = None

# Properties to return to the client
class BlogResponse(BlogBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


class BlogCreateSuccess(BaseModel):
    message: str = "Blog posted successfully"
    blog: BlogResponse