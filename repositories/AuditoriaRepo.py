import datetime
from bson import ObjectId


class AuditoriaRepo:
    def __init__(self, db):
        self.col = db.auditoria

    def registrar(self, actor, documentoId, accion, detalle=None, ip=None):
        doc = {
            "actor": actor,
            "documentoId": ObjectId(documentoId) if documentoId else None,
            "accion": accion,
            "detalle": detalle or {},
            "ip": ip,
            "createdAt": datetime.utcnow()
        }
        self.col.insert_one(doc)

    def listar(self, filtro=None, limit=200):
        return list(self.col.find(filtro or {}).sort("createdAt", -1).limit(limit))