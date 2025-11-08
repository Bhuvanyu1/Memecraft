from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, List, Dict, Any
from datetime import datetime
from config import settings
import logging

logger = logging.getLogger(__name__)

# MongoDB connection
client = AsyncIOMotorClient(settings.MONGO_URL)
db = client[settings.DB_NAME]

# Collections
users_collection = db.users
social_auth_collection = db.social_auth
memes_collection = db.memes
templates_collection = db.templates
trends_collection = db.trends
teams_collection = db.teams
team_members_collection = db.team_members
analytics_collection = db.analytics
notifications_collection = db.notifications
comments_collection = db.comments

# Helper function to exclude MongoDB _id
def exclude_id(doc: Optional[Dict]) -> Optional[Dict]:
    if doc:
        doc.pop('_id', None)
    return doc

# User operations
async def create_user(user_data: dict) -> dict:
    user_data['created_at'] = datetime.utcnow().isoformat()
    user_data['updated_at'] = datetime.utcnow().isoformat()
    await users_collection.insert_one(user_data)
    return exclude_id(user_data)

async def get_user_by_email(email: str) -> Optional[dict]:
    user = await users_collection.find_one({'email': email})
    return exclude_id(user)

async def get_user_by_id(user_id: str) -> Optional[dict]:
    user = await users_collection.find_one({'id': user_id})
    return exclude_id(user)

async def get_user_by_username(username: str) -> Optional[dict]:
    user = await users_collection.find_one({'username': username})
    return exclude_id(user)

async def update_user(user_id: str, user_data: dict) -> Optional[dict]:
    user_data['updated_at'] = datetime.utcnow().isoformat()
    await users_collection.update_one({'id': user_id}, {'$set': user_data})
    return await get_user_by_id(user_id)

# Social Auth operations
async def create_social_auth(auth_data: dict) -> dict:
    auth_data['created_at'] = datetime.utcnow().isoformat()
    auth_data['updated_at'] = datetime.utcnow().isoformat()
    await social_auth_collection.insert_one(auth_data)
    return exclude_id(auth_data)

async def get_social_auth(provider: str, provider_user_id: str) -> Optional[dict]:
    auth = await social_auth_collection.find_one({
        'provider': provider,
        'provider_user_id': provider_user_id
    })
    return exclude_id(auth)

async def get_user_social_auths(user_id: str) -> List[dict]:
    auths = await social_auth_collection.find({'user_id': user_id}).to_list(100)
    return [exclude_id(auth) for auth in auths]

# Meme operations
async def create_meme(meme_data: dict) -> dict:
    meme_data['created_at'] = datetime.utcnow().isoformat()
    meme_data['updated_at'] = datetime.utcnow().isoformat()
    await memes_collection.insert_one(meme_data)
    return exclude_id(meme_data)

async def get_meme_by_id(meme_id: str) -> Optional[dict]:
    meme = await memes_collection.find_one({'id': meme_id})
    return exclude_id(meme)

async def get_user_memes(user_id: str, skip: int = 0, limit: int = 50) -> List[dict]:
    memes = await memes_collection.find({'user_id': user_id}).skip(skip).limit(limit).to_list(limit)
    return [exclude_id(meme) for meme in memes]

async def update_meme(meme_id: str, meme_data: dict) -> Optional[dict]:
    meme_data['updated_at'] = datetime.utcnow().isoformat()
    await memes_collection.update_one({'id': meme_id}, {'$set': meme_data})
    return await get_meme_by_id(meme_id)

async def delete_meme(meme_id: str) -> bool:
    result = await memes_collection.delete_one({'id': meme_id})
    return result.deleted_count > 0

# Template operations
async def create_template(template_data: dict) -> dict:
    template_data['created_at'] = datetime.utcnow().isoformat()
    template_data['updated_at'] = datetime.utcnow().isoformat()
    await templates_collection.insert_one(template_data)
    return exclude_id(template_data)

async def get_template_by_id(template_id: str) -> Optional[dict]:
    template = await templates_collection.find_one({'id': template_id})
    return exclude_id(template)

