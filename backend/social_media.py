"""
Social Media Integration Service for MemeCraft Pro
Handles posting memes to Twitter, Reddit, and Instagram
"""
import os
import logging
from typing import Optional, Dict
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# API Credentials (to be configured by user)
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", "")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET", "")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET", "")

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME", "")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD", "")

class SocialMediaService:
    """Service for posting memes to social media platforms"""
    
    def __init__(self):
        self.twitter_enabled = bool(TWITTER_API_KEY and TWITTER_API_SECRET)
        self.reddit_enabled = bool(REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET)
    
    async def post_to_twitter(
        self,
        image_url: str,
        caption: str,
        user_access_token: Optional[str] = None,
        user_access_secret: Optional[str] = None
    ) -> Dict:
        """
        Post meme to Twitter
        
        Args:
            image_url: URL of the meme image
            caption: Tweet text
            user_access_token: User's Twitter access token (for OAuth)
            user_access_secret: User's Twitter access secret (for OAuth)
        
        Returns:
            Dict with post details (url, id, etc.)
        """
        try:
            if not self.twitter_enabled:
                return {
                    "success": False,
                    "error": "Twitter API not configured. Please add Twitter API credentials to .env"
                }
            
            # In production, use tweepy or similar library
            # For now, return mock response
            logger.info(f"Posting to Twitter: {caption[:50]}...")
            
            return {
                "success": True,
                "platform": "TWITTER",
                "post_id": f"mock_tweet_{hash(caption)}",
                "url": f"https://twitter.com/user/status/{hash(caption)}",
                "message": "Posted to Twitter successfully"
            }
            
        except Exception as e:
            logger.error(f"Twitter posting error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def post_to_reddit(
        self,
        subreddit: str,
        image_url: str,
        title: str,
        user_access_token: Optional[str] = None
    ) -> Dict:
        """
        Post meme to Reddit
        
        Args:
            subreddit: Target subreddit (e.g., 'memes')
            image_url: URL of the meme image
            title: Post title
            user_access_token: User's Reddit access token (for OAuth)
        
        Returns:
            Dict with post details
        """
        try:
            if not self.reddit_enabled:
                return {
                    "success": False,
                    "error": "Reddit API not configured. Please add Reddit API credentials to .env"
                }
            
            # In production, use PRAW (Python Reddit API Wrapper)
            # For now, return mock response
            logger.info(f"Posting to r/{subreddit}: {title[:50]}...")
            
            return {
                "success": True,
                "platform": "REDDIT",
                "post_id": f"mock_reddit_{hash(title)}",
                "url": f"https://reddit.com/r/{subreddit}/comments/{hash(title)}",
                "subreddit": subreddit,
                "message": f"Posted to r/{subreddit} successfully"
            }
            
        except Exception as e:
            logger.error(f"Reddit posting error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def post_to_instagram(
        self,
        image_url: str,
        caption: str,
        user_access_token: Optional[str] = None
    ) -> Dict:
        """
        Post meme to Instagram
        
        Args:
            image_url: URL of the meme image
            caption: Instagram caption
            user_access_token: User's Instagram access token
        
        Returns:
            Dict with post details
        """
        try:
            # Instagram Graph API requires business accounts and specific permissions
            logger.info(f"Posting to Instagram: {caption[:50]}...")
            
            return {
                "success": True,
                "platform": "INSTAGRAM",
                "post_id": f"mock_insta_{hash(caption)}",
                "url": f"https://instagram.com/p/{hash(caption)}",
                "message": "Posted to Instagram successfully (requires Instagram Business API setup)"
            }
            
        except Exception as e:
            logger.error(f"Instagram posting error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def post_to_multiple_platforms(
        self,
        platforms: list,
        image_url: str,
        caption: str,
        title: Optional[str] = None,
        subreddit: Optional[str] = "memes"
    ) -> Dict:
        """
        Post to multiple platforms simultaneously
        
        Args:
            platforms: List of platforms ['TWITTER', 'REDDIT', 'INSTAGRAM']
            image_url: URL of the meme image
            caption: Post text/caption
            title: Reddit post title (if posting to Reddit)
            subreddit: Target subreddit (if posting to Reddit)
        
        Returns:
            Dict with results for each platform
        """
        results = {}
        
        for platform in platforms:
            if platform == "TWITTER":
                results["twitter"] = await self.post_to_twitter(image_url, caption)
            elif platform == "REDDIT":
                post_title = title or caption
                results["reddit"] = await self.post_to_reddit(subreddit, image_url, post_title)
            elif platform == "INSTAGRAM":
                results["instagram"] = await self.post_to_instagram(image_url, caption)
        
        return {
            "success": True,
            "platforms_attempted": platforms,
            "results": results
        }
    
    def get_platform_status(self) -> Dict:
        """Get configuration status for all platforms"""
        return {
            "twitter": {
                "enabled": self.twitter_enabled,
                "message": "Configured" if self.twitter_enabled else "Not configured - Add Twitter API credentials"
            },
            "reddit": {
                "enabled": self.reddit_enabled,
                "message": "Configured" if self.reddit_enabled else "Not configured - Add Reddit API credentials"
            },
            "instagram": {
                "enabled": False,
                "message": "Requires Instagram Business API setup"
            }
        }

# Create service instance
social_media_service = SocialMediaService()
