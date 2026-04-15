"""
Memory Manager V2 - Sistema de Memoria Inteligente con Niveles
Implementa un sistema de memoria jerárquico con limpieza automática
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict


class MemoryLevel:
    """Niveles de importancia de la memoria"""
    CRITICAL = "critical"      # 🔴 Identidad, relaciones - Nunca se borra
    MEDIUM = "medium"          # 🟡 Preferencias frecuentes - Se limpia después de 30 días sin uso
    SHORT = "short"            # 🟢 Contexto de sesión - Se limpia después de 7 días


class IntelligentMemoryManager:
    """
    Gestor de memoria inteligente con niveles de importancia
    
    - 🔴 CRÍTICA: Identidad, relaciones (permanente)
    - 🟡 MEDIA: Preferencias, información frecuente (30 días)
    - 🟢 CORTA: Contexto temporal (7 días)
    
    Reglas:
    1. Solo guarda lo que se repite o es explícitamente importante
    2. Limpia automáticamente información obsoleta
    3. Prioriza calidad sobre cantidad
    """
    
    def __init__(self, memory_file: str = "memory/user_memory.json", 
                 conversations_file: str = "memory/conversations.json"):
        self.memory_file = memory_file
        self.conversations_file = conversations_file
        self.memory = self._load_memory()
        self.conversations = self._load_conversations()
        self.access_count = defaultdict(int)  # Contador de accesos
        
    def _get_default_memory(self) -> Dict:
        """Estructura por defecto con niveles"""
        return {
            "version": "2.0",
            "levels": {
                "critical": {
                    "identity": {
                        "name": None,
                        "age": None,
                        "city": None,
                        "profession": None
                    },
                    "relationships": []  # [{name, relation, context, first_mentioned, last_updated}]
                },
                "medium": {
                    "preferences": {},  # {key: {value, count, first_seen, last_accessed}}
                    "frequent_topics": {},  # {topic: {count, last_accessed}}
                    "important_facts": []  # [{fact, importance_score, first_seen, last_updated}]
                },
                "short": {
                    "session_context": {},  # Información de la sesión actual
                    "temporary_notes": []  # [{note, timestamp}]
                }
            },
            "metadata": {
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "last_cleanup": datetime.now().isoformat()
            }
        }
    
    def _load_memory(self) -> Dict:
        """Carga memoria desde archivo"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    memory = json.load(f)
                    # Migrar de versión antigua si es necesario
                    if memory.get("version") != "2.0":
                        return self._migrate_old_memory(memory)
                    return memory
            except Exception as e:
                print(f"Error cargando memoria: {e}")
                return self._get_default_memory()
        return self._get_default_memory()
    
    def _load_conversations(self) -> List[Dict]:
        """Carga historial de conversaciones"""
        if os.path.exists(self.conversations_file):
            try:
                with open(self.conversations_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _migrate_old_memory(self, old_memory: Dict) -> Dict:
        """Migra memoria de la versión anterior"""
        new_memory = self._get_default_memory()
        
        # Migrar identidad
        if "identity" in old_memory:
            for key, data in old_memory["identity"].items():
                if isinstance(data, dict) and data.get("value"):
                    new_memory["levels"]["critical"]["identity"][key] = data["value"]
        
        # Migrar relaciones
        if "relationships" in old_memory:
            for rel in old_memory["relationships"]:
                if isinstance(rel, dict):
                    name = rel.get("name", {}).get("value")
                    relation = rel.get("relation", {}).get("value")
                    if name and relation:
                        new_memory["levels"]["critical"]["relationships"].append({
                            "name": name,
                            "relation": relation,
                            "context": None,
                            "first_mentioned": datetime.now().isoformat(),
                            "last_updated": datetime.now().isoformat()
                        })
        
        # Migrar preferencias
        if "preferences" in old_memory:
            for key, data in old_memory["preferences"].items():
                if isinstance(data, dict) and data.get("value"):
                    new_memory["levels"]["medium"]["preferences"][key] = {
                        "value": data["value"],
                        "count": 1,
                        "first_seen": data.get("updated", datetime.now().isoformat()),
                        "last_accessed": datetime.now().isoformat()
                    }
        
        return new_memory
    
    def save_memory(self):
        """Guarda memoria en archivo"""
        try:
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            self.memory["metadata"]["last_updated"] = datetime.now().isoformat()
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando memoria: {e}")
    
    def save_conversations(self):
        """Guarda historial de conversaciones"""
        try:
            os.makedirs(os.path.dirname(self.conversations_file), exist_ok=True)
            with open(self.conversations_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversations, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando conversaciones: {e}")
    
    def update_memory(self, memory_update: Dict):
        """
        Actualiza memoria de forma inteligente
        
        Reglas:
        - Identidad y relaciones → CRÍTICA (permanente)
        - Preferencias repetidas → MEDIA (30 días)
        - Información temporal → CORTA (7 días)
        - No guarda basura semántica
        """
        if not memory_update or not isinstance(memory_update, dict):
            return
        
        timestamp = datetime.now().isoformat()
        
        # 🔴 MEMORIA CRÍTICA - Identidad
        if "identity" in memory_update and memory_update["identity"]:
            for key, value in memory_update["identity"].items():
                # Convertir a string si es necesario para validar
                if value is not None and str(value).strip():  # Solo si tiene contenido real
                    self.memory["levels"]["critical"]["identity"][key] = value
        
        # 🔴 MEMORIA CRÍTICA - Relaciones
        if "relationships" in memory_update and memory_update["relationships"]:
            for rel in memory_update["relationships"]:
                if not isinstance(rel, dict):
                    continue
                    
                name = rel.get("name")
                relation = rel.get("relation")
                
                if not name or not relation:
                    continue
                
                # Buscar si ya existe
                existing = next(
                    (r for r in self.memory["levels"]["critical"]["relationships"] 
                     if r["name"].lower() == name.lower()),
                    None
                )
                
                if existing:
                    existing["relation"] = relation
                    existing["last_updated"] = timestamp
                    if "context" in rel and rel["context"]:
                        existing["context"] = rel["context"]
                else:
                    self.memory["levels"]["critical"]["relationships"].append({
                        "name": name,
                        "relation": relation,
                        "context": rel.get("context"),
                        "first_mentioned": timestamp,
                        "last_updated": timestamp
                    })
        
        # 🟡 MEMORIA MEDIA - Preferencias
        if "preferences" in memory_update and memory_update["preferences"]:
            for key, value in memory_update["preferences"].items():
                if not value or not str(value).strip():
                    continue
                
                prefs = self.memory["levels"]["medium"]["preferences"]
                
                if key in prefs:
                    # Ya existe - incrementar contador y actualizar
                    prefs[key]["count"] += 1
                    prefs[key]["last_accessed"] = timestamp
                    if prefs[key]["value"] != value:
                        prefs[key]["value"] = value
                else:
                    # Nueva preferencia
                    prefs[key] = {
                        "value": value,
                        "count": 1,
                        "first_seen": timestamp,
                        "last_accessed": timestamp
                    }
        
        self.save_memory()
    
    def _is_semantic_garbage(self, content: str, role: str) -> bool:
        """
        Detecta si un mensaje es basura semántica que no vale la pena guardar
        
        Args:
            content: Contenido del mensaje
            role: "user" o "assistant"
            
        Returns:
            True si es basura semántica, False si vale la pena guardarlo
        """
        if not content or len(content.strip()) == 0:
            return True
        
        content_lower = content.lower().strip()
        
        # Lista de basura semántica común
        garbage_phrases = [
            # Cortesía simple
            "ok", "okay", "vale", "bien", "gracias", "de nada", "por favor",
            "hola", "adiós", "chao", "bye", "hasta luego",
            
            # Confirmaciones vacías
            "sí", "si", "no", "claro", "perfecto", "entendido", "de acuerdo",
            
            # Respuestas del asistente genéricas
            "¿en qué puedo ayudarle?", "¿necesita algo más?",
            "¿puedo ayudarle con algo más?",
            
            # Comandos muy cortos (se guardan las acciones, no los comandos)
            "abre chrome", "abre youtube", "busca", "pon música"
        ]
        
        # Si el mensaje es exactamente una frase de basura
        if content_lower in garbage_phrases:
            return True
        
        # Si es muy corto (menos de 10 caracteres) y no tiene información útil
        if len(content_lower) < 10:
            # Excepto si es del usuario y contiene información (nombre, edad, etc.)
            if role == "user":
                useful_keywords = ["llamo", "nombre", "edad", "vivo", "ciudad", "madre", "padre", "hermano"]
                if any(kw in content_lower for kw in useful_keywords):
                    return False
            return True
        
        # Si es solo puntuación o caracteres especiales
        if all(c in ".,;:!?¿¡-_()[]{}" for c in content if not c.isspace()):
            return True
        
        # Respuestas del asistente que solo confirman acciones sin contenido
        if role == "assistant":
            action_only_patterns = [
                "abriendo", "buscando", "consultando", "enviando mensaje",
                "reproduciendo", "ejecutando"
            ]
            # Si es solo confirmación de acción sin información adicional
            if any(pattern in content_lower for pattern in action_only_patterns):
                # Y es corto (menos de 50 caracteres)
                if len(content) < 50:
                    return True
        
        return False
    
    def add_conversation(self, role: str, content: str):
        """
        Agrega conversación al historial, filtrando basura semántica
        
        Args:
            role: "user" o "assistant"
            content: Contenido del mensaje
        """
        # Filtrar basura semántica
        if self._is_semantic_garbage(content, role):
            return  # No guardar
        
        self.conversations.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Mantener solo últimas 50 conversaciones
        self.conversations = self.conversations[-50:]
        self.save_conversations()
    
    def clean_garbage_conversations(self) -> int:
        """
        Limpia conversaciones que son basura semántica del historial existente
        
        Returns:
            Número de conversaciones eliminadas
        """
        if not self.conversations:
            return 0
        
        original_count = len(self.conversations)
        
        # Filtrar conversaciones válidas
        self.conversations = [
            conv for conv in self.conversations
            if not self._is_semantic_garbage(conv.get("content", ""), conv.get("role", ""))
        ]
        
        cleaned_count = original_count - len(self.conversations)
        
        if cleaned_count > 0:
            self.save_conversations()
            print(f"🧹 Limpiadas {cleaned_count} conversaciones de basura semántica")
        
        return cleaned_count
    
    def cleanup_old_data(self):
        """
        Limpia datos obsoletos basándose en niveles:
        - 🔴 CRÍTICA: Nunca se limpia
        - 🟡 MEDIA: Limpia después de 30 días sin uso
        - 🟢 CORTA: Limpia después de 7 días
        - 🧹 Limpia basura semántica de conversaciones
        """
        now = datetime.now()
        
        # Primero limpiar basura semántica de conversaciones
        garbage_cleaned = self.clean_garbage_conversations()
        
        # 🟡 Limpiar preferencias sin uso reciente
        medium_prefs = self.memory["levels"]["medium"]["preferences"]
        keys_to_remove = []
        
        for key, data in medium_prefs.items():
            last_access = datetime.fromisoformat(data["last_accessed"])
            days_inactive = (now - last_access).days
            
            # Si no se ha usado en 30 días y solo se mencionó una vez
            if days_inactive > 30 and data["count"] == 1:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del medium_prefs[key]
        
        # 🟡 Limpiar temas frecuentes antiguos
        topics = self.memory["levels"]["medium"]["frequent_topics"]
        topics_to_remove = []
        
        for topic, data in topics.items():
            last_access = datetime.fromisoformat(data["last_accessed"])
            days_inactive = (now - last_access).days
            
            if days_inactive > 30:
                topics_to_remove.append(topic)
        
        for topic in topics_to_remove:
            del topics[topic]
        
        # 🟢 Limpiar notas temporales
        temp_notes = self.memory["levels"]["short"]["temporary_notes"]
        self.memory["levels"]["short"]["temporary_notes"] = [
            note for note in temp_notes
            if (now - datetime.fromisoformat(note["timestamp"])).days <= 7
        ]
        
        # Limpiar conversaciones antiguas (más de 50)
        self.conversations = self.conversations[-50:]
        
        # Actualizar metadata
        self.memory["metadata"]["last_cleanup"] = now.isoformat()
        
        self.save_memory()
        self.save_conversations()
        
        if keys_to_remove or topics_to_remove:
            print(f"🧹 Limpieza automática: {len(keys_to_remove)} preferencias, {len(topics_to_remove)} temas eliminados")
    
    def get_memory_context(self, include_conversations: bool = True) -> str:
        """
        Obtiene contexto de memoria para el LLM
        Prioriza información crítica y relevante
        """
        context_parts = []
        
        # 🔴 CRÍTICA - Identidad
        identity = self.memory["levels"]["critical"]["identity"]
        id_info = []
        for key, value in identity.items():
            if value:
                id_info.append(f"{key}: {value}")
        
        if id_info:
            context_parts.append(f"👤 Usuario: {', '.join(id_info)}")
        
        # 🔴 CRÍTICA - Relaciones
        relationships = self.memory["levels"]["critical"]["relationships"]
        if relationships:
            rel_info = [f"{r['name']} ({r['relation']})" for r in relationships]
            context_parts.append(f"👥 Relaciones: {', '.join(rel_info)}")
        
        # 🟡 MEDIA - Preferencias (solo las más frecuentes)
        prefs = self.memory["levels"]["medium"]["preferences"]
        freq_prefs = sorted(
            [(k, v) for k, v in prefs.items()],
            key=lambda x: x[1]["count"],
            reverse=True
        )[:5]  # Solo top 5
        
        if freq_prefs:
            pref_info = [f"{k}: {v['value']}" for k, v in freq_prefs]
            context_parts.append(f"⭐ Preferencias: {', '.join(pref_info)}")
        
        # 🟢 CORTA - Conversación reciente (últimas 5)
        if include_conversations:
            recent = self.conversations[-5:]
            if recent:
                conv_info = [f"{c['role']}: {c['content'][:80]}..." for c in recent]
                context_parts.append(f"💬 Conversación reciente:\n" + "\n".join(conv_info))
        
        return "\n\n".join(context_parts) if context_parts else "Sin memoria previa."
    
    def get_memory(self) -> Dict:
        """Obtiene memoria completa"""
        return self.memory
    
    def clear_memory(self, level: Optional[str] = None):
        """
        Limpia memoria
        
        Args:
            level: "short", "medium", "critical", o None para todo
        """
        if level == "short":
            self.memory["levels"]["short"] = self._get_default_memory()["levels"]["short"]
        elif level == "medium":
            self.memory["levels"]["medium"] = self._get_default_memory()["levels"]["medium"]
        elif level == "critical":
            # Advertencia: esto borra identidad y relaciones
            self.memory["levels"]["critical"] = self._get_default_memory()["levels"]["critical"]
        else:
            # Limpia todo
            self.memory = self._get_default_memory()
            self.conversations = []
        
        self.save_memory()
        self.save_conversations()
    
    def get_statistics(self) -> Dict:
        """Obtiene estadísticas de la memoria"""
        return {
            "identity_fields": sum(1 for v in self.memory["levels"]["critical"]["identity"].values() if v),
            "relationships": len(self.memory["levels"]["critical"]["relationships"]),
            "preferences": len(self.memory["levels"]["medium"]["preferences"]),
            "frequent_topics": len(self.memory["levels"]["medium"]["frequent_topics"]),
            "temp_notes": len(self.memory["levels"]["short"]["temporary_notes"]),
            "conversations": len(self.conversations),
            "last_cleanup": self.memory["metadata"]["last_cleanup"]
        }


# Mantener compatibilidad con código existente
class MemoryManager(IntelligentMemoryManager):
    """Alias para compatibilidad"""
    pass
