from pymongo import MongoClient

url = "mongodb+srv://valentinaesquivel880_db_user:JS0RY8c4NFRBFWlk@documentosdbcluster.yqbxntf.mongodb.net/?appName=DocumentosDBCluster"
client = MongoClient(url)
db = client['GestorArchivos']
usuarios = db["Users"]
print("Conexión exitosa")
