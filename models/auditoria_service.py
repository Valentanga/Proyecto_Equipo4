# models/auditoria_service.py

from datetime import datetime
from db.mongo_connection import db   # usamos el db compartido


class AuditoriaService:
    """
    Servicio para registrar y consultar eventos de auditoría.

    Guarda en la colección 'auditoria' quién accedió, vio o descargó documentos.
    """

    def __init__(self, collection_name: str = "auditoria"):
        # Colección donde se guardan los eventos de auditoría
        self.collection = db[collection_name]

    def registrar_evento(self, usuario, rol, accion,
                         documento_id=None, documento_nombre=None, extra=None):
        """
        Inserta un nuevo evento de auditoría en la colección.

        usuario: nombre o id del usuario (ej: 'pquintero')
        rol: rol del usuario (ej: 'Administrador', 'Abogado')
        accion: string tipo 'VER_DOCUMENTO', 'DESCARGAR_DOCUMENTO', etc.
        documento_id: id del documento (opcional)
        documento_nombre: nombre legible del documento (opcional)
        extra: diccionario opcional con datos adicionales (ip, módulo, etc.)
        """
        evento = {
            "usuario": usuario,
            "rol": rol,
            "accion": accion,
            "documento_id": documento_id,
            "documento_nombre": documento_nombre,
            "fecha_hora": datetime.utcnow()
        }

        # Si te mandan datos extra (por ejemplo ip, módulo, etc.), se agregan
        if isinstance(extra, dict):
            evento.update(extra)

        resultado = self.collection.insert_one(evento)
        return str(resultado.inserted_id)

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
