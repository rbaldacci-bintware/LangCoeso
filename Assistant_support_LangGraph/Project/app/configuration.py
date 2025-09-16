# configuration.py
"""
Sistema di configurazione con file .env criptati - compatibile con logica C#
"""
import os
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.primitives import hashes

class Configuration:
    """Gestisce configurazione da file .env criptati"""
    
    def __init__(self, config_path: str = "config.json", auto_load: bool = True):
        self._data = {}
        self.config_path = config_path
        if auto_load:
            self.load()
    
    def __getitem__(self, key: str) -> str:
        """Accesso tipo configuration["key"] con eccezione se manca"""
        if key not in self._data:
            raise InvalidOperationException(f"La chiave '{key}' non è configurata.")
        return self._data[key]
    
    def get(self, key: str, default=None) -> str:
        """Accesso con default opzionale"""
        return self._data.get(key, default)
    
    def load(self):
        """Carica configurazione da file criptato"""
        # Leggi config JSON
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        settings = config.get("EnvFileSettings", {})
        file_path = os.path.join(
            settings.get("Directory", ""),
            settings.get("FileName", "")
        )
        
        # Ottieni chiave cifratura
        encryption_key = (
            os.environ.get('CHIAVE_CIFRATURA') or 
            os.getenv('CHIAVE_CIFRATURA')
        )
        if not encryption_key:
            raise InvalidOperationException("CHIAVE_CIFRATURA environment variable is not set.")
        
        # Decripta file
        self._data = self._decrypt_file(file_path, encryption_key)
    
    def _decrypt_file(self, file_path: str, encryption_key: str) -> dict:
        """Decripta file .env"""
        # Genera chiave Fernet
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'stable_salt',
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(encryption_key.encode()))
        cipher = Fernet(key)
        
        # Leggi e decripta
        with open(file_path, 'rb') as f:
            encrypted = f.read()
        
        decrypted = cipher.decrypt(encrypted).decode('utf-8')
        
        # Parsa variabili
        variables = {}
        for line in decrypted.strip().split('\n'):
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                variables[k.strip()] = v.strip().strip('"\'')
        
        return variables
    
    def __contains__(self, key):
        """Supporta 'key in configuration'"""
        return key in self._data
    
    def __repr__(self):
        return f"Configuration({len(self._data)} keys)"


class InvalidOperationException(Exception):
    """Eccezione compatibile con C#"""
    pass


# Istanza globale (come in C#)
configuration = None

def initialize_configuration(config_path: str = "config.json"):
    """Inizializza configurazione globale"""
    global configuration
    configuration = Configuration(config_path)
    return configuration

# Esempio uso:
# from configuration import configuration, initialize_configuration
# 
# initialize_configuration()
# api_key = configuration["InternalStaticKey"]  # Lancia eccezione se manca
# api_url = configuration.get("ApiUrl", "http://localhost")  # Con default