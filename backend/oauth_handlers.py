from typing import Optional, Dict
import httpx
from fastapi import HTTPException
import logging
from config import settings
from database import get_social_auth, create_social_auth, get_user_by_id, create_user, update_user
from models import Provider, User, PlanType
from auth import create_access_token
import uuid

logger = logging.getLogger(__name__)

class OAuthHandler:
    """OAuth authentication handler for Twitter, Reddit, and Google"""
    
    async def handle_oauth_callback(self, provider: Provider, code: str, 
                                   redirect_uri: str) -> Dict[str, any]:
        """Handle OAuth callback from provider"""
        try:
            # Exchange code for access token
            token_data = await self.exchange_code_for_token(provider, code, redirect_uri)
            
            # Get user info from provider
            user_info = await self.get_user_info(provider, token_data['access_token'])
            
            # Find or create user
            user = await self.find_or_create_user(provider, user_info, token_data)
            
            # Create JWT token
            access_token = create_access_token({"sub": user['id']})
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": user
            }
            
        except Exception as e:
            logger.error(f"OAuth callback error: {str(e)}")
            raise HTTPException(status_code=400, detail=f"OAuth authentication failed: {str(e)}")
    
    async def exchange_code_for_token(self, provider: Provider, code: str, 
                                     redirect_uri: str) -> Dict[str, str]:
        """Exchange authorization code for access token"""
        if provider == Provider.TWITTER:
            return await self.twitter_token_exchange(code, redirect_uri)
        elif provider == Provider.REDDIT:
            return await self.reddit_token_exchange(code, redirect_uri)
        elif provider == Provider.GOOGLE:
            return await self.google_token_exchange(code, redirect_uri)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    async def twitter_token_exchange(self, code: str, redirect_uri: str) -> Dict[str, str]:
        """Exchange Twitter OAuth code for token"""
        if not settings.TWITTER_CLIENT_ID or not settings.TWITTER_CLIENT_SECRET:
            raise HTTPException(status_code=500, detail="Twitter OAuth not configured")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.twitter.com/2/oauth2/token",
                data={
                    "code": code,
                    "grant_type": "authorization_code",
                    "client_id": settings.TWITTER_CLIENT_ID,
                    "redirect_uri": redirect_uri,
                    "code_verifier": "challenge",  # Use actual PKCE verifier in production
                },
                auth=(settings.TWITTER_CLIENT_ID, settings.TWITTER_CLIENT_SECRET)
            )
            response.raise_for_status()
            return response.json()
    
    async def reddit_token_exchange(self, code: str, redirect_uri: str) -> Dict[str, str]:
        """Exchange Reddit OAuth code for token"""
        if not settings.REDDIT_CLIENT_ID or not settings.REDDIT_CLIENT_SECRET:
            raise HTTPException(status_code=500, detail="Reddit OAuth not configured")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://www.reddit.com/api/v1/access_token",
                data={
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri,
                },
                auth=(settings.REDDIT_CLIENT_ID, settings.REDDIT_CLIENT_SECRET)
            )
            response.raise_for_status()
            return response.json()
    
    async def google_token_exchange(self, code: str, redirect_uri: str) -> Dict[str, str]:
        """Exchange Google OAuth code for token"""
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            raise HTTPException(status_code=500, detail="Google OAuth not configured")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def get_user_info(self, provider: Provider, access_token: str) -> Dict[str, any]:
        """Get user info from OAuth provider"""
        if provider == Provider.TWITTER:
            return await self.get_twitter_user_info(access_token)
        elif provider == Provider.REDDIT:
            return await self.get_reddit_user_info(access_token)
        elif provider == Provider.GOOGLE:
            return await self.get_google_user_info(access_token)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    async def get_twitter_user_info(self, access_token: str) -> Dict[str, any]:
        """Get Twitter user info"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.twitter.com/2/users/me",
                headers={"Authorization": f"Bearer {access_token}"},
                params={"user.fields": "profile_image_url,username"}
            )
            response.raise_for_status()
            data = response.json()['data']
            return {
                "id": data['id'],
                "username": data['username'],
                "avatar": data.get('profile_image_url'),
                "email": f"{data['username']}@twitter.placeholder.com"  # Twitter doesn't provide email in v2
            }
    
    async def get_reddit_user_info(self, access_token: str) -> Dict[str, any]:
        """Get Reddit user info"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://oauth.reddit.com/api/v1/me",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "User-Agent": "MemeCraft/1.0"
                }
            )
            response.raise_for_status()
            data = response.json()
            return {
                "id": data['id'],
                "username": data['name'],
                "avatar": data.get('icon_img', '').split('?')[0] if data.get('icon_img') else None,
                "email": f"{data['name']}@reddit.placeholder.com"  # Reddit doesn't provide email
            }
    
    async def get_google_user_info(self, access_token: str) -> Dict[str, any]:
        """Get Google user info"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status()
            data = response.json()
            return {
                "id": data['id'],
                "username": data.get('name', data['email'].split('@')[0]),
                "avatar": data.get('picture'),
                "email": data['email']
            }
    
    async def find_or_create_user(self, provider: Provider, user_info: Dict[str, any], 
                                 token_data: Dict[str, str]) -> Dict[str, any]:
        """Find existing user or create new one"""
        # Check if social auth exists
        social_auth = await get_social_auth(provider.value, user_info['id'])
        
        if social_auth:
            # Update tokens
            social_auth['access_token'] = token_data['access_token']
            social_auth['refresh_token'] = token_data.get('refresh_token')
            # Get existing user
            user = await get_user_by_id(social_auth['user_id'])
            return user
        
        # Check if user exists by email
        from database import get_user_by_email
        existing_user = await get_user_by_email(user_info['email'])
        
        if existing_user:
            user_id = existing_user['id']
        else:
            # Create new user
            new_user = {
                "id": str(uuid.uuid4()),
                "email": user_info['email'],
                "username": user_info['username'],
                "avatar": user_info.get('avatar'),
                "plan_type": PlanType.FREE.value,
                "storage_used": 0
            }
            user = await create_user(new_user)
            user_id = user['id']
        
        # Create social auth record
        await create_social_auth({
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "provider": provider.value,
            "provider_user_id": user_info['id'],
            "access_token": token_data['access_token'],
            "refresh_token": token_data.get('refresh_token'),
            "expires_at": None
        })
        
        return await get_user_by_id(user_id)

oauth_handler = OAuthHandler()
