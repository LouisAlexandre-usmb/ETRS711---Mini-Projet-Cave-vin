import mysql.connector

# Script d'initialisation de la base de données
# Crée la base de données vierge avec toutes les tables nécessaires

def init_database(host="127.0.0.1", user="root", password="", database="gestioncave"):
    """
    Initialise la base de données en créant la base et toutes les tables nécessaires.
    """
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        cursor = conn.cursor()
        
        # Vérifier si la base existe déjà
        cursor.execute("SHOW DATABASES LIKE %s", (database,))
        base_exists = cursor.fetchone()
        
        if not base_exists:
            print(f"Création de la base de données '{database}'...")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"Base de données '{database}' créée avec succès.")
        else:
            print(f"La base de données '{database}' existe déjà.")
        
        cursor.close()
        conn.close()
        
        # Maintenant se connecter à la base créée
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        cursor = conn.cursor()
        
        print("Création des tables...")
        
        # Table utilisateur
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `utilisateur` (
                `id` int NOT NULL AUTO_INCREMENT,
                `nom` varchar(100) NOT NULL,
                `prenom` varchar(100) NOT NULL,
                `mot_de_passe` varchar(255) NOT NULL,
                PRIMARY KEY (`id`)
            ) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("  ✓ Table 'utilisateur' créée")
        
        # Table cave
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `cave` (
                `id` int NOT NULL AUTO_INCREMENT,
                `nom` varchar(100) NOT NULL,
                `id_utilisateur` int NOT NULL,
                PRIMARY KEY (`id`),
                KEY `id_utilisateur` (`id_utilisateur`)
            ) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("  ✓ Table 'cave' créée")
        
        # Table etagere
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `etagere` (
                `id` int NOT NULL AUTO_INCREMENT,
                `nom` varchar(100) NOT NULL,
                `capacite` int NOT NULL,
                `id_cave` int NOT NULL,
                PRIMARY KEY (`id`),
                KEY `id_cave` (`id_cave`)
            ) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("  ✓ Table 'etagere' créée")
        
        # Table bouteille
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `bouteille` (
                `id` int NOT NULL AUTO_INCREMENT,
                `domaine_viticole` varchar(150) NOT NULL,
                `nom` varchar(150) NOT NULL,
                `type` enum('Rouge','Blanc','Rosé','Champagne') NOT NULL,
                `annee` int NOT NULL,
                `region` varchar(100) DEFAULT NULL,
                `photo_etiquette` varchar(255) DEFAULT NULL,
                `prix` decimal(6,2) DEFAULT NULL,
                PRIMARY KEY (`id`)
            ) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("  ✓ Table 'bouteille' créée")
        
        # Table bouteille_cave
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `bouteille_cave` (
                `id` int NOT NULL AUTO_INCREMENT,
                `id_bouteille` int NOT NULL,
                `id_etagere` int NOT NULL,
                `date_mise_en_cave` date NOT NULL DEFAULT (curdate()),
                PRIMARY KEY (`id`),
                KEY `id_bouteille` (`id_bouteille`),
                KEY `id_etagere` (`id_etagere`)
            ) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("  ✓ Table 'bouteille_cave' créée")
        
        # Table bouteille_archivee
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `bouteille_archivee` (
                `id` int NOT NULL AUTO_INCREMENT,
                `id_bouteille` int NOT NULL,
                `id_utilisateur` int NOT NULL,
                `date_archivage` date NOT NULL DEFAULT (curdate()),
                `note` float DEFAULT NULL,
                `commentaire` text,
                PRIMARY KEY (`id`),
                KEY `id_bouteille` (`id_bouteille`),
                KEY `id_utilisateur` (`id_utilisateur`)
            ) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("  ✓ Table 'bouteille_archivee' créée")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print()
        print(f"Initialisation terminée avec succès !")
        print(f"La base de données '{database}' est prête à être utilisée (vide).")
        return True
        
    except mysql.connector.Error as e:
        print(f"\nERREUR MySQL: {e}")
        print("\nVérifiez que:")
        print("  - MySQL est démarré")
        print("  - Les paramètres de connexion sont corrects dans init_db.py")
        print("  - L'utilisateur a les droits de création de base de données")
        return False
    except Exception as e:
        print(f"\nERREUR: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Script d'initialisation de la base de données")
    print("=" * 60)
    print()
    
    # Utiliser les mêmes paramètres par défaut que db.py
    success = init_database()
    
    if success:
        print()
        print("=" * 60)
        print("Vous pouvez maintenant lancer l'application avec: python app.py")
        print("=" * 60)
    else:
        print()
        print("=" * 60)
        print("Échec de l'initialisation. Corrigez les erreurs ci-dessus.")
        print("=" * 60)

