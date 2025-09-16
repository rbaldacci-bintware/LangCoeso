# main.py
import os
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from .graph import conversation_graph
from .state import GraphState

api = FastAPI(  # ← CAMBIATO da 'api' a 'app'
    title="LangGraph Audio Processing API",
    description="API per ricostruire conversazioni da file audio locali.",
    version="1.0.0",
)

class AudioFilePaths(BaseModel):
    """Modello per i percorsi dei file audio."""
    file1: str
    file2: str

@api.get("/")
async def root():
    """Endpoint di benvenuto."""
    return {"message": "LangGraph Audio API - Invia i percorsi dei file audio per la ricostruzione"}

@api.post("/transcribe-conversation/")
async def transcribe_conversation(paths: AudioFilePaths):
    """
    Accetta i percorsi di due file audio locali e ricostruisce la conversazione.
    
    Esempio di richiesta:
    {
        "file1": "C:/Users/rikka/Downloads/72aaba06-4267-443f-bf87-f50141e97734_inbound.mp3",
        "file2": "C:/Users/rikka/Downloads/72aaba06-4267-443f-bf87-f50141e97734_outbound.mp3"
    }
    """
    # Verifica che i file esistano
    if not os.path.exists(paths.file1):
        raise HTTPException(status_code=404, detail=f"File non trovato: {paths.file1}")
    if not os.path.exists(paths.file2):
        raise HTTPException(status_code=404, detail=f"File non trovato: {paths.file2}")
    
    try:
        # Prepara lo stato con i percorsi dei file
        initial_state: GraphState = {
            "messages": [],
            "audio_file_paths": [paths.file1, paths.file2],
            "transcript": "",
        }
        
        print(f"Elaborazione file:")
        print(f"  - File 1: {paths.file1}")
        print(f"  - File 2: {paths.file2}")
        
        # Esegui il grafo
        final_state = await conversation_graph.ainvoke(initial_state)
        transcript = final_state.get("transcript", "Ricostruzione non disponibile.")
        
        return {
            "files_processed": [paths.file1, paths.file2],
            "reconstructed_conversation": transcript
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore: {str(e)}")