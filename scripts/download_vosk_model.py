"""
Download Vosk Spanish model
"""
import os
import zipfile
import requests
from tqdm import tqdm

MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip"
MODEL_NAME = "vosk-model-small-es-0.42"
MODELS_DIR = "models"

def download_file(url, filename):
    """Download file with progress bar"""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(filename, 'wb') as file, tqdm(
        desc=filename,
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
    ) as progress_bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            progress_bar.update(size)

def main():
    print("Descargando modelo de español para Vosk...")
    print("Este proceso puede tardar unos minutos.\n")
    
    # Create models directory
    if not os.path.exists(MODELS_DIR):
        os.makedirs(MODELS_DIR)
    
    model_path = os.path.join(MODELS_DIR, MODEL_NAME)
    
    # Check if model already exists
    if os.path.exists(model_path):
        print(f"El modelo ya existe en: {model_path}")
        return
    
    # Download model
    zip_filename = f"{MODEL_NAME}.zip"
    print(f"Descargando {MODEL_URL}...")
    download_file(MODEL_URL, zip_filename)
    
    # Extract model
    print(f"\nExtrayendo modelo...")
    with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
        zip_ref.extractall(MODELS_DIR)
    
    # Remove zip file
    os.remove(zip_filename)
    
    print(f"\n✓ Modelo descargado exitosamente en: {model_path}")
    print("Ya puedes usar el reconocimiento de voz con Vosk.")

if __name__ == "__main__":
    main()
