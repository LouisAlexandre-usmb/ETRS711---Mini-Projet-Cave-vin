import mysql.connector

# Ce module centralise la connexion MySQL.
# Adapter les paramètres dans DB(...) selon votre environnement local.

class DB:
    def __init__(self, host="127.0.0.1", user="root", password="", database="gestioncave"):
        # Établit la connexion à la base de données
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            autocommit=True
        )
