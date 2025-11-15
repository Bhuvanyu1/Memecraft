from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import logging
from pathlib import Path

# Local imports
from config import settings
from models import (
    UserCreate, UserLogin, UserResponse, Token,
    MemeCreate, MemeUpdate, MemeResponse,
    TemplateCreate, TemplateResponse,
    TrendResponse,
    NotificationResponse,
    CommentCreate, CommentResponse,
    ImageGenerateRequest, CaptionSuggestRequest, ViralPredictRequest,
    BackgroundRemoveRequest, FaceSwapRequest,
    TeamCreate, TeamResponse, TeamMemberResponse, TeamInvite, TeamRole,
    AnalyticsCreate, UserAnalyticsSummary, TeamAnalyticsSummary,
    Provider, Platform, PlanType
)
from auth import get_password_hash, authenticate_user, create_access_token, get_current_user
from database import (
    create_user, get_user_by_email, get_user_by_username, get_user_by_id,
    create_meme, get_meme_by_id, get_user_memes, update_meme, delete_meme,
    create_template, get_template_by_id, get_templates, update_template_votes,
    get_trends, create_trend,
    get_user_notifications, mark_notification_read, create_notification,
    create_comment, get_meme_comments, resolve_comment, delete_comment,
    create_team, get_team_by_id, get_user_teams, update_team, delete_team,
    add_team_member, get_team_members, get_team_member, update_team_member_role,
    remove_team_member, accept_team_invite,
    close_db_connection
)
from ai_services import ai_service
from trends_service import trends_service
from storage import storage_service
from oauth_handlers import oauth_handler
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="MemeCraft Pro API", version="1.0.0")

# Create API router with /api prefix
api_router = APIRouter(prefix="/api")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=settings.CORS_ORIGINS if settings.CORS_ORIGINS != ['*'] else ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory for static file serving
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@api_router.post("/auth/signup", response_model=Token, tags=["Authentication"])
async def signup(user_data: UserCreate):
    """Register a new user with email and password"""
    # Check if user already exists
    existing_user = await get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    existing_username = await get_user_by_username(user_data.username)
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create new user
    user_dict = {
        "id": str(uuid.uuid4()),
        "email": user_data.email,
        "username": user_data.username,
        "password_hash": get_password_hash(user_data.password),
        "plan_type": PlanType.FREE.value,
        "storage_used": 0,
        "avatar": None
    }
    
    user = await create_user(user_dict)
    
    # Create access token
    access_token = create_access_token({"sub": user["id"]})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(**user)
    }

