"""
Universal Free LLM Client - Works with multiple free AI providers
Priority: Groq > HuggingFace > Ollama (local)
"""
import os
import requests
from typing import Dict, Optional
import sys
sys.path.insert(0, '.')
from python.utils.helpers import get_logger

logger = get_logger(__name__)


class UniversalLLM:
    """
    Intelligent LLM client that tries multiple free providers
    Automatically falls back if one service is unavailable
    """
    
    def __init__(self):
        self.provider = None
        self.client = None
        self._initialize_best_provider()
    
    def _initialize_best_provider(self):
        """Try providers in order of preference"""
        
        # Try 1: Groq (fastest, free, no install)
        groq_key = os.getenv('GROQ_API_KEY')
        if groq_key:
            try:
                from python.utils.groq_client import GroqLLM
                self.client = GroqLLM(groq_key)
                # Quick test
                response = self.client.generate("Hi", temperature=0)
                if response and 'Error' not in response:
                    self.provider = 'groq'
                    logger.info("✅ Using Groq API")
                    return
            except Exception as e:
                logger.warning(f"Groq failed: {e}")
        
        # Try 2: HuggingFace (free, no install, slower)
        hf_token = os.getenv('HUGGINGFACE_TOKEN')
        if hf_token:
            try:
                self.client = HuggingFaceLLM(hf_token)
                self.provider = 'huggingface'
                logger.info("✅ Using HuggingFace API")
                return
            except Exception as e:
                logger.warning(f"HuggingFace failed: {e}")
        
        # Try 3: Ollama (local, requires install)
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                from python.utils.llm_client import OllamaLLM
                self.client = OllamaLLM()
                self.provider = 'ollama'
                logger.info("✅ Using local Ollama")
                return
        except:
            pass
        
        # No AI available - use fallback mode
        self.provider = 'fallback'
        logger.warning("⚠️ No AI provider available - using rule-based fallbacks")
        print("\n" + "=" * 60)
        print("⚠️  NO AI PROVIDER CONFIGURED")
        print("=" * 60)
        print("\nChoose ONE of these FREE options:")
        print("\n📌 Option 1: GROQ (Recommended - Fastest)")
        print("   1. Visit: https://console.groq.com/keys")
        print("   2. Sign up (30 seconds, no credit card)")
        print("   3. Create API key")
        print("   4. Add to .env:")
        print("      GROQ_API_KEY=your_key_here")
        print("\n📌 Option 2: HuggingFace (Good alternative)")
        print("   1. Visit: https://huggingface.co/settings/tokens")
        print("   2. Sign up and create token")
        print("   3. Add to .env:")
        print("      HUGGINGFACE_TOKEN=your_token_here")
        print("\n📌 Option 3: Ollama (Local, requires install)")
        print("   1. Download from: https://ollama.ai")
        print("   2. Run: ollama pull llama3.2:1b (small & fast)")
        print("   3. Ollama will auto-start")
        print("\n💡 System will work in FALLBACK MODE until AI configured")
        print("=" * 60 + "\n")
    
    def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.7, 
                 max_tokens: int = 2000) -> str:
        """Generate text using best available provider"""
        
        if self.provider == 'fallback':
            return "FALLBACK_MODE"  # Trigger fallback logic in calling code
        
        try:
            return self.client.generate(prompt, system_prompt, temperature, max_tokens)
        except Exception as e:
            logger.error(f"Error in {self.provider}: {e}")
            return "FALLBACK_MODE"
    
    def is_available(self) -> bool:
        """Check if any AI provider is available"""
        return self.provider != 'fallback'
    
    def get_provider_name(self) -> str:
        """Get current provider name"""
        return self.provider


class HuggingFaceLLM:
    """
    HuggingFace Inference API client - FREE (no installation)
    Using Llama or Mistral models
    """
    
    def __init__(self, token: str = None):
        self.token = token or os.getenv('HUGGINGFACE_TOKEN')
        self.model = "meta-llama/Llama-3.2-1B-Instruct"  # Fast, small model
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model}"
    
    def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.7, 
                 max_tokens: int = 2000) -> str:
        """Generate text using HuggingFace"""
        
        if not self.token:
            return "Error: No HuggingFace token configured"
        
        try:
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "inputs": full_prompt,
                "parameters": {
                    "temperature": temperature,
                    "max_new_tokens": max_tokens,
                    "return_full_text": False
                }
            }
            
            logger.info(f"Sending request to HuggingFace: {self.model}")
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', '').strip()
            return str(result)
            
        except Exception as e:
            logger.error(f"HuggingFace error: {e}")
            return f"Error: {e}"


def setup_quick_ai():
    """Interactive setup for quickest AI option"""
    print("\n" + "=" * 60)
    print("🚀 QUICK AI SETUP - Choose Fastest Option")
    print("=" * 60)
    
    print("\n📌 RECOMMENDED: Groq (Free, Fastest, No Install)")
    print("   Takes 30 seconds to set up")
    print("   1. Open: https://console.groq.com/keys")
    print("   2. Sign up with Google/GitHub")
    print("   3. Click 'Create API Key'")
    print("   4. Copy the key")
    print()
    
    choice = input("Do you want to set up Groq now? (y/n): ").strip().lower()
    
    if choice == 'y':
        print("\n✅ Opening Groq console in browser...")
        import webbrowser
        webbrowser.open("https://console.groq.com/keys")
        
        print("\n📋 After getting your API key:")
        api_key = input("Paste your Groq API key here: ").strip()
        
        if api_key:
            # Update .env file
            env_path = ".env"
            with open(env_path, 'a') as f:
                f.write(f"\n# Groq API (Free Cloud LLM)\nGROQ_API_KEY={api_key}\n")
            
            # Test connection
            os.environ['GROQ_API_KEY'] = api_key
            llm = UniversalLLM()
            
            if llm.is_available():
                print("\n" + "=" * 60)
                print("✅ SUCCESS! AI is now configured and working!")
                print("=" * 60)
                print(f"Provider: {llm.get_provider_name()}")
                print("\nYou can now run:")
                print("  python demo.py")
                print("=" * 60)
                return True
            else:
                print("\n❌ Setup failed. Please check your API key.")
                return False
    
    print("\n💡 No problem! System will use rule-based fallbacks.")
    print("   You can set up AI later by adding to .env:")
    print("   GROQ_API_KEY=your_key_here")
    return False


def test_universal_llm():
    """Test which AI provider is available"""
    llm = UniversalLLM()
    
    print("\n" + "=" * 60)
    print("AI PROVIDER STATUS")
    print("=" * 60)
    
    if llm.is_available():
        print(f"✅ Active Provider: {llm.get_provider_name().upper()}")
        print("\nTesting AI response...")
        response = llm.generate("Say 'Hello' if you can read this", temperature=0)
        print(f"Response: {response[:100]}")
        print("\n🎉 AI features are ENABLED!")
    else:
        print("⚠️  No AI provider available")
        print("   System running in FALLBACK MODE (rule-based)")
        print("\n   Set up AI quickly with: setup_quick_ai()")
    
    print("=" * 60)
    return llm.is_available()


if __name__ == '__main__':
    # First check what's available
    if not test_universal_llm():
        # If nothing available, offer quick setup
        setup_quick_ai()
