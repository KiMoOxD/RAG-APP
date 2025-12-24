from ..LLMInterface import LLMInterface
from ..LLMEnums import GeminiEnums, DocumentTypeEnum
import google.generativeai as genai
import logging

class GeminiProvider(LLMInterface):
    
    def __init__(self, api_key: str, 
            default_input_max_characters: int = 4000,
            default_generation_max_output_tokens: int = 2000,
            default_generation_temperature: float = 0.7):
        
        self.api_key = api_key
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature
        
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None
        
        # تكوين عميل Gemini
        genai.configure(api_key=self.api_key)
        self.client = genai
        
        self.client.safety_settings = {
            "HARASSMENT": "BLOCK_NONE",
            "HATE_SPEECH": "BLOCK_NONE",
            "SEXUAL": "BLOCK_NONE",
            "DANGEROUS": "BLOCK_NONE",
            "VIOLENCE": "BLOCK_NONE"
        }
        
        self.enums =  GeminiEnums
        self.logger = logging.getLogger(__name__)
    
    def set_generation_model(self, model_id: str):
        """تعيين نموذج توليد النص"""
        self.generation_model_id = model_id
    
    def set_embedding_model(self, model_id: str, embedding_size: int):
        """تعيين نموذج التضمين"""
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
    
    def process_text(self, text: str):
        """معالجة النص واقتصاصه للحد الأقصى"""
        return text[:self.default_input_max_characters].strip()
    
    def generate_text(self, prompt: str, chat_history: list = [], max_output_tokens: int = None,
                        temperature: float = None):
        """توليد النص باستخدام Gemini"""

        if not self.client:
            self.logger.error("Gemini client was not set")
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model for Gemini was not set")
            return None

        max_output_tokens = max_output_tokens or self.default_generation_max_output_tokens
        temperature = temperature or self.default_generation_temperature

        try:
            model = self.client.GenerativeModel(self.generation_model_id)

            generation_config = {
                "max_output_tokens": max_output_tokens,
                "temperature": temperature
            }

            # تجهيز تاريخ المحادثة
            history = []
            if chat_history:
                for msg in chat_history:
                    role = "user" if msg.get("role") == GeminiEnums.USER.value else "model"
                    content = msg.get("content") or msg.get("text") or ""
                    if content.strip():
                        history.append({"role": role, "parts": [content]})

            # إرسال الطلب
            if history:
                chat = model.start_chat(history=history)
                response = chat.send_message(self.process_text(prompt), generation_config=generation_config)
            else:
                response = model.generate_content(self.process_text(prompt), generation_config=generation_config)

            # التأكد من finish_reason
            candidate = response.candidates[0] if response.candidates else None
            if candidate and hasattr(candidate, "finish_reason"):
                if candidate.finish_reason != 1:  # 1 = SUCCESS
                    self.logger.error(f"Generation blocked. Finish reason: {candidate.finish_reason}")
                    return "The model could not generate a response due to safety filters."

            # استخراج النص بأمان
            if not response:
                self.logger.error("Gemini returned no response object")
                return None

            if not hasattr(response, "candidates") or not response.candidates:
                self.logger.error("Gemini returned no candidates")
                return None

            parts = response.candidates[0].content.parts
            if not parts:
                self.logger.error("No content parts found in Gemini response")
                return None

            # تجميع النص من كل Part
            generated_text = "".join([p.text for p in parts if hasattr(p, "text")])

            return generated_text.strip() or None

        except Exception as e:
            self.logger.error(f"Error in Gemini generate_text: {str(e)}")
            return None

    
    def embed_text(self, text: str, document_type: str = None):
        """إنشاء تضمين النص باستخدام Gemini"""
        if not self.client:
            self.logger.error("Gemini client was not set")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("Embedding model for Gemini was not set")
            return None
        
        try:
            # معالجة النص
            processed_text = self.process_text(text)
            
            # تحديد نوع المهمة للتضمين
            task_type = GeminiEnums.DOCUMENT.value
            if document_type == DocumentTypeEnum.QUERY.value:
                task_type = GeminiEnums.QUERY.value
            
            # إنشاء التضمين
            result = self.client.embed_content(
                model=self.embedding_model_id,
                content=processed_text,
                task_type=task_type
            )
            
            if not result or 'embedding' not in result or not result['embedding']:
                self.logger.error("Error while embedding text with Gemini")
                return None
            
            return result['embedding']
            
        except Exception as e:
            self.logger.error(f"Error in Gemini embed_text: {str(e)}")
            return None
    
    def construct_prompt(self, prompt: str, role: str):
        """بناء رسالة بتنسيق Gemini"""
        # تحويل الأدوار من تنسيق النظام إلى تنسيق Gemini
        if role == GeminiEnums.ASSISTANT.value:
            gemini_role = GeminiEnums.ASSISTANT.value
        else:
            gemini_role = GeminiEnums.USER.value
        
        return {
            "role": gemini_role,
            "content": self.process_text(prompt)
        }