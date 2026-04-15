"""
Script de Limpieza Automática de Memoria
Ejecuta limpieza inteligente de memoria obsoleta
"""

from memory.memory_manager_v2 import MemoryManager
import argparse


def main():
    parser = argparse.ArgumentParser(description="Limpieza inteligente de memoria de JARVIS")
    parser.add_argument('--dry-run', action='store_true', 
                       help='Muestra qué se eliminaría sin hacerlo')
    parser.add_argument('--stats', action='store_true',
                       help='Muestra estadísticas de memoria')
    parser.add_argument('--clear', choices=['short', 'medium', 'critical', 'all'],
                       help='Limpia un nivel específico de memoria')
    parser.add_argument('--garbage', action='store_true',
                       help='Limpia solo basura semántica de conversaciones')
    
    args = parser.parse_args()
    
    manager = MemoryManager()
    
    if args.garbage:
        print("\n🧹 Limpiando basura semántica de conversaciones...")
        print("=" * 50)
        
        before = len(manager.conversations)
        cleaned = manager.clean_garbage_conversations()
        after = len(manager.conversations)
        
        print(f"\n📊 RESULTADOS:")
        print(f"  Conversaciones antes: {before}")
        print(f"  Conversaciones después: {after}")
        print(f"  Eliminadas: {cleaned}")
        
        if cleaned > 0:
            print(f"\n✅ Limpieza completada: {cleaned} conversaciones eliminadas")
        else:
            print(f"\n✅ No se encontró basura semántica")
        
        print("=" * 50)
        return
    
    if args.stats:
        print("\n📊 ESTADÍSTICAS DE MEMORIA")
        print("=" * 50)
        stats = manager.get_statistics()
        print(f"🔴 CRÍTICA:")
        print(f"  - Campos de identidad: {stats['identity_fields']}")
        print(f"  - Relaciones: {stats['relationships']}")
        print(f"\n🟡 MEDIA:")
        print(f"  - Preferencias: {stats['preferences']}")
        print(f"  - Temas frecuentes: {stats['frequent_topics']}")
        print(f"\n🟢 CORTA:")
        print(f"  - Notas temporales: {stats['temp_notes']}")
        print(f"  - Conversaciones: {stats['conversations']}")
        print(f"\n🧹 Última limpieza: {stats['last_cleanup']}")
        print("=" * 50)
        return
    
    if args.clear:
        level_names = {
            'short': '🟢 CORTA',
            'medium': '🟡 MEDIA', 
            'critical': '🔴 CRÍTICA',
            'all': 'TODA'
        }
        
        print(f"\n⚠️  ¿Estás seguro de que quieres limpiar la memoria {level_names[args.clear]}?")
        if args.clear == 'critical':
            print("   Esto borrará tu identidad y relaciones. Esta acción NO se puede deshacer.")
        elif args.clear == 'all':
            print("   Esto borrará TODA la memoria. Esta acción NO se puede deshacer.")
        
        confirm = input("Escribe 'si' para confirmar: ")
        
        if confirm.lower() == 'si':
            if args.clear == 'all':
                manager.clear_memory()
            else:
                manager.clear_memory(level=args.clear)
            print(f"✅ Memoria {level_names[args.clear]} limpiada")
        else:
            print("❌ Operación cancelada")
        return
    
    # Limpieza normal
    print("\n🧹 Iniciando limpieza automática de memoria...")
    print("=" * 50)
    
    before_stats = manager.get_statistics()
    
    if args.dry_run:
        print("⚠️  MODO DRY-RUN: Solo mostrando qué se eliminaría\n")
    else:
        manager.cleanup_old_data()
    
    after_stats = manager.get_statistics()
    
    print("\n📊 RESULTADOS:")
    print(f"🟡 Preferencias: {before_stats['preferences']} → {after_stats['preferences']}")
    print(f"🟡 Temas: {before_stats['frequent_topics']} → {after_stats['frequent_topics']}")
    print(f"🟢 Notas temporales: {before_stats['temp_notes']} → {after_stats['temp_notes']}")
    
    if not args.dry_run:
        print("\n✅ Limpieza completada")
        print("🔴 Memoria crítica (identidad y relaciones) conservada")
    
    print("=" * 50)


if __name__ == "__main__":
    main()
