import random
from datetime import datetime, timedelta
from typing import List, Optional
from models import Platform, Trend
import logging

logger = logging.getLogger(__name__)

class TrendsService:
    """Mock trends service - generates sample trending memes"""
    
    MOCK_TRENDS = [
        {
            "title": "Distracted Boyfriend Returns",
            "description": "The classic meme is back with a new twist",
            "image_url": "https://i.imgflip.com/1ur9b0.jpg",
            "platform": Platform.TWITTER,
            "engagement_data": {"likes": 45231, "retweets": 8934, "comments": 1245}
        },
        {
            "title": "Woman Yelling at Cat - 2025 Edition",
            "description": "This meme never gets old",
            "image_url": "https://i.imgflip.com/345v97.jpg",
            "platform": Platform.TWITTER,
            "engagement_data": {"likes": 67432, "retweets": 12453, "comments": 2341}
        },
        {
            "title": "Drake Hotline Bling",
            "description": "Drake's approval/disapproval format still trending",
            "image_url": "https://i.imgflip.com/30b1gx.jpg",
            "platform": Platform.REDDIT,
            "engagement_data": {"score": 34567, "comments": 567, "upvote_ratio": 0.94}
        },
        {
            "title": "Is This a Pigeon?",
            "description": "Perfect for any confusion scenario",
            "image_url": "https://i.imgflip.com/1o00in.jpg",
            "platform": Platform.REDDIT,
            "engagement_data": {"score": 28934, "comments": 423, "upvote_ratio": 0.91}
        },
        {
            "title": "Two Buttons",
            "description": "Difficult choices require strong wills",
            "image_url": "https://i.imgflip.com/1g8my4.jpg",
            "platform": Platform.TWITTER,
            "engagement_data": {"likes": 39842, "retweets": 7234, "comments": 934}
        },
        {
            "title": "Change My Mind",
            "description": "Steven Crowder's controversial opinion format",
            "image_url": "https://i.imgflip.com/24y43o.jpg",
            "platform": Platform.REDDIT,
            "engagement_data": {"score": 41234, "comments": 892, "upvote_ratio": 0.88}
        },
        {
            "title": "Expanding Brain",
            "description": "From basic to galaxy brain",
            "image_url": "https://i.imgflip.com/1jwhww.jpg",
            "platform": Platform.TWITTER,
            "engagement_data": {"likes": 52341, "retweets": 9876, "comments": 1567}
        },
        {
            "title": "Bernie Sanders Mittens",
            "description": "The inauguration meme that keeps giving",
            "image_url": "https://i.imgflip.com/4t0m5.jpg",
            "platform": Platform.REDDIT,
            "engagement_data": {"score": 67893, "comments": 1234, "upvote_ratio": 0.96}
        },
        {
            "title": "Always Has Been",
            "description": "Wait, it's all...? Always has been.",
            "image_url": "https://i.imgflip.com/46e43q.jpg",
            "platform": Platform.TWITTER,
            "engagement_data": {"likes": 44567, "retweets": 8234, "comments": 1123}
        },
        {
            "title": "This Is Fine",
            "description": "Dog in burning room - perfect for 2025",
            "image_url": "https://i.imgflip.com/wxica.jpg",
            "platform": Platform.REDDIT,
            "engagement_data": {"score": 58234, "comments": 987, "upvote_ratio": 0.93}
        }
    ]
    
    def calculate_viral_score(self, engagement_data: dict, platform: Platform) -> int:
        """Calculate viral score based on engagement"""
        if platform == Platform.TWITTER:
            likes = engagement_data.get('likes', 0)
            retweets = engagement_data.get('retweets', 0)
            # Simple algorithm: more retweets = more viral
            score = min(100, (likes / 1000 + retweets / 100))
        elif platform == Platform.REDDIT:
            score_val = engagement_data.get('score', 0)
            ratio = engagement_data.get('upvote_ratio', 0.5)
            # High score + high ratio = more viral
            score = min(100, (score_val / 1000) * ratio * 100)
        else:
            score = random.randint(50, 90)
        
        # Add some randomness
        score = int(score + random.randint(-5, 15))
        return max(0, min(100, score))
    
    def generate_mock_trends(self, count: int = 10, platform: Optional[str] = None) -> List[dict]:
        """Generate mock trending memes"""
        trends = []
        mock_data = self.MOCK_TRENDS.copy()
        
        # Filter by platform if specified
        if platform:
            mock_data = [t for t in mock_data if t['platform'].value == platform.upper()]
        
        # Shuffle and select
        random.shuffle(mock_data)
        selected = mock_data[:count]
        
        # Generate trend objects
        for idx, trend_data in enumerate(selected):
            viral_score = self.calculate_viral_score(
                trend_data['engagement_data'],
                trend_data['platform']
            )
            
            trend = {
                "id": f"trend-{idx}-{datetime.now().timestamp()}",
                "platform": trend_data['platform'].value,
                "title": trend_data['title'],
                "description": trend_data['description'],
                "image_url": trend_data['image_url'],
                "viral_score": viral_score,
                "engagement_data": trend_data['engagement_data'],
                "discovered_at": (datetime.utcnow() - timedelta(hours=random.randint(1, 24))).isoformat(),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            trends.append(trend)
        
        # Sort by viral score
        trends.sort(key=lambda x: x['viral_score'], reverse=True)
        logger.info(f"Generated {len(trends)} mock trends")
        return trends

trends_service = TrendsService()
