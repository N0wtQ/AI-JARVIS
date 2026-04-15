"""
RAG Knowledge Base
Manages document embeddings and retrieval for JARVIS
"""

import os
import json
import pickle
from typing import List, Dict, Optional, Tuple
import numpy as np
from pathlib import Path
from datetime import datetime

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("⚠️ sentence-transformers no instalado. Instala con: pip install sentence-transformers")

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️ PyPDF2 no instalado. Instala con: pip install PyPDF2")


class KnowledgeBase:
    def __init__(self, knowledge_dir: str = "knowledge", cache_dir: str = "knowledge/.cache"):
        self.knowledge_dir = knowledge_dir
        self.cache_dir = cache_dir
        os.makedirs(self.knowledge_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Initialize embeddings model (lightweight)
        if EMBEDDINGS_AVAILABLE:
            self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        else:
            self.model = None
        
        # Load or create index
        self.documents = []
        self.embeddings = []
        self.index_file = os.path.join(self.cache_dir, "index.pkl")
        self.load_index()
    
    def load_index(self):
        """Load existing index from cache"""
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, 'rb') as f:
                    data = pickle.load(f)
                    self.documents = data.get('documents', [])
                    self.embeddings = data.get('embeddings', [])
                print(f"✅ Cargados {len(self.documents)} documentos del índice")
            except Exception as e:
                print(f"⚠️ Error cargando índice: {e}")
                self.documents = []
                self.embeddings = []
    
    def save_index(self):
        """Save index to cache"""
        try:
            with open(self.index_file, 'wb') as f:
                pickle.dump({
                    'documents': self.documents,
                    'embeddings': self.embeddings
                }, f)
        except Exception as e:
            print(f"⚠️ Error guardando índice: {e}")
    
    def read_file(self, file_path: str) -> str:
        """Read content from a file"""
        # Handle PDFs
        if file_path.lower().endswith('.pdf'):
            return self._read_pdf(file_path)
        
        # Handle text files
        try:
            # Try UTF-8 first
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Fallback to latin-1
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                print(f"⚠️ Error leyendo {file_path}: {e}")
                return ""
    
    def _read_pdf(self, file_path: str) -> str:
        """Read content from a PDF file"""
        if not PDF_AVAILABLE:
            print(f"⚠️ No se puede leer PDF sin PyPDF2: {file_path}")
            return ""
        
        try:
            text = []
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text.append(page_text)
                    except Exception as e:
                        print(f"⚠️ Error en página {page_num} de {os.path.basename(file_path)}: {e}")
            
            return "\n".join(text)
        except Exception as e:
            print(f"⚠️ Error leyendo PDF {file_path}: {e}")
            return ""
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)
        
        return chunks
    
    def index_documents(self, force_reindex: bool = False):
        """Index all documents in knowledge directory"""
        if not EMBEDDINGS_AVAILABLE:
            print("❌ No se puede indexar sin sentence-transformers")
            return
        
        # Check if reindex needed
        if not force_reindex and len(self.documents) > 0:
            print("📚 Índice existente encontrado. Usa force_reindex=True para reindexar.")
            return
        
        print("📖 Indexando documentos...")
        self.documents = []
        self.embeddings = []
        
        # Supported file types
        supported_extensions = ['.txt', '.md', '.json', '.py', '.csv', '.pdf']
        
        # Walk through knowledge directory
        for root, dirs, files in os.walk(self.knowledge_dir):
            # Skip cache directory
            if '.cache' in root:
                continue
                
            for file in files:
                file_path = os.path.join(root, file)
                ext = os.path.splitext(file)[1].lower()
                
                if ext in supported_extensions:
                    print(f"  📄 {file}")
                    content = self.read_file(file_path)
                    
                    if content:
                        # Split into chunks
                        chunks = self.chunk_text(content)
                        
                        for i, chunk in enumerate(chunks):
                            doc = {
                                'file': file,
                                'path': file_path,
                                'chunk_id': i,
                                'total_chunks': len(chunks),
                                'content': chunk,
                                'type': ext,
                                'indexed_at': datetime.now().isoformat(),
                                'char_start': sum(len(c) for c in chunks[:i]),
                                'char_end': sum(len(c) for c in chunks[:i+1])
                            }
                            self.documents.append(doc)
        
        if not self.documents:
            print("⚠️ No se encontraron documentos para indexar")
            return
        
        # Generate embeddings
        print(f"🔄 Generando embeddings para {len(self.documents)} fragmentos...")
        contents = [doc['content'] for doc in self.documents]
        self.embeddings = self.model.encode(contents, show_progress_bar=True)
        
        # Save index
        self.save_index()
        print(f"✅ Indexación completa: {len(self.documents)} fragmentos")
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search for relevant documents"""
        if not EMBEDDINGS_AVAILABLE or not self.model:
            return []
        
        if not self.documents or len(self.embeddings) == 0:
            print("⚠️ No hay documentos indexados. Ejecuta index_documents() primero.")
            return []
        
        # Encode query
        query_embedding = self.model.encode([query])[0]
        
        # Calculate cosine similarity
        similarities = []
        for i, doc_embedding in enumerate(self.embeddings):
            similarity = np.dot(query_embedding, doc_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
            )
            similarities.append((i, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top-k results
        results = []
        for i, similarity in similarities[:top_k]:
            doc = self.documents[i].copy()
            doc['similarity'] = float(similarity)
            results.append(doc)
        
        return results
    
    def get_context(self, query: str, max_tokens: int = 1000) -> str:
        """Get relevant context for a query (legacy method - returns only text)"""
        context, _ = self.get_context_with_sources(query, max_tokens)
        return context
    
    def get_context_with_sources(self, query: str, max_tokens: int = 1000) -> Tuple[str, List[Dict]]:
        """
        Get relevant context with source metadata for traceability
        
        Returns:
            Tuple[str, List[Dict]]: (context_text, sources_metadata)
        """
        results = self.search(query, top_k=5)
        
        if not results:
            return "", []
        
        # Build context from results with metadata
        context_parts = []
        sources = []
        total_length = 0
        
        for idx, result in enumerate(results):
            content = result['content']
            file_name = result['file']
            chunk_id = result['chunk_id']
            total_chunks = result.get('total_chunks', '?')
            similarity = result.get('similarity', 0.0)
            indexed_at = result.get('indexed_at', 'Desconocido')
            
            # Estimate tokens (rough: ~4 chars per token)
            estimated_tokens = len(content) // 4
            
            if total_length + estimated_tokens > max_tokens:
                break
            
            # Formato de sección legible
            section_info = f"fragmento {chunk_id+1}/{total_chunks}"
            
            # Add to context with inline source reference
            context_parts.append(f"[Fuente {idx+1}: {file_name} - {section_info}]\n{content}\n")
            total_length += estimated_tokens
            
            # Collect source metadata
            source_meta = {
                'source_id': idx + 1,
                'file': file_name,
                'path': result.get('path', ''),
                'section': section_info,
                'chunk_id': chunk_id,
                'total_chunks': total_chunks,
                'similarity': round(similarity, 3),
                'indexed_at': indexed_at,
                'content_preview': content[:150] + '...' if len(content) > 150 else content
            }
            sources.append(source_meta)
        
        context_text = "\n---\n".join(context_parts)
        return context_text, sources
    
    def add_document(self, file_path: str, content: Optional[str] = None):
        """Add a single document to the knowledge base"""
        if not EMBEDDINGS_AVAILABLE:
            print("❌ No se puede agregar sin sentence-transformers")
            return
        
        if content is None:
            content = self.read_file(file_path)
        
        if not content:
            return
        
        file_name = os.path.basename(file_path)
        chunks = self.chunk_text(content)
        
        for i, chunk in enumerate(chunks):
            doc = {
                'file': file_name,
                'path': file_path,
                'chunk_id': i,
                'total_chunks': len(chunks),
                'content': chunk,
                'type': os.path.splitext(file_name)[1],
                'indexed_at': datetime.now().isoformat(),
                'char_start': sum(len(c) for c in chunks[:i]),
                'char_end': sum(len(c) for c in chunks[:i+1])
            }
            self.documents.append(doc)
        
        # Generate embeddings for new chunks
        new_embeddings = self.model.encode([chunk for chunk in chunks])
        
        if len(self.embeddings) == 0:
            self.embeddings = new_embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, new_embeddings])
        
        self.save_index()
        print(f"✅ Documento agregado: {file_name} ({len(chunks)} fragmentos)")
    
    def stats(self):
        """Print knowledge base statistics"""
        print(f"\n📊 Estadísticas de la Base de Conocimiento:")
        print(f"   Documentos: {len(set(doc['file'] for doc in self.documents))}")
        print(f"   Fragmentos totales: {len(self.documents)}")
        
        if self.documents:
            file_types = {}
            for doc in self.documents:
                ext = doc['type']
                file_types[ext] = file_types.get(ext, 0) + 1
            
            print(f"   Tipos de archivo:")
            for ext, count in file_types.items():
                print(f"     {ext}: {count} fragmentos")


# Global instance
_kb_instance = None

def get_knowledge_base() -> KnowledgeBase:
    """Get or create global knowledge base instance"""
    global _kb_instance
    if _kb_instance is None:
        _kb_instance = KnowledgeBase()
    return _kb_instance
