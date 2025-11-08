import os
import random
from typing import List, Optional
from openai import AsyncOpenAI
from config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize OpenAI client with Emergent LLM key
client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL
)

class AIService:
    """AI service for image generation and caption suggestions using Emergent LLM key"""
    
    async def generate_image(self, prompt: str, width: int = 1024, height: int = 1024) -> str:
        """Generate image using DALL-E via Emergent LLM key"""
        try:
            response = await client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=f"{width}x{height}" if width == height else "1024x1024",
                quality="standard",
                n=1,
            )
            
            image_url = response.data[0].url
            logger.info(f"Generated image for prompt: {prompt[:50]}...")
            return image_url
            
        except Exception as e:
            logger.error(f"Image generation error: {str(e)}")
            raise Exception(f"Failed to generate image: {str(e)}")
    
    async def suggest_captions(self, image_url: str, context: Optional[str] = None) -> List[str]:
        """Generate caption suggestions using GPT-4 Vision"""
        try:
            prompt = f"Generate 5 funny and viral-worthy meme captions for this image."
            if context:
                prompt += f" Context: {context}"
            prompt += " Return only the captions, one per line. Be creative and humorous."
            
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }
                ],
                max_tokens=500
            )
            
            captions_text = response.choices[0].message.content
            captions = [c.strip() for c in captions_text.split('\n') if c.strip()]
            
            logger.info(f"Generated {len(captions)} captions for image")
            return captions[:5]  # Return max 5 captions
            
        except Exception as e:
            logger.error(f"Caption generation error: {str(e)}")
            # Return fallback captions
            return [
                "When you finally understand the joke",
                "Me trying to act normal",
                "POV: You're the main character",
                "This is fine",
                "Expectation vs Reality"
            ]
    
    async def generate_meme_complete(self, topic: str, humor_style: str = "sarcastic") -> dict:
        """Generate a complete meme (text + context) using GPT-4"""
        try:
            prompt = f"""Generate a meme idea about "{topic}" with a {humor_style} humor style.
            
Provide:
1. A short title/caption (max 50 chars)
2. Top text for the meme (if applicable, max 30 chars)
3. Bottom text for the meme (if applicable, max 30 chars)
4. Image description for DALL-E (detailed, max 100 words)

Format your response as JSON with keys: title, top_text, bottom_text, image_description"""
            
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                response_format={"type": "json_object"}
            )
            
            import json
            meme_data = json.loads(response.choices[0].message.content)
            
            # Generate the actual image
            if 'image_description' in meme_data:
                image_url = await self.generate_image(meme_data['image_description'])
                meme_data['image_url'] = image_url
            
            logger.info(f"Generated complete meme for topic: {topic}")
            return meme_data
            
        except Exception as e:
            logger.error(f"Complete meme generation error: {str(e)}")
            raise Exception(f"Failed to generate meme: {str(e)}")
    
    async def predict_viral_score(self, meme_data: dict) -> int:
        """Predict viral potential of a meme (simplified version)"""
        try:
            # Use GPT-4 to analyze meme potential
            prompt = f"""Analyze this meme and predict its viral potential on a scale of 0-100.
            
Meme title: {meme_data.get('title', 'Untitled')}
Tags: {', '.join(meme_data.get('tags', []))}

Consider factors like:
- Relatability
- Humor quality
- Current trends
- Visual appeal

Respond with just a number between 0-100."""
            
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.5
            )
            
            score_text = response.choices[0].message.content.strip()
            score = int(''.join(filter(str.isdigit, score_text)))
            score = max(0, min(100, score))  # Clamp between 0-100
            
            logger.info(f"Predicted viral score: {score}")
            return score
            
        except Exception as e:
            logger.error(f"Viral prediction error: {str(e)}")
            # Return random score as fallback
            return random.randint(40, 85)

ai_service = AIService()
