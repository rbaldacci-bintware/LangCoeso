# graph_nodes.py
import os
import requests
from .state import GraphState

# URL dell'API Google che hai sviluppato - legge da variabile d'ambiente
API_URL = os.getenv("GOOGLE_API_URL", "http://localhost:8001")

def conversation_reconstruction_node(state: GraphState) -> dict:
    """
    Nodo che prende due file audio e ricostruisce la conversazione.
    """
    print("--- ESECUZIONE NODO RICOSTRUZIONE CONVERSAZIONE ---")
    
    if len(state["audio_file_paths"]) != 2:  # ← CORRETTO
        raise ValueError("Sono richiesti esattamente due file audio.")
    
    files = []
    for file_path in state["audio_file_paths"]:
        with open(file_path, "rb") as f:
            ext = os.path.splitext(file_path)[1][1:]
            mime_type = f"audio/{ext}"
            file_content = f.read()
            files.append(('files', (os.path.basename(file_path), file_content, mime_type)))
    
    response = requests.post(f"{API_URL}/audio/reconstruct", files=files)
    
    if response.status_code == 200:
        transcript = response.json()["reconstructed_transcript"]
        print("--- RICOSTRUZIONE RICEVUTA ---")
        print(transcript)
        return {"transcript": transcript}
    else:
        raise Exception(f"Errore API: {response.status_code}")