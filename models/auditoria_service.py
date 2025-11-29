# models/auditoria_service.py

from datetime import datetime
from pymongo import MongoClient
from config import MONGO_URI, DB_NAME


class AuditoriaService:
    """
    Servicio para registrar y consultar eventos de auditoría.

    Guarda en la colección 'auditoria' quién accedió o descargó documentos.
    """

    def __init__(self):
        # Crear el cliente de Mongo y apuntar a la base de datos
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]

        # Colección donde se guardan los eventos de auditoría
        self.collection = db["auditoria"]

    def registrar_evento(self, usuario, rol, accion,
                         documento_id=None, documento_nombre=None):
        """
        Inserta un nuevo evento de auditoría en la colección.

        usuario: nombre o id del usuario (ej: 'pquintero')
        rol: rol del usuario (ej: 'Administrador', 'Abogado')
        accion: string tipo 'VER_DOCUMENTO' o 'DESCARGAR_DOCUMENTO'
        documento_id: id del documento (opcional)
        documento_nombre: nombre legible del documento (opcional)
        """
        evento = {
            "usuario": usuario,
            "rol": rol,
            "accion": accion,  # 'VER_DOCUMENTO' o 'DESCARGAR_DOCUMENTO'
            "documento_id": documento_id,
            "documento_nombre": documento_nombre,
            "fecha_hora": datetime.utcnow()
        }

        self.collection.insert_one(evento)

    def obtener_eventos(self, filtro=None):
        """
        Regresa una lista de eventos de auditoría.

        filtro: diccionario opcional para filtrar por usuario, acción, etc.
        Ejemplo: {"usuario": "pquintero"} o {"accion": "DESCARGAR_DOCUMENTO"}
        """
        if filtro is None:
            filtro = {}

        # Ordenamos por fecha_hora descendente (del más nuevo al más viejo)
        cursor = self.collection.find(filtro).sort("fecha_hora", -1)
        return list(cursor)
