# models/auditoria_service.py

from datetime import datetime
from db.connection import get_db   # 👈 usamos la función que ya existe


class AuditoriaService:
    """
    Servicio para registrar y consultar eventos de auditoría.

    Guarda en la colección 'auditoria' quién accedió, vio o descargó documentos.
    """

    def __init__(self, collection_name: str = "auditoria"):
        # Obtenemos la base de datos usando la conexión del proyecto
        db = get_db()
        if db is None:
            # Por si falla la conexión, lanzamos un error claro
            raise RuntimeError("No se pudo obtener la base de datos desde get_db()")

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

        cursor = self.collection.find(filtro).sort("fecha_hora", -1)
        return list(cursor)
