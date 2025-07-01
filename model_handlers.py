"""
Custom Model Handlers for specialized LLM functionality

This module provides optional custom handlers for specific model types
and advanced features like document processing and multimodal inputs.
"""

import os
import json
import base64
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import logging

try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    from PIL import Image
    import PyPDF2
    HAS_EXTRAS = True
except ImportError:
    HAS_EXTRAS = False
    print("Warning: Some optional dependencies not available. Advanced features disabled.")

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Handles document processing for context augmentation"""
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from PDF file"""
        if not HAS_EXTRAS:
            return "PDF processing not available - missing dependencies"
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            logger.error(f"PDF extraction error: {str(e)}")
            return f"Error extracting PDF: {str(e)}"
    
    @staticmethod
    def extract_text_from_image(file_path: str) -> str:
        """Extract text from image using OCR (placeholder)"""
        # This would require OCR libraries like pytesseract
        # For now, return image metadata
        try:
            if HAS_EXTRAS:
                with Image.open(file_path) as img:
                    return f"Image: {img.format}, Size: {img.size}, Mode: {img.mode}"
            else:
                return "Image processing not available"
        except Exception as e:
            return f"Error processing image: {str(e)}"
    
    @staticmethod
    def process_uploaded_file(file_path: str, file_type: str) -> str:
        """Process uploaded file based on type"""
        try:
            if file_type.lower() == 'pdf':
                return DocumentProcessor.extract_text_from_pdf(file_path)
            elif file_type.lower() in ['jpg', 'jpeg', 'png', 'gif']:
                return DocumentProcessor.extract_text_from_image(file_path)
            elif file_type.lower() in ['txt', 'md']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                return f"Unsupported file type: {file_type}"
        except Exception as e:
            logger.error(f"File processing error: {str(e)}")
            return f"Error processing file: {str(e)}"

class SpecializedModelHandlers:
    """Handlers for specialized model types"""
    
    @staticmethod
    def handle_code_model(model_name: str, prompt: str, **kwargs) -> str:
        """Handle code generation models with special formatting"""
        if 'codegen' in model_name.lower() or 'code' in model_name.lower():
            # Add code-specific prompt formatting
            formatted_prompt = f"```\n{prompt}\n```\nComplete the code:"
            return formatted_prompt
        return prompt
    
    @staticmethod
    def handle_chat_model(model_name: str, messages: List[Dict], **kwargs) -> str:
        """Handle chat models with conversation history"""
        if 'chat' in model_name.lower() or 'instruct' in model_name.lower():
            # Format as conversation
            formatted_prompt = ""
            for msg in messages:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                if role == 'user':
                    formatted_prompt += f"Human: {content}\n"
                elif role == 'assistant':
                    formatted_prompt += f"Assistant: {content}\n"
            formatted_prompt += "Assistant: "
            return formatted_prompt
        return messages[-1].get('content', '') if messages else ""
    
    @staticmethod
    def handle_multimodal_model(model_name: str, prompt: str, images: List[str] = None, **kwargs) -> str:
        """Handle multimodal models with image inputs"""
        if images and ('vision' in model_name.lower() or 'multimodal' in model_name.lower()):
            # Add image descriptions to prompt
            image_context = "\nImages provided:\n"
            for i, img_path in enumerate(images):
                image_context += f"Image {i+1}: {img_path}\n"
            return prompt + image_context
        return prompt

