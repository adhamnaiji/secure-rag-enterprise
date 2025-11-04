from langchain_perplexity import ChatPerplexity
from langchain_core.messages import HumanMessage
from config.settings import settings
from typing import List
import logging

logger = logging.getLogger(__name__)

class PerplexityLLM:
    """Handle Perplexity LLM integration"""
    
    def __init__(self):
        try:
            self.llm = ChatPerplexity(
                api_key=settings.PERPLEXITY_API_KEY,
                model=settings.PERPLEXITY_MODEL,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS
            )
            logger.info("Perplexity LLM initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Perplexity LLM: {e}")
            self.llm = None
    
    def generate_response(self, query: str, context: List[str] = None) -> str:
        """Generate response using Perplexity"""
        try:
            if not self.llm:
                return "LLM not initialized. Check API key."
            
            context = context or []
            context_str = "\n".join(context) if context else "No context available"
            
            prompt = f"""Based on the following context, answer the user's query:

Context:
{context_str}

Query: {query}

Answer:"""
            
            message = HumanMessage(content=prompt)
            response = self.llm.invoke([message])
            return response.content
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error: {str(e)}"