@api_router.post("/auth/login", response_model=Token, tags=["Authentication"])
async def login(credentials: UserLogin):
    """Login with email and password"""
    user = await authenticate_user(credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token = create_access_token({"sub": user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(**user.model_dump())
    }

@api_router.get("/auth/me", response_model=UserResponse, tags=["Authentication"])
async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@api_router.get("/auth/oauth/{provider}/url", tags=["Authentication"])
async def get_oauth_url(provider: Provider):
    """Get OAuth authorization URL for provider"""
    redirect_uri = f"{settings.FRONTEND_URL}/auth/callback/{provider.value.lower()}"
    
    if provider == Provider.TWITTER:
        if not settings.TWITTER_CLIENT_ID:
            raise HTTPException(status_code=500, detail="Twitter OAuth not configured")
        # Twitter OAuth 2.0 URL
        auth_url = f"https://twitter.com/i/oauth2/authorize?response_type=code&client_id={settings.TWITTER_CLIENT_ID}&redirect_uri={redirect_uri}&scope=tweet.read%20users.read&state=state123&code_challenge=challenge&code_challenge_method=plain"
        return {"url": auth_url}
    
    elif provider == Provider.REDDIT:
        if not settings.REDDIT_CLIENT_ID:
            raise HTTPException(status_code=500, detail="Reddit OAuth not configured")
        auth_url = f"https://www.reddit.com/api/v1/authorize?client_id={settings.REDDIT_CLIENT_ID}&response_type=code&state=state123&redirect_uri={redirect_uri}&duration=permanent&scope=identity%20read%20submit"
        return {"url": auth_url}
    
    elif provider == Provider.GOOGLE:
        if not settings.GOOGLE_CLIENT_ID:
            raise HTTPException(status_code=500, detail="Google OAuth not configured")
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={settings.GOOGLE_CLIENT_ID}&redirect_uri={redirect_uri}&response_type=code&scope=openid%20email%20profile&state=state123"
        return {"url": auth_url}
    
    raise HTTPException(status_code=400, detail="Invalid provider")

@api_router.post("/auth/oauth/{provider}/callback", response_model=Token, tags=["Authentication"])
async def oauth_callback(provider: Provider, code: str, state: str):
    """Handle OAuth callback from provider"""
    redirect_uri = f"{settings.FRONTEND_URL}/auth/callback/{provider.value.lower()}"
    result = await oauth_handler.handle_oauth_callback(provider, code, redirect_uri)
    
    return {
        "access_token": result["access_token"],
        "token_type": "bearer",
        "user": UserResponse(**result["user"])
    }

# ============================================================================
# MEME ROUTES
# ============================================================================

@api_router.get("/memes", response_model=List[MemeResponse], tags=["Memes"])
async def list_memes(
    skip: int = 0,
    limit: int = 50,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get user's memes"""
    memes = await get_user_memes(current_user.id, skip, limit)
    return [MemeResponse(**meme) for meme in memes]

@api_router.post("/memes", response_model=MemeResponse, tags=["Memes"])
async def create_meme_endpoint(
    meme_data: MemeCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new meme"""
    meme_dict = {
        "id": str(uuid.uuid4()),
        "user_id": current_user.id,
        **meme_data.model_dump()
    }
    
    meme = await create_meme(meme_dict)
    return MemeResponse(**meme)

@api_router.get("/memes/{meme_id}", response_model=MemeResponse, tags=["Memes"])
async def get_meme(
    meme_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get meme by ID"""
    meme = await get_meme_by_id(meme_id)
    if not meme:
        raise HTTPException(status_code=404, detail="Meme not found")
    
    # Check ownership (or team membership in future)
    if meme["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this meme")
    
    return MemeResponse(**meme)

@api_router.put("/memes/{meme_id}", response_model=MemeResponse, tags=["Memes"])
async def update_meme_endpoint(
    meme_id: str,
    meme_data: MemeUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update meme"""
    meme = await get_meme_by_id(meme_id)
    if not meme:
        raise HTTPException(status_code=404, detail="Meme not found")
    
    if meme["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this meme")
    
    # Update only provided fields
    update_dict = {k: v for k, v in meme_data.model_dump().items() if v is not None}
    updated_meme = await update_meme(meme_id, update_dict)
    
    return MemeResponse(**updated_meme)

@api_router.delete("/memes/{meme_id}", tags=["Memes"])
async def delete_meme_endpoint(
    meme_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete meme"""
    meme = await get_meme_by_id(meme_id)
    if not meme:
        raise HTTPException(status_code=404, detail="Meme not found")
    
    if meme["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this meme")
    
    await delete_meme(meme_id)
    return {"message": "Meme deleted successfully"}

@api_router.post("/memes/{meme_id}/duplicate", response_model=MemeResponse, tags=["Memes"])
async def duplicate_meme(
    meme_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Duplicate an existing meme"""
    meme = await get_meme_by_id(meme_id)
    if not meme:
        raise HTTPException(status_code=404, detail="Meme not found")
    
    # Create duplicate
    duplicate_dict = {
        "id": str(uuid.uuid4()),
        "user_id": current_user.id,
        "title": f"{meme['title']} (Copy)",
        "description": meme.get("description"),
        "canvas_data": meme["canvas_data"],
        "thumbnail_url": meme["thumbnail_url"],
        "status": "DRAFT",
        "tags": meme.get("tags", [])
    }
    
    new_meme = await create_meme(duplicate_dict)
    return MemeResponse(**new_meme)

# ============================================================================
# TEMPLATE ROUTES
# ============================================================================

@api_router.get("/templates", response_model=List[TemplateResponse], tags=["Templates"])
async def list_templates(
    category: Optional[str] = None,
    is_community: Optional[bool] = None,
    skip: int = 0,
    limit: int = 50
):
    """Get templates"""
    templates = await get_templates(category, is_community, skip, limit)
    return [TemplateResponse(**template) for template in templates]

@api_router.post("/templates", response_model=TemplateResponse, tags=["Templates"])
async def create_template_endpoint(
    template_data: TemplateCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new template"""
    template_dict = {
        "id": str(uuid.uuid4()),
        "creator_id": current_user.id,
        "votes": 0,
        "is_approved": not template_data.is_community,  # Auto-approve non-community
        **template_data.model_dump()
    }
    
    template = await create_template(template_dict)
    return TemplateResponse(**template)

@api_router.get("/templates/{template_id}", response_model=TemplateResponse, tags=["Templates"])
async def get_template(template_id: str):
    """Get template by ID"""
    template = await get_template_by_id(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return TemplateResponse(**template)

@api_router.post("/templates/{template_id}/vote", tags=["Templates"])
async def vote_template(
    template_id: str,
    vote: int = Query(..., ge=-1, le=1),
    current_user: UserResponse = Depends(get_current_user)
):
    """Vote on template (1 for upvote, -1 for downvote)"""
    template = await get_template_by_id(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    updated_template = await update_template_votes(template_id, vote)
    return TemplateResponse(**updated_template)

@api_router.get("/templates/categories/list", tags=["Templates"])
async def list_template_categories():
    """Get list of template categories"""
    # Return common categories
    categories = [
        "Reaction", "Advice", "Comparison", "Success", "Failure",
        "Gaming", "Work", "Relationship", "Pop Culture", "Sports",
        "Animals", "Technology", "Politics", "Other"
    ]
    return {"categories": categories}

# ============================================================================
# TREND ROUTES
# ============================================================================

@api_router.get("/trends", response_model=List[TrendResponse], tags=["Trends"])
async def list_trends(
    platform: Optional[str] = None,
    min_score: int = 0,
    skip: int = 0,
    limit: int = 20,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get trending memes (mock data)"""
    # Generate mock trends on the fly
    mock_trends = trends_service.generate_mock_trends(count=limit, platform=platform)
    
    # Store in database for future reference
    for trend_data in mock_trends[:5]:  # Store top 5
        try:
            await create_trend(trend_data)
        except:
            pass  # Ignore duplicates
    
    return [TrendResponse(**trend) for trend in mock_trends]

@api_router.get("/trends/{trend_id}", response_model=TrendResponse, tags=["Trends"])
async def get_trend(
    trend_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get trend by ID"""
    from database import trends_collection, exclude_id
    trend = await trends_collection.find_one({'id': trend_id})
    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")
    
    return TrendResponse(**exclude_id(trend))

# ============================================================================
# AI ROUTES
# ============================================================================

@api_router.post("/ai/generate-image", tags=["AI"])
async def generate_image_endpoint(
    request: ImageGenerateRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Generate image from prompt using DALL-E"""
    try:
        image_url = await ai_service.generate_image(
            request.prompt,
            request.width,
            request.height
        )
        return {"image_url": image_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/ai/suggest-captions", tags=["AI"])
async def suggest_captions_endpoint(
    request: CaptionSuggestRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Suggest captions for image using GPT-4 Vision"""
    try:
        captions = await ai_service.suggest_captions(request.image_url, request.context)
        return {"captions": captions}
    except Exception as e:
        logger.error(f"Caption suggestion error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/ai/generate-meme", tags=["AI"])
async def generate_complete_meme(
    topic: str = Query(..., description="Meme topic"),
    humor_style: str = Query("sarcastic", description="Humor style"),
    current_user: UserResponse = Depends(get_current_user)
):
    """Generate complete meme with AI"""
    try:
        meme_data = await ai_service.generate_meme_complete(topic, humor_style)
        return meme_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/ai/predict-viral", tags=["AI"])
async def predict_viral_endpoint(
    request: ViralPredictRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Predict viral potential of a meme"""
    meme = await get_meme_by_id(request.meme_id)
    if not meme:
        raise HTTPException(status_code=404, detail="Meme not found")
    
    if meme["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        viral_score = await ai_service.predict_viral_score(meme)
        return {"viral_score": viral_score, "meme_id": request.meme_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/ai/face-swap", tags=["AI"])
async def face_swap_endpoint(
    request: FaceSwapRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Perform face swap between two images using Replicate API"""
    try:
        result_url = await ai_service.face_swap(
            request.source_image_url,
            request.target_image_url
        )
        return {"result_url": result_url}
    except Exception as e:
        logger.error(f"Face swap error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/ai/remove-background", tags=["AI"])
async def remove_background_endpoint(
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_user)
):
    """Remove background from an uploaded image using rembg"""
    try:
        # Read image data
        image_data = await file.read()
        
        # Remove background
        output_data = await ai_service.remove_background(image_data)
        
        # Convert to base64 for response
        import base64
        output_base64 = base64.b64encode(output_data).decode('utf-8')
        result_url = f"data:image/png;base64,{output_base64}"
        
        return {"result_url": result_url}
    except Exception as e:
        logger.error(f"Background removal error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# FILE UPLOAD ROUTES
# ============================================================================

@api_router.post("/upload/image", tags=["Upload"])
async def upload_image(
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_user)
):
    """Upload an image file"""
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Check file size (10MB max)
    file_size = 0
    chunk = await file.read(settings.MAX_FILE_SIZE + 1)
    file_size = len(chunk)
    
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")
    
    # Reset file pointer
    await file.seek(0)
    
    try:
        # Save image
        image_url = await storage_service.save_image(file, folder=f"users/{current_user.id}")
        return {"url": image_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@api_router.post("/upload/file", tags=["Upload"])
async def upload_file(
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_user)
):
    """Upload a general file"""
    # Check file size
    file_size = 0
    chunk = await file.read(settings.MAX_FILE_SIZE + 1)
    file_size = len(chunk)
    
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")
    
    await file.seek(0)
    
    try:
        file_url = await storage_service.save_file(file, folder=f"users/{current_user.id}")
        return {"url": file_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# ============================================================================
# NOTIFICATION ROUTES
# ============================================================================

@api_router.get("/notifications", response_model=List[NotificationResponse], tags=["Notifications"])
async def list_notifications(
    unread_only: bool = False,
    skip: int = 0,
    limit: int = 50,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get user notifications"""
    notifications = await get_user_notifications(current_user.id, unread_only, skip, limit)
    return [NotificationResponse(**notif) for notif in notifications]

@api_router.put("/notifications/{notification_id}/read", tags=["Notifications"])
async def mark_notification_as_read(
    notification_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Mark notification as read"""
    success = await mark_notification_read(notification_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"message": "Notification marked as read"}

# ============================================================================
# COMMENT ROUTES
# ============================================================================

@api_router.get("/memes/{meme_id}/comments", response_model=List[CommentResponse], tags=["Comments"])
async def list_meme_comments(
    meme_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get comments for a meme"""
    meme = await get_meme_by_id(meme_id)
    if not meme:
        raise HTTPException(status_code=404, detail="Meme not found")
    
    comments = await get_meme_comments(meme_id)
    return [CommentResponse(**comment) for comment in comments]

@api_router.post("/memes/{meme_id}/comments", response_model=CommentResponse, tags=["Comments"])
async def create_comment_endpoint(
    meme_id: str,
    comment_data: CommentCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Add a comment to a meme"""
    meme = await get_meme_by_id(meme_id)
    if not meme:
        raise HTTPException(status_code=404, detail="Meme not found")
    
    comment_dict = {
        "id": str(uuid.uuid4()),
        "meme_id": meme_id,
        "user_id": current_user.id,
        "is_resolved": False,
        **comment_data.model_dump()
    }
    
    comment = await create_comment(comment_dict)
    return CommentResponse(**comment)

@api_router.put("/comments/{comment_id}/resolve", tags=["Comments"])
async def resolve_comment_endpoint(
    comment_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Mark comment as resolved"""
    success = await resolve_comment(comment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    return {"message": "Comment resolved"}

@api_router.delete("/comments/{comment_id}", tags=["Comments"])
async def delete_comment_endpoint(
    comment_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete a comment"""
    success = await delete_comment(comment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    return {"message": "Comment deleted"}

# ============================================================================
# HEALTH CHECK
# ============================================================================

@api_router.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "MemeCraft Pro API"}

@api_router.get("/", tags=["Health"])
async def root():
    """Root endpoint"""
    return {"message": "MemeCraft Pro API - Ready to create viral memes!", "version": "1.0.0"}

# Include router in app
app.include_router(api_router)

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    await close_db_connection()
    logger.info("Application shutdown complete")

# ============================================================================

# ============================================================================
# TEAM MANAGEMENT ROUTES
# ============================================================================

@api_router.post("/teams", response_model=TeamResponse, tags=["Teams"])
async def create_team_endpoint(
    team_data: TeamCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new team"""
    team_dict = {
        "id": str(uuid.uuid4()),
        "name": team_data.name,
        "owner_id": current_user.id,
        "plan_type": PlanType.TEAM.value,
        "storage_limit": 5 * 1024 * 1024 * 1024  # 5GB for team
    }
    
    team = await create_team(team_dict)
    
    # Add owner as team member
    member_dict = {
        "id": str(uuid.uuid4()),
        "team_id": team["id"],
        "user_id": current_user.id,
        "role": TeamRole.OWNER.value,
        "joined_at": datetime.utcnow().isoformat()
    }
    await add_team_member(member_dict)
    
    # Get member count
    members = await get_team_members(team["id"])
    team["member_count"] = len(members)
    
    return team

@api_router.get("/teams", response_model=List[TeamResponse], tags=["Teams"])
async def list_teams(
    current_user: UserResponse = Depends(get_current_user)
):
    """Get all teams user is member of"""
    teams = await get_user_teams(current_user.id)
    
    # Add member count to each team
    for team in teams:
        members = await get_team_members(team["id"])
        team["member_count"] = len(members)
    
    return teams

@api_router.get("/teams/{team_id}", response_model=TeamResponse, tags=["Teams"])
async def get_team_endpoint(
    team_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get team details"""
    # Check if user is member
    member = await get_team_member(team_id, current_user.id)
    if not member:
        raise HTTPException(status_code=403, detail="Not a team member")
    
    team = await get_team_by_id(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Add member count
    members = await get_team_members(team_id)
    team["member_count"] = len(members)
    
    return team

@api_router.put("/teams/{team_id}", response_model=TeamResponse, tags=["Teams"])
async def update_team_endpoint(
    team_id: str,
    team_data: TeamCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update team details (owner/admin only)"""
    member = await get_team_member(team_id, current_user.id)
    if not member or member["role"] not in [TeamRole.OWNER.value, TeamRole.ADMIN.value]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    team = await update_team(team_id, {"name": team_data.name})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    members = await get_team_members(team_id)
    team["member_count"] = len(members)
    
    return team

@api_router.delete("/teams/{team_id}", tags=["Teams"])
async def delete_team_endpoint(
    team_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete team (owner only)"""
    team = await get_team_by_id(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    if team["owner_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Only owner can delete team")
    
    await delete_team(team_id)
    return {"message": "Team deleted successfully"}

@api_router.get("/teams/{team_id}/members", response_model=List[TeamMemberResponse], tags=["Teams"])
async def list_team_members(
    team_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get all team members"""
    # Check if user is member
    member = await get_team_member(team_id, current_user.id)
    if not member:
        raise HTTPException(status_code=403, detail="Not a team member")
    
    members = await get_team_members(team_id)
    
    # Enrich with user data
    for m in members:
        user = await get_user_by_id(m["user_id"])
        if user:
            m["username"] = user.get("username")
            m["email"] = user.get("email")
    
    return members

@api_router.post("/teams/{team_id}/invite", tags=["Teams"])
async def invite_team_member(
    team_id: str,
    invite_data: TeamInvite,
    current_user: UserResponse = Depends(get_current_user)
):
    """Invite user to team (owner/admin only)"""
    member = await get_team_member(team_id, current_user.id)
    if not member or member["role"] not in [TeamRole.OWNER.value, TeamRole.ADMIN.value]:
        raise HTTPException(status_code=403, detail="Not authorized to invite")
    
    # Find user by email
    invited_user = await get_user_by_email(invite_data.email)
    if not invited_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already member
    existing = await get_team_member(team_id, invited_user["id"])
    if existing:
        raise HTTPException(status_code=400, detail="User already in team")
    
    # Create team member record
    member_dict = {
        "id": str(uuid.uuid4()),
        "team_id": team_id,
        "user_id": invited_user["id"],
        "role": invite_data.role.value
    }
    await add_team_member(member_dict)
    
    # Create notification
    notification_dict = {
        "id": str(uuid.uuid4()),
        "user_id": invited_user["id"],
        "type": "TEAM_INVITE",
        "title": "Team Invitation",
        "message": f"You've been invited to join {await get_team_by_id(team_id)}",
        "is_read": False
    }
    await create_notification(notification_dict)
    
    return {"message": "Invitation sent", "user_id": invited_user["id"]}

@api_router.post("/teams/{team_id}/accept", tags=["Teams"])
async def accept_team_invitation(
    team_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Accept team invitation"""
    member = await get_team_member(team_id, current_user.id)
    if not member:
        raise HTTPException(status_code=404, detail="No invitation found")
    
    if member.get("joined_at"):
        raise HTTPException(status_code=400, detail="Already accepted")
    
    await accept_team_invite(team_id, current_user.id)
    return {"message": "Team invitation accepted"}

@api_router.put("/teams/{team_id}/members/{user_id}/role", tags=["Teams"])
async def update_member_role(
    team_id: str,
    user_id: str,
    role: TeamRole = Query(...),
    current_user: UserResponse = Depends(get_current_user)
):
    """Update team member role (owner/admin only)"""
    member = await get_team_member(team_id, current_user.id)
    if not member or member["role"] not in [TeamRole.OWNER.value, TeamRole.ADMIN.value]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Can't change owner role
    target_member = await get_team_member(team_id, user_id)
    if target_member and target_member["role"] == TeamRole.OWNER.value:
        raise HTTPException(status_code=400, detail="Cannot change owner role")
    
    await update_team_member_role(team_id, user_id, role.value)
    return {"message": "Role updated"}

@api_router.delete("/teams/{team_id}/members/{user_id}", tags=["Teams"])
async def remove_member(
    team_id: str,
    user_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Remove team member (owner/admin only or self)"""
    member = await get_team_member(team_id, current_user.id)
    
    # Allow self-removal or owner/admin removal
    if user_id != current_user.id:
        if not member or member["role"] not in [TeamRole.OWNER.value, TeamRole.ADMIN.value]:
            raise HTTPException(status_code=403, detail="Not authorized")
    
    # Can't remove owner
    target_member = await get_team_member(team_id, user_id)
    if target_member and target_member["role"] == TeamRole.OWNER.value:
        raise HTTPException(status_code=400, detail="Cannot remove owner")
    
    await remove_team_member(team_id, user_id)
    return {"message": "Member removed"}


# REAL-TIME COLLABORATION (Socket.IO)
# ============================================================================

from collaboration import sio as collaboration_sio, app as socket_app

# Mount Socket.IO app
app.mount("/socket.io", socket_app)

# Collaboration endpoints
@api_router.get("/collaboration/active-users/{meme_id}", tags=["Collaboration"])
async def get_active_users(
    meme_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get count of active users for a meme"""
    from collaboration import get_active_users as get_users_count
    count = get_users_count(meme_id)
    return {"meme_id": meme_id, "active_users": count}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
