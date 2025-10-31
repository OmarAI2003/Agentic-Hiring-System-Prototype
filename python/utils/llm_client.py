"""
Ollama LLM Integration for Agentic AI Decision Making
Uses local Llama 3 model via Ollama (completely free)
"""
import requests
import json
from typing import Dict, List
from python.utils.helpers import get_logger, ConfigManager, log_decision

logger = get_logger(__name__)


class OllamaLLM:
    """
    Wrapper for Ollama API to interact with local LLM
    """
    
    def __init__(self, model: str = None, host: str = None):
        config = ConfigManager.get_ollama_config()
        self.model = model or config['model']
        self.host = host or config['host']
        self.api_url = f"{self.host}/api/generate"
        self.chat_url = f"{self.host}/api/chat"
    
    def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.7, 
                 max_tokens: int = 2000) -> str:
        """
        Generate text using Ollama
        
        Args:
            prompt: User prompt
            system_prompt: System instructions
            temperature: Creativity level (0-1)
            max_tokens: Maximum response length
        
        Returns:
            Generated text response
        """
        try:
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "temperature": temperature,
                "stream": False,
                "options": {
                    "num_predict": max_tokens
                }
            }
            
            logger.info(f"Sending request to Ollama: {self.model}")
            response = requests.post(self.api_url, json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '').strip()
            
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out")
            return "Error: Request timed out. Ensure Ollama is running."
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama. Is it running?")
            return "Error: Cannot connect to Ollama. Please start Ollama service."
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            return f"Error: {str(e)}"
    
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """
        Chat completion using Ollama
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Creativity level
        
        Returns:
            Assistant's response
        """
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "stream": False
            }
            
            response = requests.post(self.chat_url, json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            return result.get('message', {}).get('content', '').strip()
            
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            return f"Error: {str(e)}"
    
    def analyze_with_context(self, context: str, question: str, 
                            system_role: str = "You are an expert HR recruitment AI assistant.") -> str:
        """
        Analyze information with given context
        
        Args:
            context: Background information
            question: Question to answer
            system_role: System role description
        
        Returns:
            Analysis result
        """
        messages = [
            {"role": "system", "content": system_role},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{question}"}
        ]
        return self.chat(messages)
    
    def make_decision(self, decision_context: Dict, module: str) -> Dict:
        """
        Make an agentic AI decision based on context
        
        Args:
            decision_context: Dictionary with decision-making context
            module: Module name for logging
        
        Returns:
            Decision result as dictionary
        """
        system_prompt = """You are an autonomous AI recruitment agent. 
        Make intelligent, data-driven decisions based on the context provided.
        Always respond in valid JSON format with your decision and reasoning."""
        
        context_str = json.dumps(decision_context, indent=2)
        prompt = f"""Based on the following context, make a decision and explain your reasoning.

Context:
{context_str}

Provide your response in the following JSON format:
{{
    "decision": "your decision here",
    "reasoning": "explanation of your reasoning",
    "confidence": 0.85,
    "factors_considered": ["factor1", "factor2"]
}}
"""
        
        response = self.generate(prompt, system_prompt, temperature=0.3)
        
        try:
            # Try to parse as JSON
            decision = json.loads(response)
            log_decision(module, decision.get('decision', 'Unknown'), {
                'reasoning': decision.get('reasoning'),
                'confidence': decision.get('confidence'),
                'context': decision_context
            })
            return decision
        except json.JSONDecodeError:
            logger.warning("Could not parse LLM response as JSON, using text response")
            log_decision(module, response[:100], {'full_response': response})
            return {
                'decision': response,
                'reasoning': 'Raw LLM response',
                'confidence': 0.5
            }


class AgenticDecisionMaker:
    """
    High-level agentic AI decision-making interface
    """
    
    def __init__(self):
        self.llm = OllamaLLM()
    
    def decide_ranking_weights(self, job_details: Dict) -> Dict[str, float]:
        """
        Autonomously decide how to weight different factors in candidate ranking
        based on job characteristics
        
        Args:
            job_details: Job information
        
        Returns:
            Dictionary of weights for different ranking factors
        """
        decision_context = {
            "task": "determine_ranking_weights",
            "job_title": job_details.get('title'),
            "experience_level": job_details.get('experience_level'),
            "required_skills": job_details.get('required_skills', []),
            "department": job_details.get('department')
        }
        
        prompt = f"""You are analyzing a job posting to determine how to weight different factors when ranking candidates.

Job Details:
- Title: {job_details.get('title')}
- Experience Level: {job_details.get('experience_level')}
- Skills: {', '.join(job_details.get('required_skills', [])[:5])}
- Department: {job_details.get('department')}

Determine the optimal weights (0.0 to 1.0) for these factors. Weights should sum to 1.0:
- skills_match: How important is skills alignment?
- experience_match: How important is years of experience?
- location_match: How important is location proximity?
- education_match: How important is educational background?

Respond ONLY with valid JSON:
{{
    "skills_match": 0.4,
    "experience_match": 0.3,
    "location_match": 0.2,
    "education_match": 0.1,
    "reasoning": "Explanation of weight choices"
}}
"""
        
        response = self.llm.generate(prompt, temperature=0.3)
        
        try:
            weights = json.loads(response)
            log_decision('candidate_sourcing', 
                        f"Determined ranking weights for {job_details.get('title')}", 
                        weights)
            return weights
        except Exception as e:
            # Fallback to balanced weights
            logger.warning(f"Using default weights due to parsing error: {str(e)}")
            return {
                'skills_match': 0.40,
                'experience_match': 0.30,
                'location_match': 0.15,
                'education_match': 0.15,
                'reasoning': 'Default balanced weights'
            }
    
    def assess_candidate_fit(self, candidate: Dict, job: Dict) -> Dict:
        """
        Holistically assess candidate-job fit
        
        Args:
            candidate: Candidate information
            job: Job information
        
        Returns:
            Assessment result with reasoning
        """
        prompt = f"""Assess the overall fit between this candidate and job:

Job: {job.get('title')} - {job.get('experience_level')} level
Required Skills: {', '.join(job.get('required_skills', [])[:10])}

Candidate: {candidate.get('full_name')}
Skills: {', '.join(candidate.get('skills', [])[:10])}
Experience: {candidate.get('experience_years')} years
Current Role: {candidate.get('current_position')}

Provide assessment in JSON:
{{
    "overall_fit": "excellent|good|fair|poor",
    "score": 0.85,
    "key_strengths": ["strength1", "strength2"],
    "key_concerns": ["concern1"],
    "recommendation": "Interview|Screen Further|Reject",
    "reasoning": "Brief explanation"
}}
"""
        
        response = self.llm.generate(prompt, temperature=0.3)
        
        try:
            assessment = json.loads(response)
            return assessment
        except Exception as e:
            logger.error(f"Error parsing assessment: {str(e)}")
            return {
                'overall_fit': 'unknown',
                'score': 0.5,
                'key_strengths': [],
                'key_concerns': ['Assessment error'],
                'recommendation': 'Screen Further',
                'reasoning': 'Error in assessment'
            }


def test_ollama_connection():
    """Test if Ollama is accessible"""
    try:
        llm = OllamaLLM()
        response = llm.generate("Hello, respond with 'OK' if you can read this.", temperature=0)
        if response and 'error' not in response.lower():
            print("✓ Ollama connection successful!")
            print(f"Response: {response[:100]}")
            return True
        else:
            print("✗ Ollama returned an error")
            return False
    except Exception as e:
        print(f"✗ Cannot connect to Ollama: {str(e)}")
        print("\nTo fix this:")
        print("1. Install Ollama from https://ollama.ai")
        print("2. Run: ollama pull llama3")
        print("3. Start Ollama service")
        return False


if __name__ == '__main__':
    test_ollama_connection()