class ModelOptimizer:
    """Optimizations for different model types"""
    
    @staticmethod
    def get_optimal_parameters(model_name: str, task_type: str = 'chat') -> Dict[str, Any]:
        """Get optimal parameters for specific models and tasks"""
        
        # Default parameters
        params = {
            'temperature': 0.7,
            'top_p': 0.9,
            'max_tokens': 512,
            'repetition_penalty': 1.1,
            'do_sample': True
        }
        
        # Model-specific optimizations
        if 'gpt' in model_name.lower():
            if task_type == 'code':
                params.update({'temperature': 0.2, 'top_p': 0.95})
            elif task_type == 'creative':
                params.update({'temperature': 0.9, 'top_p': 0.9})
        
        elif 'llama' in model_name.lower():
            params.update({'repetition_penalty': 1.05})
            if '7b' in model_name.lower():
                params.update({'max_tokens': 256})  # Smaller context for efficiency
        
        elif 'flan' in model_name.lower():
            params.update({'temperature': 0.3, 'top_p': 0.95})  # More focused for instruction following
        
        elif 'phi' in model_name.lower():
            params.update({'temperature': 0.6, 'max_tokens': 384})
        
        return params
    
    @staticmethod
    def estimate_memory_usage(model_name: str) -> Dict[str, str]:
        """Estimate memory requirements for models"""
        
        # Rough estimates based on model size
        if '70b' in model_name.lower():
            return {'ram': '~140GB', 'vram': '~80GB', 'recommendation': 'Use quantization'}
        elif '13b' in model_name.lower():
            return {'ram': '~26GB', 'vram': '~15GB', 'recommendation': 'Consider 8-bit loading'}
        elif '7b' in model_name.lower():
            return {'ram': '~14GB', 'vram': '~8GB', 'recommendation': 'Should run well'}
        elif '3b' in model_name.lower():
            return {'ram': '~6GB', 'vram': '~4GB', 'recommendation': 'Efficient for most systems'}
        elif '1b' in model_name.lower() or 'small' in model_name.lower():
            return {'ram': '~2GB', 'vram': '~1GB', 'recommendation': 'Very efficient'}
        else:
            return {'ram': 'Unknown', 'vram': 'Unknown', 'recommendation': 'Check model documentation'}

class AdvancedFeatures:
    """Advanced features for enhanced AI capabilities"""
    
    @staticmethod
    def create_context_from_files(file_paths: List[str]) -> str:
        """Create rich context from multiple uploaded files"""
        context = "Document Context:\n"
        
        for file_path in file_paths:
            try:
                file_extension = Path(file_path).suffix.lower().lstrip('.')
                content = DocumentProcessor.process_uploaded_file(file_path, file_extension)
                filename = Path(file_path).name
                context += f"\n--- {filename} ---\n{content}\n"
            except Exception as e:
                context += f"\n--- {Path(file_path).name} ---\nError: {str(e)}\n"
        
        return context
    
    @staticmethod
    def enhance_prompt_with_research(prompt: str, research_results: List[Dict]) -> str:
        """Enhance prompt with research context"""
        if not research_results:
            return prompt
        
        enhanced = f"Research Context:\n"
        for result in research_results[:3]:  # Limit to top 3 results
            enhanced += f"- {result.get('title', 'Unknown')}: {result.get('content', '')[:200]}...\n"
        
        enhanced += f"\nUser Query: {prompt}\n\nPlease provide a comprehensive response using the above context when relevant:"
        return enhanced
    
    @staticmethod
    def generate_suggested_prompts(conversation_history: List[Dict]) -> List[str]:
        """Generate suggested follow-up prompts based on conversation"""
        if not conversation_history:
            return [
                "Tell me about artificial intelligence",
                "Help me write some code",
                "Explain a complex topic simply",
                "What's new in technology?"
            ]
        
        last_message = conversation_history[-1].get('content', '').lower()
        
        # Simple heuristic-based suggestions
        if 'code' in last_message or 'program' in last_message:
            return [
                "Can you optimize this code?",
                "Add error handling to this",
                "Explain how this works",
                "Convert this to another language"
            ]
        elif 'explain' in last_message or 'what' in last_message:
            return [
                "Can you give an example?",
                "What are the pros and cons?",
                "Tell me more about this topic",
                "How does this relate to other concepts?"
            ]
        else:
            return [
                "Can you elaborate on that?",
                "What are the practical applications?",
                "Are there alternatives to consider?",
                "Can you provide more details?"
            ]

# Export main classes for use in the extension
__all__ = [
    'DocumentProcessor',
    'SpecializedModelHandlers', 
    'ModelOptimizer',
    'AdvancedFeatures'
] 