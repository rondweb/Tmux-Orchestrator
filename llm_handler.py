#!/usr/bin/env python3

import os
import sys
import yaml
import json
import requests
from typing import Dict, Any, Optional

class LLMHandler:
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the LLM handler with configuration."""
        self.config = self._load_config(config_path)
        self.active_model = self.config.get('active_model', 'litellm')
        self.api_key = os.getenv('LLM_API_KEY', self.config.get('api_key', ''))
        self.model_name = self.config.get('model_name', 'gpt-3.5-turbo')
        self.base_url = self.config.get('base_url', '')
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file) or {}
        except FileNotFoundError:
            print(f"Warning: Config file {config_path} not found. Using defaults.")
            return {}
        except yaml.YAMLError as e:
            print(f"Error parsing config file: {e}")
            return {}
    
    def send_message(self, agent_name: str, prompt: str) -> str:
        """Main function to send message to the configured LLM."""
        if not self.api_key or self.api_key == 'YOUR_API_KEY':
            return "Error: API key not configured. Please set LLM_API_KEY environment variable."
        
        try:
            if self.active_model == 'litellm':
                return self._send_litellm_message(prompt)
            elif self.active_model == 'gemini':
                return self._send_gemini_message(prompt)
            elif self.active_model == 'qwen':
                return self._send_qwen_message(prompt)
            elif self.active_model == 'claude':
                return self._send_claude_message(prompt)
            else:
                return f"Error: Unsupported model '{self.active_model}'"
        except Exception as e:
            return f"Error communicating with LLM: {str(e)}"
    
    def _send_litellm_message(self, prompt: str) -> str:
        """Send message using LiteLLM (unified interface)."""
        try:
            import litellm
            
            # Configure LiteLLM
            if self.base_url:
                litellm.api_base = self.base_url
            
            response = litellm.completion(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                api_key=self.api_key
            )
            
            return response.choices[0].message.content
        except ImportError:
            return "Error: LiteLLM not installed. Run: pip install litellm"
        except Exception as e:
            return f"LiteLLM Error: {str(e)}"
    
    def _send_gemini_message(self, prompt: str) -> str:
        """Send message to Google Gemini API."""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            
            return response.text
        except ImportError:
            return "Error: Google Generative AI not installed. Run: pip install google-generativeai"
        except Exception as e:
            return f"Gemini Error: {str(e)}"
    
    def _send_qwen_message(self, prompt: str) -> str:
        """Send message to Qwen API."""
        url = self.base_url or "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model_name,
            "input": {
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            return result["output"]["text"]
        except requests.RequestException as e:
            return f"Qwen API Error: {str(e)}"
        except KeyError as e:
            return f"Qwen Response Error: Missing key {str(e)}"
    
    def _send_claude_message(self, prompt: str) -> str:
        """Send message to Claude API (Anthropic)."""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.api_key)
            
            response = client.messages.create(
                model=self.model_name,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
        except ImportError:
            return "Error: Anthropic not installed. Run: pip install anthropic"
        except Exception as e:
            return f"Claude Error: {str(e)}"

def main():
    """Command line interface for the LLM handler."""
    if len(sys.argv) < 3:
        print("Usage: python llm_handler.py <agent_name> <prompt>")
        sys.exit(1)
    
    agent_name = sys.argv[1]
    prompt = " ".join(sys.argv[2:])
    
    handler = LLMHandler()
    response = handler.send_message(agent_name, prompt)
    print(response)

if __name__ == "__main__":
    main()