async def get_templates(category: Optional[str] = None, is_community: Optional[bool] = None, 
                       skip: int = 0, limit: int = 50) -> List[dict]:
    query = {}
    if category:
        query['category'] = category
    if is_community is not None:
        query['is_community'] = is_community
        if is_community:
            query['is_approved'] = True
    
    templates = await templates_collection.find(query).sort('votes', -1).skip(skip).limit(limit).to_list(limit)
    return [exclude_id(template) for template in templates]

async def update_template_votes(template_id: str, increment: int) -> Optional[dict]:
    await templates_collection.update_one({'id': template_id}, {'$inc': {'votes': increment}})
    return await get_template_by_id(template_id)

# Trend operations
async def create_trend(trend_data: dict) -> dict:
    trend_data['created_at'] = datetime.utcnow().isoformat()
    trend_data['updated_at'] = datetime.utcnow().isoformat()
    await trends_collection.insert_one(trend_data)
    return exclude_id(trend_data)

async def get_trends(platform: Optional[str] = None, min_score: int = 0, 
                     skip: int = 0, limit: int = 50) -> List[dict]:
    query = {'viral_score': {'$gte': min_score}}
    if platform:
        query['platform'] = platform
    
    trends = await trends_collection.find(query).sort('viral_score', -1).skip(skip).limit(limit).to_list(limit)
    return [exclude_id(trend) for trend in trends]

# Team operations
async def create_team(team_data: dict) -> dict:
    team_data['created_at'] = datetime.utcnow().isoformat()
    team_data['updated_at'] = datetime.utcnow().isoformat()
    await teams_collection.insert_one(team_data)
    return exclude_id(team_data)

async def get_team_by_id(team_id: str) -> Optional[dict]:
    team = await teams_collection.find_one({'id': team_id})
    return exclude_id(team)

async def get_user_teams(user_id: str) -> List[dict]:
    member_records = await team_members_collection.find({'user_id': user_id}).to_list(100)
    team_ids = [m['team_id'] for m in member_records]
    teams = await teams_collection.find({'id': {'$in': team_ids}}).to_list(100)
    return [exclude_id(team) for team in teams]

# Notification operations
async def create_notification(notification_data: dict) -> dict:
    notification_data['created_at'] = datetime.utcnow().isoformat()
    notification_data['updated_at'] = datetime.utcnow().isoformat()
    await notifications_collection.insert_one(notification_data)
    return exclude_id(notification_data)

async def get_user_notifications(user_id: str, unread_only: bool = False, 
                                 skip: int = 0, limit: int = 50) -> List[dict]:
    query = {'user_id': user_id}
    if unread_only:
        query['is_read'] = False
    
    notifications = await notifications_collection.find(query).sort('created_at', -1).skip(skip).limit(limit).to_list(limit)
    return [exclude_id(n) for n in notifications]

async def mark_notification_read(notification_id: str) -> bool:
    result = await notifications_collection.update_one(
        {'id': notification_id},
        {'$set': {'is_read': True, 'updated_at': datetime.utcnow().isoformat()}}
    )
    return result.modified_count > 0

# Comment operations
async def create_comment(comment_data: dict) -> dict:
    comment_data['created_at'] = datetime.utcnow().isoformat()
    comment_data['updated_at'] = datetime.utcnow().isoformat()
    await comments_collection.insert_one(comment_data)
    return exclude_id(comment_data)

async def get_meme_comments(meme_id: str) -> List[dict]:
    comments = await comments_collection.find({'meme_id': meme_id}).sort('created_at', 1).to_list(1000)
    return [exclude_id(comment) for comment in comments]

async def resolve_comment(comment_id: str) -> bool:
    result = await comments_collection.update_one(
        {'id': comment_id},
        {'$set': {'is_resolved': True, 'updated_at': datetime.utcnow().isoformat()}}
    )
    return result.modified_count > 0

async def delete_comment(comment_id: str) -> bool:
    result = await comments_collection.delete_one({'id': comment_id})
    return result.deleted_count > 0

# Shutdown
async def close_db_connection():
    client.close()
