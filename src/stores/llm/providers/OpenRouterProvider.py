from ..LLMInterface import LLMInterface
from ..LLMEnums import OpenRouterEnums, DocumentTypeEnum
import requests
import logging


class OpenRouterProvider(LLMInterface):
    """OpenRouter LLM Provider - supports various free and paid models"""
    
    BASE_URL = "https://openrouter.ai/api/v1"
    
    def __init__(self, api_key: str, 
            default_input_max_characters: int = 4000,
            default_generation_max_output_tokens: int = 2000,
            default_generation_temperature: float = 0.7,
            site_url: str = "http://localhost:8000",
            site_name: str = "RAG Application"):
        
        self.api_key = api_key
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature
        self.site_url = site_url
        self.site_name = site_name
        
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None
        
        self.enums = OpenRouterEnums
        self.logger = logging.getLogger(__name__)
    
    def set_generation_model(self, model_id: str):
        """Set the generation model"""
        self.generation_model_id = model_id
        self.logger.info(f"OpenRouter generation model set to: {model_id}")
    
    def set_embedding_model(self, model_id: str, embedding_size: int):
        """Set the embedding model - Note: OpenRouter doesn't support embeddings directly"""
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
        self.logger.warning("OpenRouter doesn't support embeddings. Using Gemini for embeddings.")
    
    def process_text(self, text: str):
        """Process and trim text to max characters"""
        return text[:self.default_input_max_characters].strip()
    
    def generate_text(self, prompt: str, chat_history: list = [], max_output_tokens: int = None,
                        temperature: float = None):
        """Generate text using OpenRouter API"""
        
        if not self.api_key:
            self.logger.error("OpenRouter API key was not set")
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model for OpenRouter was not set")
            return None

        max_output_tokens = max_output_tokens or self.default_generation_max_output_tokens
        temperature = temperature or self.default_generation_temperature

        try:
            # Build messages array
            messages = []
            
            # Add chat history
            if chat_history:
                for msg in chat_history:
                    role = msg.get("role", "user")
                    content = msg.get("content") or msg.get("text") or ""
                    
                    # Map roles to OpenRouter format
                    if role == OpenRouterEnums.SYSTEM.value:
                        openrouter_role = "system"
                    elif role == OpenRouterEnums.ASSISTANT.value:
                        openrouter_role = "assistant"
                    else:
                        openrouter_role = "user"
                    
                    if content.strip():
                        messages.append({
                            "role": openrouter_role,
                            "content": content
                        })
            
            # Add the current prompt
            messages.append({
                "role": "user",
                "content": self.process_text(prompt)
            })

            # Make API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": self.site_url,
                "X-Title": self.site_name
            }
            
            payload = {
                "model": self.generation_model_id,
                "messages": messages,
                "max_tokens": max_output_tokens,
                "temperature": temperature
            }
            
            response = requests.post(
                f"{self.BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code != 200:
                error_msg = f"OpenRouter API error: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
            
            result = response.json()
            
            # Extract generated text
            if "choices" in result and len(result["choices"]) > 0:
                generated_text = result["choices"][0].get("message", {}).get("content", "")
                return generated_text.strip() if generated_text else None
            
            self.logger.error("No choices in OpenRouter response")
            raise Exception("OpenRouter returned no choices in response")

        except requests.exceptions.Timeout:
            error_msg = "OpenRouter API request timed out after 60 seconds"
            self.logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            self.logger.error(f"Error in OpenRouter generate_text: {str(e)}")
            raise

    def embed_text(self, text: str, document_type: str = None):
        """
        OpenRouter doesn't support embeddings directly.
        This method should not be called - use a separate embedding provider.
        """
        self.logger.error("OpenRouter does not support embeddings. Use Gemini or another embedding provider.")
        return None
    
    def construct_prompt(self, prompt: str, role: str):
        """Build a message in OpenRouter/OpenAI format"""
        # Map roles
        if role == OpenRouterEnums.SYSTEM.value:
            openrouter_role = "system"
        elif role == OpenRouterEnums.ASSISTANT.value:
            openrouter_role = "assistant"
        else:
            openrouter_role = "user"
        
        return {
            "role": openrouter_role,
            "content": self.process_text(prompt)
        }
