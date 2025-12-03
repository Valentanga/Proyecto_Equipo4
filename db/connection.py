# db/connection.py
# --- IMPORTACIONES ---
from pymongo import MongoClient  # Importamos el cliente oficial de MongoDB para Python

# 1. CONFIGURACIÓN DE LA CONEXIÓN (IGUAL QUE ANTES)
#    Esta es la URI de Mongo Atlas que ya usan todos
MONGO_URI = 'mongodb+srv://Sandy:Sandy1_1@documentosdbcluster.yqbxntf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
DB_NAME = 'GestorArchivos'

# 2. VARIABLES GLOBALES PARA REUTILIZAR LA CONEXIÓN
_client = None
_db = None


def get_db():
    """
    Devuelve SIEMPRE la misma instancia de base de datos.

    Primera vez que se llama:
      - Crea el MongoClient
      - Se conecta al cluster de Atlas
      - Obtiene la base de datos 'GestorArchivos'

    En llamadas siguientes:
      - Regresa la misma _db al instante (mucho más rápido)
    """
    global _client, _db

    # Si ya se inicializó antes, regresamos la misma
    if _db is not None:
        return _db

    try:
        # Si todavía no existe el cliente, se crea UNA sola vez
        if _client is None:
            _client = MongoClient(MONGO_URI)

        _db = _client[DB_NAME]
        return _db

    except Exception as e:
        # Si hay algún problema de red / Atlas, se muestra en consola
        print(f"Error de conexión a MongoDB: {e}")
        return None
