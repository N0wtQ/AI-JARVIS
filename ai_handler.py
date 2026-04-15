"""
AI Handler
Handles communication with AI APIs with intent parsing and memory support
"""

import os
import re
import json
import requests
import time
from typing import List, Dict, Optional, Any
from memory.memory_manager_v2 import MemoryManager

# Google Gemini (nueva librería)
try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from rag_knowledge import get_knowledge_base
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False


class AIHandler:
    def __init__(self):
        # Support multiple API keys separated by commas
        api_keys_str = os.getenv("API_KEY", "")
        self.api_keys = [k.strip() for k in api_keys_str.split(",") if k.strip()]
        self.current_key_index = 0
        self.api_key = self.api_keys[0] if self.api_keys else None
        
        self.api_provider = os.getenv("API_PROVIDER", "openai")  # openai, groq, anthropic
        self.model = os.getenv("MODEL", "gpt-3.5-turbo")
        self.api_url = self._get_api_url()
        
        # Initialize memory manager
        self.memory_manager = MemoryManager()
        
        # Initialize knowledge base (RAG)
        self.knowledge_base = get_knowledge_base() if RAG_AVAILABLE else None
        
        # Conversation history (short-term)
        self.conversation_history: List[Dict] = []
        
        # Store last RAG sources for traceability
        self.last_rag_sources: List[Dict] = []
        
        # Pending action awaiting confirmation
        self.pending_action: Optional[Dict] = None
        
        # Load system prompt from file
        self.system_prompt = self._load_system_prompt()
        
        if len(self.api_keys) > 1:
            print(f"🔑 {len(self.api_keys)} API keys cargadas para rotación")
    
    def _rotate_api_key(self):
        """Rotate to the next API key"""
        if len(self.api_keys) > 1:
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
            self.api_key = self.api_keys[self.current_key_index]
            print(f"🔄 Rotando a API key {self.current_key_index + 1}/{len(self.api_keys)}")
            return True
        return False
        
    def _load_system_prompt(self) -> str:
        """Load system prompt from core/prompt.txt"""
        prompt_path = "core/prompt.txt"
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Warning: Could not load prompt from {prompt_path}: {e}")
            return self._get_fallback_prompt()
            
    def _get_fallback_prompt(self) -> str:
        """Fallback prompt if file not found"""
        return """Eres JARVIS, un asistente IA. Responde siempre en JSON con este formato:
{
  "intent": "chat",
  "parameters": {},
  "needs_clarification": false,
  "text": "tu respuesta aquí",
  "memory_update": {}
}"""
        
    def _get_api_url(self):
        """Get API URL based on provider"""
        urls = {
            "openai": "https://api.openai.com/v1/chat/completions",
            "groq": "https://api.groq.com/openai/v1/chat/completions",
            "anthropic": "https://api.anthropic.com/v1/messages",
            "gemini": "https://generativelanguage.googleapis.com/v1beta/models"
        }
        return urls.get(self.api_provider, urls["openai"])
    
    def _parse_json_response(self, content: str) -> Dict:
        """Parse JSON from LLM response, handling various formats"""
        # Try direct JSON parse first
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        
        # Try to extract JSON from markdown code blocks
        json_patterns = [
            r'```json\s*([\s\S]*?)\s*```',
            r'```\s*([\s\S]*?)\s*```',
            r'\{[\s\S]*\}'
        ]
        
        for pattern in json_patterns:
            match = re.search(pattern, content)
            if match:
                try:
                    json_str = match.group(1) if '```' in pattern else match.group(0)
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    continue
        
        # If all parsing fails, return a chat response with the raw text
        return {
            "intent": "chat",
            "parameters": {},
            "needs_clarification": False,
            "text": content,
            "memory_update": {}
        }
        
    def get_response(self, user_message: str) -> Dict[str, Any]:
        """
        Get response from AI with intent parsing
        
        Returns:
            Dict with keys: intent, parameters, needs_clarification, text, memory_update
        """
        if not self.api_key:
            return {
                "intent": "chat",
                "parameters": {},
                "needs_clarification": False,
                "text": "Error: API key no encontrada. Configura API_KEY en el archivo .env",
                "memory_update": {}
            }
        
        # Get memory context
        memory_context = self.memory_manager.get_memory_context()
        
        # Get RAG context with sources if available
        rag_context = ""
        self.last_rag_sources = []  # Reset sources
        
        if self.knowledge_base and RAG_AVAILABLE:
            rag_context, self.last_rag_sources = self.knowledge_base.get_context_with_sources(
                user_message, max_tokens=400
            )
        
        # Build enhanced message with all context
        context_parts = []
        
        if memory_context:
            context_parts.append(f"MEMORIA DEL USUARIO:\n{memory_context}")
        
        if rag_context:
            context_parts.append(f"DOCUMENTOS RELEVANTES:\n{rag_context}")
        
        context_parts.append(f"MENSAJE DEL USUARIO:\n{user_message}")
        
        enhanced_message = "\n\n".join(context_parts)
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": enhanced_message
        })
        
        try:
            if self.api_provider == "anthropic":
                raw_response = self._get_anthropic_response()
            elif self.api_provider == "gemini":
                raw_response = self._get_gemini_response()
            else:
                raw_response = self._get_openai_compatible_response()
            
            # Parse JSON response
            parsed = self._parse_json_response(raw_response)
            
            # Add RAG sources to response for traceability
            if self.last_rag_sources:
                parsed["rag_sources"] = self.last_rag_sources
            
            # Update memory if needed
            if parsed.get("memory_update"):
                self.memory_manager.update_memory(parsed["memory_update"])
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": raw_response
            })
            
            # Save conversation to memory
            self.memory_manager.add_conversation("user", user_message)
            self.memory_manager.add_conversation("assistant", parsed.get("text", raw_response))
            
            # Keep only last 10 messages in short-term history
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            return parsed
            
        except Exception as e:
            return {
                "intent": "chat",
                "parameters": {},
                "needs_clarification": False,
                "text": f"Error comunicando con la IA: {str(e)}",
                "memory_update": {}
            }
    
    def get_simple_response(self, user_message: str) -> str:
        """Get just the text response (for backward compatibility)"""
        result = self.get_response(user_message)
        return result.get("text", "Sin respuesta")
            
    def _get_openai_compatible_response(self) -> str:
        """Get response from OpenAI-compatible API (OpenAI, Groq, etc.) with retry and key rotation"""
        messages = [{"role": "system", "content": self.system_prompt}] + self.conversation_history
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        # Try with all available keys
        keys_tried = 0
        max_keys_to_try = len(self.api_keys) if self.api_keys else 1
        
        while keys_tried < max_keys_to_try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Retry logic for each key
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
                    response.raise_for_status()
                    
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                    
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 429:  # Rate limit
                        if attempt < max_retries - 1:
                            # Short wait before retry
                            time.sleep(1)
                            continue
                        else:
                            # Try next API key
                            if self._rotate_api_key():
                                keys_tried += 1
                                break  # Try with new key
                            else:
                                raise Exception("Límite de solicitudes excedido. Espera un momento.")
                    else:
                        raise
            else:
                # If we finished retries without breaking, increment keys_tried
                keys_tried += 1
        
        raise Exception("Todas las API keys han alcanzado el límite. Espera un momento.")
        
    def _get_anthropic_response(self) -> str:
        """Get response from Anthropic API"""
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "max_tokens": 1000,
            "system": self.system_prompt,
            "messages": self.conversation_history
        }
        
        response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result["content"][0]["text"]
    
    def _get_gemini_response(self) -> str:
        """Get response from Google Gemini API using official library (google-genai)"""
        if not GEMINI_AVAILABLE:
            raise Exception("Librería google-genai no instalada. Ejecuta: pip install google-genai")
        
        # Create client
        client = genai.Client(api_key=self.api_key)
        
        # Build contents with conversation history
        contents = []
        
        # Add system prompt as first user message context
        contents.append({
            "role": "user",
            "parts": [{"text": f"[SYSTEM INSTRUCTIONS]\n{self.system_prompt}\n[END SYSTEM INSTRUCTIONS]"}]
        })
        contents.append({
            "role": "model",
            "parts": [{"text": "Entendido. Seguiré las instrucciones del sistema."}]
        })
        
        # Add conversation history
        for msg in self.conversation_history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
        
        # Generate response
        response = client.models.generate_content(
            model=self.model,
            contents=contents
        )
        
        return response.text
        
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        
    def clear_memory(self):
        """Clear persistent memory"""
        self.memory_manager.clear_memory()
        
    def get_memory(self) -> Dict:
        """Get current memory state"""
        return self.memory_manager.get_memory()
        
    def reload_prompt(self):
        """Reload system prompt from file"""
        self.system_prompt = self._load_system_prompt()
