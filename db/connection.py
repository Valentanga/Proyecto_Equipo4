# --- IMPORTACIONES ---
from pymongo import MongoClient  # Importamos el cliente oficial de MongoDB para Python

def get_db():
    # 1. CONFIGURACIÓN DE LA CONEXIÓN
    # aqui ingrese mi cuenta pueden hacer otro archivo como este y su cuenta 
    #o bien todos podemos usar esta coneccion como quieran
    MONGO_URI = 'mongodb+srv://Sandy:Sandy1_1@documentosdbcluster.yqbxntf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'    
    # Nombre de tu base de datos. Si no existe, Mongo la crea al guardar el primer dato.
    DB_NAME = 'GestorArchivos'

    try:
        # 2. INTENTO DE CONEXIÓN
        # Creamos el cliente (el "enchufe")
        client = MongoClient(MONGO_URI)
        
        # Devolvemos el objeto que representa tu base de datos específica
        return client[DB_NAME]
        
    except Exception as e:
        # 3. MANEJO DE ERRORES
        # Si Mongo no está instalado o el servicio está apagado, entra aquí.
        print(f"Error de conexión: {e}")
        return None