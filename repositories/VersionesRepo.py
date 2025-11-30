import datetime

from bson import ObjectId


class VersionesRepo:
    def __init__(self, db):
        self.col = db.versiones

    def crear(self, documentoId, numero, ruta, hash, createdBy):
        doc = {
            "documentoId": documentoId,  # 👈 sin ObjectId()
            "numero": numero,
            "ruta": ruta,
            "hash": hash,
            "createdBy": createdBy,
            "createdAt": datetime.utcnow()
        }
        result = self.col.insert_one(doc)
        return result.inserted_id

    def listar_por_documento(self, documentoId):
        return list(self.col.find({"documentoId": documentoId}).sort("numero", 1))