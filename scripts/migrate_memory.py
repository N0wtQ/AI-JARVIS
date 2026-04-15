"""
Script de Migración de Memoria
Migra memory.json al nuevo formato con limpieza de basura semántica
"""

import json
import os
from memory.memory_manager_v2 import MemoryManager


def migrate_old_memory():
    """Migra la memoria antigua al nuevo sistema con limpieza"""
    
    old_file = "memory/memory.json"
    
    if not os.path.exists(old_file):
        print("❌ No se encontró memory.json para migrar")
        return
    
    print("\n" + "="*60)
    print("MIGRACIÓN DE MEMORIA A NUEVO FORMATO".center(60))
    print("="*60 + "\n")
    
    # Cargar memoria antigua
    try:
        with open(old_file, 'r', encoding='utf-8') as f:
            old_memory = json.load(f)
    except Exception as e:
        print(f"❌ Error leyendo {old_file}: {e}")
        return
    
    # Crear manager nuevo
    manager = MemoryManager()
    
    print("📋 MIGRACIÓN DE DATOS:\n")
    
    # 1. Migrar identidad
    identity_count = 0
    if "identity" in old_memory:
        for key, data in old_memory["identity"].items():
            if isinstance(data, dict) and data.get("value"):
                manager.memory["levels"]["critical"]["identity"][key] = data["value"]
                identity_count += 1
                print(f"  ✅ Identidad: {key} = {data['value']}")
    
    # 2. Migrar relaciones
    relationships_count = 0
    if "relationships" in old_memory:
        for rel in old_memory["relationships"]:
            if isinstance(rel, dict):
                name = rel.get("name", {}).get("value")
                relation = rel.get("relation", {}).get("value")
                if name and relation:
                    manager.memory["levels"]["critical"]["relationships"].append({
                        "name": name,
                        "relation": relation,
                        "context": None,
                        "first_mentioned": rel.get("name", {}).get("updated", ""),
                        "last_updated": rel.get("name", {}).get("updated", "")
                    })
                    relationships_count += 1
                    print(f"  ✅ Relación: {name} ({relation})")
    
    # 3. Migrar preferencias
    preferences_count = 0
    if "preferences" in old_memory:
        for key, data in old_memory["preferences"].items():
            if isinstance(data, dict) and data.get("value"):
                manager.memory["levels"]["medium"]["preferences"][key] = {
                    "value": data["value"],
                    "count": 1,
                    "first_seen": data.get("updated", ""),
                    "last_accessed": data.get("updated", "")
                }
                preferences_count += 1
                print(f"  ✅ Preferencia: {key} = {data['value']}")
    
    print(f"\n📊 RESUMEN DE MIGRACIÓN:")
    print(f"  - Identidad: {identity_count} campos")
    print(f"  - Relaciones: {relationships_count}")
    print(f"  - Preferencias: {preferences_count}")
    
    # 4. Migrar conversaciones (CON FILTRADO)
    print(f"\n💬 MIGRACIÓN DE CONVERSACIONES:\n")
    
    old_conversations = old_memory.get("conversation_history", [])
    print(f"  Total en memory.json: {len(old_conversations)}")
    
    # Agregar conversaciones con filtrado automático
    for conv in old_conversations:
        manager.add_conversation(
            role=conv.get("role", ""),
            content=conv.get("content", "")
        )
    
    new_count = len(manager.conversations)
    filtered_count = len(old_conversations) - new_count
    
    print(f"  Después del filtrado: {new_count}")
    print(f"  🧹 Basura eliminada: {filtered_count}")
    
    if filtered_count > 0:
        percentage = (filtered_count * 100) // len(old_conversations)
        print(f"  📊 Reducción: {percentage}%")
    
    # Guardar nueva memoria
    manager.save_memory()
    manager.save_conversations()
    
    print(f"\n✅ MIGRACIÓN COMPLETADA")
    print(f"\n📁 ARCHIVOS:")
    print(f"  ✅ memory/user_memory.json (nuevo formato)")
    print(f"  ✅ memory/conversations.json (limpio)")
    
    # Preguntar si eliminar antiguo
    print(f"\n⚠️  ¿Deseas eliminar memory.json antiguo?")
    print(f"   Se creará un respaldo como memory.json.backup")
    confirm = input("Escribe 'si' para confirmar: ")
    
    if confirm.lower() == 'si':
        # Crear backup
        backup_file = old_file + ".backup"
        try:
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(old_memory, f, indent=2, ensure_ascii=False)
            
            # Eliminar original
            os.remove(old_file)
            
            print(f"\n✅ memory.json eliminado")
            print(f"✅ Respaldo creado: {backup_file}")
        except Exception as e:
            print(f"\n❌ Error creando backup: {e}")
    else:
        print(f"\n📝 memory.json conservado (puedes eliminarlo manualmente)")
    
    print("\n" + "="*60)
    print("MIGRACIÓN FINALIZADA".center(60))
    print("="*60)
    
    # Mostrar estadísticas finales
    print(f"\n📊 ESTADÍSTICAS FINALES:")
    stats = manager.get_statistics()
    print(f"  🔴 Identidad: {stats['identity_fields']} campos")
    print(f"  🔴 Relaciones: {stats['relationships']}")
    print(f"  🟡 Preferencias: {stats['preferences']}")
    print(f"  💬 Conversaciones: {stats['conversations']} (sin basura)")
    
    print(f"\n✨ Tu memoria ahora está limpia y optimizada!")


if __name__ == "__main__":
    migrate_old_memory()
