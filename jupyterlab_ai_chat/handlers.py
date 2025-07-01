"""
JupyterLab AI Chat Server Handlers

This module provides handlers for AI chat requests with local LLM support.
"""

import os
import json
import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado
from tornado import web

try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    print("Warning: transformers not available. Some features may not work.")

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("Warning: requests not available. Deep research mode disabled.")

# Configuration
MODEL_DIR = os.getenv('MODEL_DIR', '/mnt/sisplockers/models')
DEFAULT_MODEL = 'microsoft/DialoGPT-medium'
SEARCH_API_URL = "https://api.duckduckgo.com/"

logger = logging.getLogger(__name__)

class ModelManager:
    """Manages loading and inference for local LLM models"""
    
    def __init__(self):
        self.loaded_models = {}
        self.tokenizers = {}
        
    def get_available_models(self) -> List[str]:
        """Get list of available models from the models directory"""
        models = []
        
        if os.path.exists(MODEL_DIR) and os.access(MODEL_DIR, os.R_OK):
            try:
                for item in os.listdir(MODEL_DIR):
                    model_path = os.path.join(MODEL_DIR, item)
                    if os.path.isdir(model_path):
                        if (os.path.exists(os.path.join(model_path, 'config.json')) or
                            os.path.exists(os.path.join(model_path, 'pytorch_model.bin'))):
                            models.append(item)
            except PermissionError:
                logger.warning(f"Permission denied accessing {MODEL_DIR}")
        
        # Add fallback models
        fallback_models = [
            'microsoft/DialoGPT-medium',
            'microsoft/DialoGPT-small', 
            'gpt2',
            'distilgpt2'
        ]
        
        for model in fallback_models:
            if model not in models:
                models.append(model)
                
        return models
    
    def load_model(self, model_name: str):
        """Load a model and tokenizer"""
        if model_name in self.loaded_models:
            return self.loaded_models[model_name], self.tokenizers[model_name]
        
        try:
            model_path = os.path.join(MODEL_DIR, model_name)
            if os.path.exists(model_path):
                model_name = model_path
            
            tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side='left')
            
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                low_cpu_mem_usage=True
            )
            
            self.loaded_models[model_name] = model
            self.tokenizers[model_name] = tokenizer
            
            return model, tokenizer
            
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {str(e)}")
            raise tornado.web.HTTPError(500, f"Failed to load model: {str(e)}")
    
    def generate_response(
        self, 
        model_name: str, 
        prompt: str, 
        temperature: float = 0.7,
        top_p: float = 0.9, 
        max_tokens: int = 512
    ) -> str:
        """Generate response using the specified model"""
        try:
            model, tokenizer = self.load_model(model_name)
            
            inputs = tokenizer.encode(prompt, return_tensors='pt', padding=True, truncation=True)
            
            with torch.no_grad():
                outputs = model.generate(
                    inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id,
                    eos_token_id=tokenizer.eos_token_id
                )
            
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            if response.startswith(prompt):
                response = response[len(prompt):].strip()
            
            return response
            
        except Exception as e:
            logger.error(f"Generation error: {str(e)}")
            return f"Sorry, I encountered an error: {str(e)}"

class ResearchHelper:
    """Helper for internet research capabilities"""
    
    @staticmethod
    def search_web(query: str, max_results: int = 3) -> List[Dict[str, str]]:
        """Perform web search using DuckDuckGo API"""
        if not HAS_REQUESTS:
            return []
        
        try:
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = requests.get(SEARCH_API_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            if data.get('Abstract'):
                results.append({
                    'title': data.get('AbstractSource', 'Web Search'),
                    'content': data['Abstract'],
                    'url': data.get('AbstractURL', '')
                })
            
            for topic in data.get('RelatedTopics', [])[:max_results-1]:
                if isinstance(topic, dict) and topic.get('Text'):
                    results.append({
                        'title': topic.get('FirstURL', '').split('/')[-1] or 'Related',
                        'content': topic['Text'],
                        'url': topic.get('FirstURL', '')
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Web search error: {str(e)}")
            return []

# Initialize managers
model_manager = ModelManager()
research_helper = ResearchHelper()

class AIChatHandler(APIHandler):
    """Main API handler for AI chat requests"""
    
    @tornado.web.authenticated
    async def post(self):
        """Handle chat requests"""
        try:
            message = self.get_argument('message', '')
            model_name = self.get_argument('model', '')
            temperature = float(self.get_argument('temperature', '0.7'))
            top_p = float(self.get_argument('top_p', '0.9'))
            max_tokens = int(self.get_argument('max_tokens', '512'))
            deep_research = self.get_argument('deep_research', 'false').lower() == 'true'
            
            if not message:
                raise tornado.web.HTTPError(400, "Message is required")
            
            if not model_name:
                available_models = model_manager.get_available_models()
                model_name = available_models[0] if available_models else DEFAULT_MODEL
            
            enhanced_prompt = message
            research_context = ""
            
            if deep_research and HAS_REQUESTS:
                search_results = research_helper.search_web(message)
                if search_results:
                    research_context = "\n\nRecent information:\n"
                    for result in search_results:
                        research_context += f"- {result['title']}: {result['content']}\n"
                    
                    enhanced_prompt = f"Context: {research_context}\n\nUser question: {message}\n\nResponse:"
            
            if HAS_TRANSFORMERS:
                response = model_manager.generate_response(
                    model_name=model_name,
                    prompt=enhanced_prompt,
                    temperature=temperature,
                    top_p=top_p,
                    max_tokens=max_tokens
                )
            else:
                response = f"Model response simulation for: {message}"
                if research_context:
                    response += f"\n\n(Enhanced with research: {research_context[:100]}...)"
            
            self.finish(json.dumps({
                'response': response,
                'model': model_name,
                'research_used': bool(research_context)
            }))
            
        except Exception as e:
            logger.error(f"Chat handler error: {str(e)}")
            self.set_status(500)
            self.finish(json.dumps({'error': str(e)}))

class ModelsHandler(APIHandler):
    """Handler for retrieving available models"""
    
    @tornado.web.authenticated
    async def get(self):
        """Get list of available models"""
        try:
            models = model_manager.get_available_models()
            self.finish(json.dumps(models))
        except Exception as e:
            logger.error(f"Models handler error: {str(e)}")
            self.set_status(500)
            self.finish(json.dumps({'error': str(e)}))

def setup_handlers(server_app):
    """Setup the handlers for the server extension"""
    web_app = server_app.web_app
    host_pattern = '.*$'
    
    route_pattern = url_path_join(web_app.settings['base_url'], '/aichat/chat')
    web_app.add_handlers(host_pattern, [(route_pattern, AIChatHandler)])
    
    route_pattern = url_path_join(web_app.settings['base_url'], '/aichat/models')
    web_app.add_handlers(host_pattern, [(route_pattern, ModelsHandler)])
    
    logger.info("AI Chat server extension loaded") 