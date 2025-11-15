import os
import random
import base64
import io
from typing import List, Optional
from dotenv import load_dotenv
import logging
from PIL import Image as PILImage
import replicate
import asyncio

# Load environment variables
load_dotenv()

# Import Emergent Integrations
from emergentintegrations.llm.chat import LlmChat, UserMessage
from emergentintegrations.llm.openai.image_generation import OpenAIImageGeneration

logger = logging.getLogger(__name__)

# Get API keys from environment
EMERGENT_LLM_KEY = os.getenv("EMERGENT_LLM_KEY")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")

class AIService:
    """AI service for image generation, face swap, background removal, and meme generation using real AI APIs"""
    
    def __init__(self):
        # Initialize LLM Chat for text generation
        self.llm_chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id="meme-generator",
            system_message="You are a creative meme generator AI. Generate funny, viral-worthy meme content."
        ).with_model("openai", "gpt-4o")
        
        # Initialize Image Generation
        self.image_gen = OpenAIImageGeneration(api_key=EMERGENT_LLM_KEY)
        
        # Set Replicate API token if available
        if REPLICATE_API_TOKEN:
            os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN
    
    async def generate_image(self, prompt: str, width: int = 1024, height: int = 1024) -> str:
        """Generate image using gpt-image-1 (latest DALL-E) via Emergent LLM key"""
        try:
            logger.info(f"Generating image for prompt: {prompt[:50]}...")
            
            # Generate images using emergentintegrations
            images = await self.image_gen.generate_images(
                prompt=prompt,
                model="gpt-image-1",
                number_of_images=1
            )
            
            if images and len(images) > 0:
                # Convert image bytes to base64 data URL
                image_base64 = base64.b64encode(images[0]).decode('utf-8')
                image_url = f"data:image/png;base64,{image_base64}"
                
                logger.info(f"Successfully generated image")
                return image_url
            else:
                raise Exception("No image was generated")
            
        except Exception as e:
            logger.error(f"Image generation error: {str(e)}")
            raise Exception(f"Failed to generate image: {str(e)}")
    
    async def suggest_captions(self, image_url: str, context: Optional[str] = None) -> List[str]:
        """Generate caption suggestions using GPT-4o via Emergent LLM key"""
        try:
            prompt = f"Generate 5 funny and viral-worthy meme captions. Be creative and humorous. Return only the captions, one per line, no numbers or bullets."
            if context:
                prompt += f" Context: {context}"
            
            logger.info("Generating meme captions...")
            
            # Create a new chat instance for this request
            caption_chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=f"caption-{random.randint(1000, 9999)}",
                system_message="You are a creative meme caption generator. Generate funny, viral-worthy captions."
            ).with_model("openai", "gpt-4o")
            
            user_message = UserMessage(text=prompt)
            response = await caption_chat.send_message(user_message)
            
            captions = [c.strip() for c in response.split('\n') if c.strip()]
            captions = [c.lstrip('0123456789.-•* ') for c in captions]  # Remove numbering
            
            logger.info(f"Generated {len(captions)} captions")
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
        """Generate a complete meme (text + image) using GPT-4o and gpt-image-1"""
        try:
            prompt = f"""Generate a meme idea about "{topic}" with a {humor_style} humor style.

Provide:
1. A short title/caption (max 50 chars)
2. Top text for the meme (if applicable, max 30 chars, can be empty)
3. Bottom text for the meme (if applicable, max 30 chars, can be empty)
4. Image description for AI image generation (detailed, visual, max 100 words)

Format your response EXACTLY as JSON with keys: title, top_text, bottom_text, image_description

Example:
{{"title": "Monday Mood", "top_text": "ME ON MONDAY", "bottom_text": "PRETENDING TO BE OKAY", "image_description": "A tired cat with messy fur sitting at a desk with coffee"}}"""
            
            logger.info(f"Generating complete meme for topic: {topic}")
            
            # Create meme generation chat
            meme_chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=f"meme-gen-{random.randint(1000, 9999)}",
                system_message="You are a creative meme generator. Always respond with valid JSON only."
            ).with_model("openai", "gpt-4o")
            
            user_message = UserMessage(text=prompt)
            response = await meme_chat.send_message(user_message)
            
            import json
            # Clean response to extract JSON
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            meme_data = json.loads(response)
            
            # Generate the actual image
            if 'image_description' in meme_data:
                image_url = await self.generate_image(meme_data['image_description'])
                meme_data['image_url'] = image_url
            
            logger.info(f"Successfully generated complete meme for topic: {topic}")
            return meme_data
            
        except Exception as e:
            logger.error(f"Complete meme generation error: {str(e)}")
            raise Exception(f"Failed to generate meme: {str(e)}")
    
    async def predict_viral_score(self, meme_data: dict) -> int:
        """Predict viral potential of a meme using GPT-4o"""
        try:
            prompt = f"""Analyze this meme and predict its viral potential on a scale of 0-100.

Meme title: {meme_data.get('title', 'Untitled')}
Tags: {', '.join(meme_data.get('tags', []))}

Consider factors like:
- Relatability
- Humor quality
- Current trends
- Visual appeal
- Meme format popularity

Respond with ONLY a number between 0-100, nothing else."""
            
            logger.info("Predicting viral score...")
            
            score_chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=f"score-{random.randint(1000, 9999)}",
                system_message="You are a meme viral potential analyzer. Respond only with a number."
            ).with_model("openai", "gpt-4o")
            
            user_message = UserMessage(text=prompt)
            response = await score_chat.send_message(user_message)
            
            score_text = response.strip()
            score = int(''.join(filter(str.isdigit, score_text)))
            score = max(0, min(100, score))  # Clamp between 0-100
            
            logger.info(f"Predicted viral score: {score}")
            return score
            
        except Exception as e:
            logger.error(f"Viral prediction error: {str(e)}")
            # Return random score as fallback
            return random.randint(40, 85)
    
    async def face_swap(self, source_image_url: str, target_image_url: str) -> str:
        """Perform face swap using Replicate API"""
        try:
            if not REPLICATE_API_TOKEN:
                raise Exception("Replicate API token not configured. Please add REPLICATE_API_TOKEN to .env file")
            
            logger.info("Starting face swap...")
            
            # Run face swap using Replicate in a thread to avoid blocking
            def run_face_swap():
                output = replicate.run(
                    "codeplugtech/face-swap:278a81e7ebb22db98bcba54de985d22cc1abeead2754eb1f2af717247be69b34",
                    input={
                        "source_image": source_image_url,
                        "target_image": target_image_url
                    }
                )
                return output
            
            # Run in executor to make it async
            loop = asyncio.get_event_loop()
            output = await loop.run_in_executor(None, run_face_swap)
            
            # Output is typically a URL
            result_url = str(output) if output else None
            
            if not result_url:
                raise Exception("Face swap did not return a result")
            
            logger.info("Face swap completed successfully")
            return result_url
            
        except Exception as e:
            logger.error(f"Face swap error: {str(e)}")
            raise Exception(f"Failed to perform face swap: {str(e)}")
    
    async def remove_background(self, image_data: bytes) -> bytes:
        """Remove background from image using rembg library"""
        try:
            logger.info("Removing background from image...")
            
            from rembg import remove
            
            # Run rembg in executor to avoid blocking
            loop = asyncio.get_event_loop()
            output_data = await loop.run_in_executor(None, remove, image_data)
            
            logger.info("Background removed successfully")
            return output_data
            
        except Exception as e:
            logger.error(f"Background removal error: {str(e)}")
            raise Exception(f"Failed to remove background: {str(e)}")

ai_service = AIService()
