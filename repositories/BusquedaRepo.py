from db.connection import get_db

class BusquedaRepo:
    def __init__(self):
        self.collection = get_db()["documentos"]

    def buscar(self, filtros):
        query = {}

        for key, value in filtros.items():
            if value and value.strip():
                query[key] = {"$regex": value, "$options": "i"}

        return list(self.collection.find(query))
