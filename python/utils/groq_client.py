"""
Free Cloud LLM Client using Groq API
Alternative to Ollama for quick setup - completely free, no installation
Get API key from: https://console.groq.com/keys (takes 30 seconds)
"""
import requests
import json
import os
from typing import Dict, List
from python.utils.helpers import get_logger

logger = get_logger(__name__)


class GroqLLM:
    """
    Groq API client - FREE cloud LLM (no installation needed)
    Models available: llama3-8b, llama3-70b, mixtral-8x7b
    """
    
    def __init__(self, api_key: str = None, model: str = "llama-3.3-70b-versatile"):
        """
        Initialize Groq client
        
        Args:
            api_key: Groq API key (get free from https://console.groq.com/keys)
            model: Model to use (llama-3.3-70b-versatile is fast and free)
        """
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        if not self.api_key:
            logger.warning("No GROQ_API_KEY found. Get one from: https://console.groq.com/keys")
        
        self.model = model
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
    
    def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.7, 
                 max_tokens: int = 2000) -> str:
        """
        Generate text using Groq
        
        Args:
            prompt: User prompt
            system_prompt: System instructions
            temperature: Creativity level (0-1)
            max_tokens: Maximum response length
        
        Returns:
            Generated text response
        """
        if not self.api_key:
            return "Error: No API key configured. Set GROQ_API_KEY in .env"
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            logger.info(f"Sending request to Groq: {self.model}")
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
            
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Groq API. Check internet connection.")
            return "Error: Cannot connect to Groq API"
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                logger.error("Invalid Groq API key")
                return "Error: Invalid API key. Get one from https://console.groq.com/keys"
            else:
                logger.error(f"Groq API error: {e}")
                return f"Error: {e}"
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            return f"Error: {str(e)}"
    
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """
        Chat completion using Groq
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Creativity level
        
        Returns:
            Assistant's response
        """
        if not self.api_key:
            return "Error: No API key configured"
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
            
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            return f"Error: {str(e)}"


def test_groq_connection():
    """Test if Groq API is accessible"""
    try:
        llm = GroqLLM()
        
        if not llm.api_key:
            print("=" * 60)
            print("⚠️  NO GROQ API KEY FOUND")
            print("=" * 60)
            print("\n📝 Get a FREE API key (takes 30 seconds):")
            print("   1. Visit: https://console.groq.com/keys")
            print("   2. Sign up (free, no credit card)")
            print("   3. Create API key")
            print("   4. Add to .env file:")
            print("      GROQ_API_KEY=your_key_here")
            print("\n💡 Groq is 100% FREE with generous limits:")
            print("   - No installation needed")
            print("   - Extremely fast responses")
            print("   - Llama3, Mixtral models available")
            print("=" * 60)
            return False
        
        response = llm.generate("Say 'OK' if you can read this.", temperature=0)
        
        if response and 'Error' not in response:
            print("=" * 60)
            print("✅ GROQ API CONNECTION SUCCESSFUL")
            print("=" * 60)
            print(f"Model: {llm.model}")
            print(f"Response: {response}")
            print("\n🚀 AI features are now ENABLED!")
            print("=" * 60)
            return True
        else:
            print(f"❌ Groq returned an error: {response}")
            return False
            
    except Exception as e:
        print(f"❌ Cannot connect to Groq: {str(e)}")
        return False


if __name__ == '__main__':
    test_groq_connection()
