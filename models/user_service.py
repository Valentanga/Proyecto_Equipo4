# models/user_service.py

from db.mongo_connection import db


class UserService:
    def __init__(self):
        # 👇 OJO: nombre de la colección tal como sale en Compass
        self.collection = db["usuarios"]

    def buscar_por_username(self, username):
        return self.collection.find_one({"username": username})

    def autenticar(self, username, password_clara):
        """
        Autenticación sencilla:
        - Busca el usuario por username
        - Compara la contraseña que escribió el usuario
          con el campo password_hash (que en tu caso es "123", "abc", etc.)
        """
        user = self.buscar_por_username(username)
        if not user:
            return None

        # En tu BD el campo se llama password_hash, pero guarda "123", "abc", etc.
        if user.get("password_hash") != password_clara:
            return None

        return user
