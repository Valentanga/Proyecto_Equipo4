# models/categorias_service.py
from datetime import datetime
from uuid import uuid4
from bson import ObjectId
from db.connection import get_db

class CategoriasService:
    def __init__(self, collection_name="categorias"):
        db = get_db()
        if db is None:
            raise RuntimeError("No se pudo obtener la base de datos desde get_db()")
        self.collection = db[collection_name]

    # ----------------- CATEGORIAS -----------------
    def crear_categoria(self, slug, descripcion, creado_por):
        slug = slug.strip().lower().replace(" ", "-")
        descripcion = descripcion.strip()

        if not slug:
            raise ValueError("El slug de la categoría no puede estar vacío.")

        existente = self.collection.find_one({"slug": slug, "activo": True})
        if existente:
            raise ValueError(f"Ya existe una categoría activa con el slug '{slug}'.")

        doc = {
            "slug": slug,
            "descripcion": descripcion,
            "tipos": [],
            "activo": True,
            "creado_por": creado_por,
            "fecha_creacion": datetime.utcnow(),
            "ultima_modificacion_por": creado_por,
            "fecha_ultima_modificacion": datetime.utcnow()
        }
        res = self.collection.insert_one(doc)
        return str(res.inserted_id)

    def listar_categorias(self, solo_activas=True):
        filtro = {"activo": True} if solo_activas else {}
        return list(self.collection.find(filtro).sort("descripcion", 1))

    def obtener_categoria(self, categoria_id):
        return self.collection.find_one({"_id": ObjectId(categoria_id)})

    def actualizar_categoria(self, categoria_id, slug, descripcion, modificado_por):
        slug = slug.strip().lower().replace(" ", "-")
        descripcion = descripcion.strip()

        if not slug:
            raise ValueError("El slug de la categoría no puede estar vacío.")

        otro = self.collection.find_one({
            "slug": slug,
            "activo": True,
            "_id": {"$ne": ObjectId(categoria_id)}
        })

        if otro:
            raise ValueError("El slug ya está en uso por otra categoría activa.")

        update = {
            "$set": {
                "slug": slug,
                "descripcion": descripcion,
                "ultima_modificacion_por": modificado_por,
                "fecha_ultima_modificacion": datetime.utcnow()
            }
        }
        return self.collection.update_one({"_id": ObjectId(categoria_id)}, update).modified_count

    def eliminar_categoria(self, categoria_id, eliminado_por):
        update = {
            "$set": {
                "activo": False,
                "ultima_modificacion_por": eliminado_por,
                "fecha_ultima_modificacion": datetime.utcnow()
            }
        }
        return self.collection.update_one({"_id": ObjectId(categoria_id)}, update).modified_count

    # ----------------- TIPOS -----------------
    def agregar_tipo(self, categoria_id, nombre_tipo, descripcion_tipo, creado_por):
        nombre_tipo_slug = nombre_tipo.strip().lower().replace(" ", "-")
        descripcion_tipo = descripcion_tipo.strip()

        if not nombre_tipo_slug:
            raise ValueError("El nombre del tipo no puede estar vacío.")

        cat = self.collection.find_one({"_id": ObjectId(categoria_id)})
        if not cat:
            raise ValueError("Categoría no encontrada.")

        # validar duplicado
        for t in cat.get("tipos", []):
            if t.get("slug") == nombre_tipo_slug and t.get("activo", True):
                raise ValueError("Ya existe un tipo con ese nombre en la categoría.")

        tipo = {
            "id": str(uuid4()),
            "slug": nombre_tipo_slug,
            "nombre": nombre_tipo,
            "descripcion": descripcion_tipo,
            "activo": True,
            "creado_por": creado_por,
            "fecha_creacion": datetime.utcnow(),
            "ultima_modificacion_por": creado_por,
            "fecha_ultima_modificacion": datetime.utcnow()
        }

        self.collection.update_one(
            {"_id": ObjectId(categoria_id)},
            {
                "$push": {"tipos": tipo},
                "$set": {
                    "ultima_modificacion_por": creado_por,
                    "fecha_ultima_modificacion": datetime.utcnow()
                }
            }
        )
        return tipo["id"]

    def editar_tipo(self, categoria_id, tipo_id, nombre_tipo, descripcion_tipo, modificado_por):
        nombre_tipo_slug = nombre_tipo.strip().lower().replace(" ", "-")
        descripcion_tipo = descripcion_tipo.strip()

        cat = self.collection.find_one({"_id": ObjectId(categoria_id)})
        if not cat:
            raise ValueError("Categoría no encontrada.")

        # revisar duplicado
        for t in cat.get("tipos", []):
            if t.get("slug") == nombre_tipo_slug and t.get("id") != tipo_id and t.get("activo", True):
                raise ValueError("Otro tipo ya usa ese nombre.")

        update = {
            "$set": {
                "tipos.$.slug": nombre_tipo_slug,
                "tipos.$.nombre": nombre_tipo,
                "tipos.$.descripcion": descripcion_tipo,
                "tipos.$.ultima_modificacion_por": modificado_por,
                "tipos.$.fecha_ultima_modificacion": datetime.utcnow(),
                "ultima_modificacion_por": modificado_por,
                "fecha_ultima_modificacion": datetime.utcnow()
            }
        }

        return self.collection.update_one(
            {"_id": ObjectId(categoria_id), "tipos.id": tipo_id},
            update
        ).modified_count

    def eliminar_tipo(self, categoria_id, tipo_id, eliminado_por):
        update = {
            "$set": {
                "tipos.$.activo": False,
                "tipos.$.ultima_modificacion_por": eliminado_por,
                "tipos.$.fecha_ultima_modificacion": datetime.utcnow(),
                "ultima_modificacion_por": eliminado_por,
                "fecha_ultima_modificacion": datetime.utcnow()
            }
        }

        return self.collection.update_one(
            {"_id": ObjectId(categoria_id), "tipos.id": tipo_id},
            update
        ).modified_count
