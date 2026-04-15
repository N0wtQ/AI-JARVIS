"""
Memory Manager
Handles persistent memory storage for the AI assistant
"""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime


class MemoryManager:
    def __init__(self, memory_file: str = "memory/memory.json"):
        self.memory_file = memory_file
        self.memory = self._load_memory()
        
    def _get_default_memory(self) -> Dict:
        """Return default memory structure"""
        return {
            "identity": {
                "name": {"value": None, "updated": None},
                "age": {"value": None, "updated": None},
                "city": {"value": None, "updated": None}
            },
            "preferences": {
                "favorite_color": {"value": None, "updated": None},
                "favorite_food": {"value": None, "updated": None},
                "favorite_music": {"value": None, "updated": None}
            },
            "relationships": [],
            "emotional_state": [],
            "conversation_history": []
        }
        
    def _load_memory(self) -> Dict:
        """Load memory from JSON file"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading memory: {e}")
                return self._get_default_memory()
        return self._get_default_memory()
        
    def save_memory(self):
        """Save memory to JSON file"""
        try:
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving memory: {e}")
            
    def update_memory(self, memory_update: Dict):
        """Update memory with new information"""
        if not memory_update:
            return
            
        timestamp = datetime.now().isoformat()
        
        # Update identity
        if "identity" in memory_update and memory_update["identity"]:
            for key, value in memory_update["identity"].items():
                if value:
                    self.memory["identity"][key] = {
                        "value": value,
                        "updated": timestamp
                    }
                    
        # Update preferences
        if "preferences" in memory_update and memory_update["preferences"]:
            for key, value in memory_update["preferences"].items():
                if value:
                    self.memory["preferences"][key] = {
                        "value": value,
                        "updated": timestamp
                    }
                    
        # Update relationships
        if "relationships" in memory_update and memory_update["relationships"]:
            for rel in memory_update["relationships"]:
                if rel:
                    existing = next(
                        (r for r in self.memory["relationships"] 
                         if r.get("name", {}).get("value") == rel.get("name")),
                        None
                    )
                    if existing:
                        existing.update({
                            "name": {"value": rel.get("name"), "updated": timestamp},
                            "relation": {"value": rel.get("relation"), "updated": timestamp}
                        })
                    else:
                        self.memory["relationships"].append({
                            "name": {"value": rel.get("name"), "updated": timestamp},
                            "relation": {"value": rel.get("relation"), "updated": timestamp}
                        })
                        
        # Update emotional state
        if "emotional_state" in memory_update and memory_update["emotional_state"]:
            self.memory["emotional_state"].append({
                "value": memory_update["emotional_state"],
                "timestamp": timestamp
            })
            # Keep only last 10 emotional states
            self.memory["emotional_state"] = self.memory["emotional_state"][-10:]
            
        self.save_memory()
        
    def add_conversation(self, role: str, content: str):
        """Add a conversation entry to history"""
        self.memory["conversation_history"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        # Keep only last 50 conversations
        self.memory["conversation_history"] = self.memory["conversation_history"][-50:]
        self.save_memory()
        
    def get_memory_context(self) -> str:
        """Get memory as context string for the LLM"""
        context_parts = []
        
        # Identity
        identity = self.memory.get("identity", {})
        identity_info = []
        for key, data in identity.items():
            if data.get("value"):
                identity_info.append(f"{key}: {data['value']}")
        if identity_info:
            context_parts.append(f"Usuario: {', '.join(identity_info)}")
            
        # Preferences
        prefs = self.memory.get("preferences", {})
        pref_info = []
        for key, data in prefs.items():
            if data.get("value"):
                pref_info.append(f"{key}: {data['value']}")
        if pref_info:
            context_parts.append(f"Preferencias: {', '.join(pref_info)}")
            
        # Relationships
        rels = self.memory.get("relationships", [])
        if rels:
            rel_info = [f"{r.get('name', {}).get('value', '?')} ({r.get('relation', {}).get('value', '?')})" 
                       for r in rels if r.get('name', {}).get('value')]
            if rel_info:
                context_parts.append(f"Relaciones: {', '.join(rel_info)}")
                
        # Recent conversation (last 5)
        history = self.memory.get("conversation_history", [])[-5:]
        if history:
            recent = [f"{h['role']}: {h['content'][:100]}" for h in history]
            context_parts.append(f"Conversación reciente:\n" + "\n".join(recent))
            
        return "\n".join(context_parts) if context_parts else "Sin memoria previa."
        
    def get_memory(self) -> Dict:
        """Get full memory dict"""
        return self.memory
        
    def clear_memory(self):
        """Clear all memory"""
        self.memory = self._get_default_memory()
        self.save_memory()
