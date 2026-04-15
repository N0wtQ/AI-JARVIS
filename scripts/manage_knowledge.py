"""
Knowledge Base Management Tool
Use this to index, search, and manage your documents
"""

import sys
from rag_knowledge import get_knowledge_base


def main():
    kb = get_knowledge_base()
    
    if len(sys.argv) < 2:
        print("""
🧠 Gestor de Base de Conocimiento de JARVIS

Uso:
  python manage_knowledge.py index          - Indexar documentos en knowledge/
  python manage_knowledge.py reindex        - Reindexar todos los documentos
  python manage_knowledge.py stats          - Ver estadísticas
  python manage_knowledge.py search <query> - Buscar en la base de conocimiento
  python manage_knowledge.py add <file>     - Agregar un documento específico

Archivos soportados: .txt, .md, .json, .py, .csv
        """)
        return
    
    command = sys.argv[1].lower()
    
    if command == "index":
        kb.index_documents(force_reindex=False)
        kb.stats()
        
    elif command == "reindex":
        kb.index_documents(force_reindex=True)
        kb.stats()
        
    elif command == "stats":
        kb.stats()
        
    elif command == "search":
        if len(sys.argv) < 3:
            print("❌ Proporciona una consulta de búsqueda")
            return
        
        query = ' '.join(sys.argv[2:])
        print(f"\n🔍 Buscando: {query}\n")
        
        results = kb.search(query, top_k=5)
        
        if not results:
            print("❌ No se encontraron resultados")
            return
        
        for i, result in enumerate(results, 1):
            print(f"{i}. [{result['file']}] (similitud: {result['similarity']:.2%})")
            print(f"   {result['content'][:200]}...")
            print()
            
    elif command == "add":
        if len(sys.argv) < 3:
            print("❌ Proporciona la ruta del archivo")
            return
        
        file_path = sys.argv[2]
        kb.add_document(file_path)
        kb.stats()
        
    else:
        print(f"❌ Comando desconocido: {command}")


if __name__ == "__main__":
    main()
