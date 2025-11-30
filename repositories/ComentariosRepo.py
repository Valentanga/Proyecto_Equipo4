import datetime
from bson import ObjectId


class ComentariosRepo:
    def __init__(self, db):
        self.col = db.comentarios

    def crear(self, versionId, texto, autor, parentId=None):
        doc = {
            "versionId": ObjectId(versionId),
            "parentId": ObjectId(parentId) if parentId else None,
            "texto": texto,
            "autor": autor,
            "createdAt": datetime.utcnow()
        }
        return self.col.insert_one(doc).inserted_id

    def listar_por_version(self, versionId):
        return list(self.col.find({"versionId": ObjectId(versionId)}).sort("createdAt", 1))
