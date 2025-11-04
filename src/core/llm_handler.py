from langchain_perplexity import ChatPerplexity
from langchain_core.messages import HumanMessage
import os
import logging
from config.settings import settings

logger = logging.getLogger(__name__)


class PerplexityLLM:
    """Perplexity LLM Handler"""
    
    def __init__(self):
        try:
            # Get API key from environment
            api_key = os.getenv("PERPLEXITY_API_KEY") or settings.PERPLEXITY_API_KEY
            
            if not api_key or api_key == "None":
                logger.error("❌ PERPLEXITY_API_KEY not set in .env")
                self.llm = None
                return
            
            # Initialize Perplexity - use 'model' not 'model_name'
            self.llm = ChatPerplexity(
                api_key=api_key,
                model="sonar",  # ✅ FIXED: use 'model' not 'model_name'
                temperature=0.7,
                max_tokens=1000
            )
            
            logger.info("✅ Perplexity LLM initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Perplexity: {e}")
            self.llm = None
    
    def generate_response(self, query: str, context: list = None) -> str:
        """Generate response using Perplexity"""
        
        try:
            if not self.llm:
                logger.error("❌ Perplexity LLM not initialized - check .env file")
                return "Error: LLM not initialized. Set PERPLEXITY_API_KEY in .env"
            
            # Build prompt with context
            if context and len(context) > 0:
                context_text = ""
                for i, doc in enumerate(context[:3]):
                    if isinstance(doc, str):
                        context_text += f"\n{i+1}. {doc}"
                    else:
                        context_text += f"\n{i+1}. {str(doc)}"
                
                prompt = f"""Based on the following context, answer the question:

CONTEXT:{context_text}

QUESTION: {query}

ANSWER:"""
            else:
                prompt = query
            
            # Generate response
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            logger.info("✅ Response generated successfully")
            return response.content
            
        except Exception as e:
            logger.error(f"❌ Error generating response: {e}", exc_info=True)
            return f"Error: {str(e)[:200]}"
    
    def is_initialized(self) -> bool:
        """Check if LLM is initialized"""
        return self.llm is not None