from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

# Enums
class Provider(str, Enum):
    TWITTER = "TWITTER"
    REDDIT = "REDDIT"
    GOOGLE = "GOOGLE"

class PlanType(str, Enum):
    FREE = "FREE"
    SOLO = "SOLO"
    TEAM = "TEAM"
    ENTERPRISE = "ENTERPRISE"

class MemeStatus(str, Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"

class Platform(str, Enum):
    TWITTER = "TWITTER"
    REDDIT = "REDDIT"
    INSTAGRAM = "INSTAGRAM"

class TeamRole(str, Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    EDITOR = "EDITOR"
    VIEWER = "VIEWER"

class NotificationType(str, Enum):
    TREND = "TREND"
    TEAM = "TEAM"
    SUBMISSION = "SUBMISSION"
    VIRAL_PREDICTION = "VIRAL_PREDICTION"

# Base Models
class BaseDBModel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# User Models
class User(BaseDBModel):
    email: EmailStr
    username: str
    avatar: Optional[str] = None
    plan_type: PlanType = PlanType.FREE
    storage_used: int = 0
    password_hash: Optional[str] = None

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    avatar: Optional[str]
    plan_type: PlanType
    storage_used: int
    created_at: datetime

# Social Auth Models
class SocialAuth(BaseDBModel):
    user_id: str
    provider: Provider
    provider_user_id: str
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None

# Meme Models
class Meme(BaseDBModel):
    user_id: str
    team_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    canvas_data: Dict[str, Any]
    thumbnail_url: str
    status: MemeStatus = MemeStatus.DRAFT
    tags: List[str] = []

class MemeCreate(BaseModel):
    title: str
    description: Optional[str] = None
    canvas_data: Dict[str, Any]
    thumbnail_url: str
    tags: List[str] = []

class MemeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    canvas_data: Optional[Dict[str, Any]] = None
    thumbnail_url: Optional[str] = None
    status: Optional[MemeStatus] = None
    tags: Optional[List[str]] = None

class MemeResponse(BaseModel):
    id: str
    user_id: str
    team_id: Optional[str]
    title: str
    description: Optional[str]
    canvas_data: Dict[str, Any]
    thumbnail_url: str
    status: MemeStatus
    tags: List[str]
    created_at: datetime
    updated_at: datetime

# Template Models
class Template(BaseDBModel):
    title: str
    category: str
    tags: List[str]
    image_url: str
    canvas_data: Dict[str, Any]
    creator_id: Optional[str] = None
    is_community: bool = False
    votes: int = 0
    is_approved: bool = False

class TemplateCreate(BaseModel):
    title: str
    category: str
    tags: List[str]
    image_url: str
    canvas_data: Dict[str, Any]
    is_community: bool = False

class TemplateResponse(BaseModel):
    id: str
    title: str
    category: str
    tags: List[str]
    image_url: str
    canvas_data: Dict[str, Any]
    creator_id: Optional[str]
    is_community: bool
    votes: int
    is_approved: bool
    created_at: datetime

# Trend Models
class Trend(BaseDBModel):
    platform: Platform
    title: str
    description: Optional[str]
    image_url: Optional[str]
    viral_score: int
    engagement_data: Dict[str, Any]
    discovered_at: datetime = Field(default_factory=datetime.utcnow)

class TrendResponse(BaseModel):
    id: str
    platform: Platform
    title: str
    description: Optional[str]
    image_url: Optional[str]
    viral_score: int
    engagement_data: Dict[str, Any]
    discovered_at: datetime

# Team Models
class Team(BaseDBModel):
    name: str
    owner_id: str
    plan_type: PlanType
    storage_limit: int

class TeamCreate(BaseModel):
    name: str

class TeamMember(BaseDBModel):
    team_id: str
    user_id: str
    role: TeamRole
    invited_at: datetime = Field(default_factory=datetime.utcnow)
    joined_at: Optional[datetime] = None


class TeamResponse(BaseModel):
    id: str
    name: str
    owner_id: str
    plan_type: PlanType
    storage_limit: int
    member_count: int = 0
    created_at: datetime

class TeamMemberResponse(BaseModel):
    id: str
    team_id: str
    user_id: str
    role: TeamRole
    invited_at: datetime
    joined_at: Optional[datetime] = None
    username: Optional[str] = None
    email: Optional[str] = None



class AnalyticsCreate(BaseModel):
    meme_id: str
    platform: Platform
    url: str
    engagement_data: Dict[str, Any] = {}

class UserAnalyticsSummary(BaseModel):
    total_memes: int
    total_views: int
    total_likes: int
    total_shares: int
    storage_used: int
    daily_stats: Dict[str, Dict[str, int]]

class TeamAnalyticsSummary(BaseModel):
    total_memes: int
    total_members: int
    total_views: int
    total_likes: int


class SocialMediaPost(BaseModel):
    meme_id: str
    platform: Platform
    caption: str
    title: Optional[str] = None  # For Reddit
    subreddit: Optional[str] = "memes"  # For Reddit

class MultiPlatformPost(BaseModel):
    meme_id: str
    platforms: List[Platform]
    caption: str
    title: Optional[str] = None
    subreddit: Optional[str] = "memes"

    total_shares: int
    top_memes: List[Dict[str, Any]]

class TeamInvite(BaseModel):
    email: str
    role: TeamRole = TeamRole.EDITOR

# Analytics Models
class Analytics(BaseDBModel):
    meme_id: str
    user_id: str
    platform: Platform
    url: str
    engagement_data: Dict[str, Any]
    tracked_at: datetime = Field(default_factory=datetime.utcnow)

# Notification Models
class Notification(BaseDBModel):
    user_id: str
    type: NotificationType
    title: str
    message: str
    link: Optional[str] = None
    image_url: Optional[str] = None
    is_read: bool = False

class NotificationResponse(BaseModel):
    id: str
    type: NotificationType
    title: str
    message: str
    link: Optional[str]
    image_url: Optional[str]
    is_read: bool
    created_at: datetime

# Comment Models
class Comment(BaseDBModel):
    meme_id: str
    user_id: str
    content: str
    position: Optional[Dict[str, Any]] = None
    is_resolved: bool = False

class CommentCreate(BaseModel):
    content: str
    position: Optional[Dict[str, Any]] = None

class CommentResponse(BaseModel):
    id: str
    meme_id: str
    user_id: str
    content: str
    position: Optional[Dict[str, Any]]
    is_resolved: bool
    created_at: datetime

# AI Models
class ImageGenerateRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = None
    width: int = 1024
    height: int = 1024

class CaptionSuggestRequest(BaseModel):
    image_url: str
    context: Optional[str] = None

class BackgroundRemoveRequest(BaseModel):
    image_url: str


class FaceSwapRequest(BaseModel):
    source_image_url: str
    target_image_url: str

class ViralPredictRequest(BaseModel):
    meme_id: str

# Token Models
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
