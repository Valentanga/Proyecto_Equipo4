#Esta clase sirve para la creaciond de usuarios
#Pues al no tener nosotros una seccion de creacion de usuarios esta el la opcion ideal jeje 
# --- IMPORTACIONES ---
import sys
import os
from datetime import datetime

# --- TRUCO DE IMPORTACIÓN ---
# Esta línea ayuda a buscar en la carpeta de atrás (..)". el "db" para podernos conectar
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Ahora sí podemos importar nuestra función de conexión de get_db
from db.connection import get_db
#Como solo tenemos 2 usuarios podemos reiniciar si es que ya estaban insertados
def reinicio_usuarios():
    # 1. OBTENER CONEXIÓN
    db = get_db()
    if db is None: return # Si no hay conexión, no hacemos nada

    users_col = db['usuarios'] # Seleccionamos la colección 'usuarios'

    # 2. LIMPIEZA TOTAL
    # delete_many({}) borra TODOS los documentos de esta colección.
    # Hacemos esto para no tener usuarios duplicados cada vez que corremos el script.
    users_col.delete_many({}) 

    # --- DEFINICIÓN DE PERMISOS (LA LÓGICA DE NEGOCIO) ---
    # Estos strings (textos) deben ser IDÉNTICOS a los que revisamos en los 'if' del main.py
    
    # Admin tiene acceso a Módulos 1, 3 y 5
    permisos_admin = ["subir_documentos", "gestion_categorias", "auditoria_accesos"]

    # Abogado tiene acceso a Módulos 1, 2 y 4
    permisos_abogado = ["subir_documentos", "busqueda_avanzada", "versiones_comentarios"]

    # --- CREACIÓN DE LA LISTA DE USUARIOS ---
    usuarios = [
        # USUARIO 1: ADMIN
        {
            "username": "admin1",
            "nombre": "Director General",
            "email": "admin@bufete.com",
            "password_hash": "123", # Contraseña simple para pruebas
            "rol": "Administrador",
            "permisos": permisos_admin, # <--- Aquí asignamos sus permisos
            "fecha_creacion": datetime.utcnow(),
            "creado_por": "system",
            "estado": "activo",
            "ultimo_login": None,
            "intentos_fallidos": 0
        },
        # USUARIO 2: ABOGADO
        {
            "username": "abogado1",
            "nombre": "Dr. Pedro López",
            "email": "p.lopez@bufete.com",
            "password_hash": "abc", # Contraseña simple
            "rol": "abogado",
            "permisos": permisos_abogado, # <--- Permisoss diferentes
            "fecha_creacion": datetime(2025, 11, 21, 20, 0, 0), # Fecha fija 
            "creado_por": "system",
            "estado": "activo",
            "ultimo_login": datetime.utcnow()
        }
    ]

    # 3. INSERTAR EN MONGO SI todo va bien
    try:
        users_col.insert_many(usuarios) # insert_many guarda la lista completa de golpe
        print("Base de datos reiniciada correctamente.")
        print("   -> Usuario: admin1 / 123")
        print("   -> Usuario: abogado1 / abc")
    except Exception as e:
        print(f"Error insertando: {e}")

# Bloque estándar para ejecutar el script solo si lo llamamos directamente
if __name__ == "__main__":
    reinicio_usuarios()