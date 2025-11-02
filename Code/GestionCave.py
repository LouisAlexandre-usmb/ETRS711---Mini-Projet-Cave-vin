from datetime import date
from typing import List, Optional

# Modèles métier et accès base pour la gestion d'une cave à vin.
# Chaque classe gère ses opérations CRUD principales via un curseur MySQL fourni (self.conn).


class Utilisateur:
    # Représente un utilisateur de l'application.
    def __init__(self, nom: str, prenom: str, mot_de_passe: str, id_utilisateur: Optional[int] = None, conn=None):
        self.id_utilisateur = id_utilisateur
        self.nom = nom
        self.prenom = prenom
        self.mot_de_passe = mot_de_passe
        self.conn = conn

    def trouver_par_identifiants(self):
        # Retourne un utilisateur si la combinaison nom/prénom/mdp existe.
        cur = self.conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM utilisateur WHERE nom=%s AND prenom=%s AND mot_de_passe=%s", (self.nom, self.prenom, self.mot_de_passe))
        row = cur.fetchone()
        if row:
            return Utilisateur(row["nom"], row["prenom"], row["mot_de_passe"], row["id"], self.conn)
        return None

    def sauvegarder(self):
        # Insère l'utilisateur et met à jour son id.
        cur = self.conn.cursor()
        cur.execute("INSERT INTO utilisateur (nom, prenom, mot_de_passe) VALUES (%s, %s, %s)", (self.nom, self.prenom, self.mot_de_passe))
        self.id_utilisateur = cur.lastrowid
        return self.id_utilisateur


class Cave:
    # Représente une cave appartenant à un utilisateur.
    def __init__(self, nom: str, utilisateur_id: int, id_cave: Optional[int] = None, conn=None):
        self.id_cave = id_cave
        self.nom = nom
        self.utilisateur_id = utilisateur_id
        self.conn = conn

    def sauvegarder(self):
        # Crée une cave et renvoie son identifiant.
        cur = self.conn.cursor()
        cur.execute("INSERT INTO cave (nom, id_utilisateur) VALUES (%s, %s)", (self.nom, self.utilisateur_id))
        self.id_cave = cur.lastrowid
        return self.id_cave

    def obtenir_par_utilisateur(self, user_id: int) -> List["Cave"]:
        # Liste les caves d'un utilisateur donné.
        cur = self.conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM cave WHERE id_utilisateur=%s", (user_id,))
        return [Cave(row["nom"], row["id_utilisateur"], row["id"], self.conn) for row in cur.fetchall()]

    def obtenir_toutes(self) -> List["Cave"]:
        # Liste toutes les caves (exploration publique).
        cur = self.conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM cave")
        return [Cave(row["nom"], row["id_utilisateur"], row["id"], self.conn) for row in cur.fetchall()]

    def trouver_par_id(self, cave_id: int):
        # Récupère une cave par son identifiant.
        cur = self.conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM cave WHERE id=%s", (cave_id,))
        row = cur.fetchone()
        if row:
            return Cave(row["nom"], row["id_utilisateur"], row["id"], self.conn)
        return None


class Etagere:
    # Étagère (nom, capacité) appartenant à une cave.
    def __init__(self, nom: str, capacite: int, cave_id: int, id_etagere: Optional[int] = None, conn=None):
        self.id_etagere = id_etagere
        self.nom = nom
        self.capacite = capacite
        self.cave_id = cave_id
        self.conn = conn

    def obtenir_par_cave(self, cave_id: int) -> List["Etagere"]:
        # Retourne les étagères d'une cave.
        cur = self.conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM etagere WHERE id_cave=%s", (cave_id,))
        return [Etagere(row["nom"], row["capacite"], row["id_cave"], row["id"], self.conn) for row in cur.fetchall()]

    def sauvegarder(self):
        # Crée une étagère et renvoie son identifiant.
        cur = self.conn.cursor()
        cur.execute("INSERT INTO etagere (nom, capacite, id_cave) VALUES (%s, %s, %s)", (self.nom, self.capacite, self.cave_id))
        self.id_etagere = cur.lastrowid
        return self.id_etagere

    def compter_bouteilles(self) -> int:
        # Compte le nombre de bouteilles sur cette étagère.
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM bouteille_cave WHERE id_etagere=%s", (self.id_etagere,))
        row = cur.fetchone()
        return int(row[0]) if row else 0

    def supprimer_si_vide(self) -> bool:
        # Supprime l'étagère si elle ne contient aucune bouteille.
        if self.compter_bouteilles() > 0:
            return False
        cur = self.conn.cursor()
        cur.execute("DELETE FROM etagere WHERE id=%s", (self.id_etagere,))
        return True

    @staticmethod
    def compter_par_cave(conn, cave_id: int) -> int:
        # Compte le nombre d'étagères dans une cave.
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM etagere WHERE id_cave=%s", (cave_id,))
        row = cur.fetchone()
        return int(row[0]) if row else 0

    @staticmethod
    def verifier_existe_dans_cave(conn, etagere_id: int, cave_id: int) -> bool:
        # Vérifie qu'une étagère existe et appartient à la cave donnée.
        cur = conn.cursor()
        cur.execute("SELECT id FROM etagere WHERE id=%s AND id_cave=%s", (etagere_id, cave_id))
        return cur.fetchone() is not None

    @staticmethod
    def obtenir_capacite(conn, etagere_id: int) -> Optional[int]:
        # Récupère la capacité d'une étagère.
        cur = conn.cursor()
        cur.execute("SELECT capacite FROM etagere WHERE id=%s", (etagere_id,))
        row = cur.fetchone()
        return int(row[0]) if row and row[0] else None

    @staticmethod
    def compter_bouteilles_par_etagere(conn, etagere_id: int) -> int:
        # Compte le nombre de bouteilles sur une étagère donnée.
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM bouteille_cave WHERE id_etagere=%s", (etagere_id,))
        row = cur.fetchone()
        return int(row[0]) if row else 0


class Bouteille:
    # Métadonnées d'une bouteille (référentiel), indépendamment de sa présence en cave.
    def __init__(self, domaine_viticole: str, nom: str, type: str, annee: int, region: str, photo_etiquette: str = None, prix: float = None, id_bouteille: Optional[int] = None, conn=None):
        self.id_bouteille = id_bouteille
        self.domaine_viticole = domaine_viticole
        self.nom = nom
        self.type = type
        self.annee = annee
        self.region = region
        self.photo_etiquette = photo_etiquette
        self.prix = prix
        self.conn = conn

    def sauvegarder(self):
        # Insère la bouteille dans le référentiel et met à jour son id.
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO bouteille (domaine_viticole, nom, type, annee, region, photo_etiquette, prix) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (self.domaine_viticole, self.nom, self.type, self.annee, self.region, self.photo_etiquette, self.prix),
        )
        self.id_bouteille = cur.lastrowid
        return self.id_bouteille


class BouteilleCave(Bouteille):
    # Instance d'une bouteille placée dans une cave (via une étagère) avec date d'entrée.
    def __init__(self, domaine_viticole: str, nom: str, type: str, annee: int, region: str, etagere_id: int, photo_etiquette: str = None, prix: float = None, date_mise_en_cave: date = None, id_bouteille: Optional[int] = None, conn=None):
        super().__init__(domaine_viticole, nom, type, annee, region, photo_etiquette, prix, id_bouteille, conn)
        self.date_mise_en_cave = date_mise_en_cave or date.today()
        self.etagere_id = etagere_id

    def sauvegarder(self):
        # Lie la bouteille référentielle à une étagère de cave.
        cur = self.conn.cursor()
        cur.execute("INSERT INTO bouteille_cave (id_bouteille, id_etagere, date_mise_en_cave) VALUES (%s, %s, %s)", (self.id_bouteille, self.etagere_id, self.date_mise_en_cave))

    def obtenir_groupes_par_cave_par_etagere(self, cave_id: int):
        # Regroupe par caractéristiques et par étagère, inclut la photo éventuelle.
        cur = self.conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT 
              b.domaine_viticole,
              b.nom,
              b.type,
              b.annee,
              b.region,
              b.photo_etiquette,
              e.nom AS etagere_nom,
              COUNT(*) AS quantite
            FROM bouteille_cave bc
            JOIN bouteille b ON b.id = bc.id_bouteille
            JOIN etagere e ON e.id = bc.id_etagere
            WHERE e.id_cave=%s
            GROUP BY b.domaine_viticole, b.nom, b.type, b.annee, b.region, b.photo_etiquette, e.nom
            ORDER BY b.nom, b.annee, e.nom
            """,
            (cave_id,),
        )
        return cur.fetchall()

    @staticmethod
    def supprimer_bc_par_id(conn, bc_id: int):
        # Supprime une entrée bouteille_cave par son identifiant (ligne précise).
        cur = conn.cursor()
        cur.execute("DELETE FROM bouteille_cave WHERE id=%s", (bc_id,))

    @staticmethod
    def selectionner_pour_archivage_par_id(conn, cave_id: int, id_bouteille: int, quantite: int):
        # Sélectionne des bouteilles à archiver par identifiant de bouteille.
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT b.*, bc.id AS bc_id
            FROM bouteille_cave bc
            JOIN bouteille b ON b.id = bc.id_bouteille
            JOIN etagere e ON e.id = bc.id_etagere
            WHERE e.id_cave=%s AND b.id=%s
            LIMIT %s
            """,
            (cave_id, id_bouteille, quantite),
        )
        return cur.fetchall()

    @staticmethod
    def selectionner_pour_archivage_par_caracteristiques(conn, cave_id: int, domaine: str, nom: str, type_vin: str, annee: int, region: str, quantite: int):
        # Sélectionne des bouteilles à archiver par leurs caractéristiques.
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT b.*, bc.id AS bc_id
            FROM bouteille_cave bc
            JOIN bouteille b ON b.id = bc.id_bouteille
            JOIN etagere e ON e.id = bc.id_etagere
            WHERE e.id_cave=%s AND b.domaine_viticole=%s AND b.nom=%s AND b.type=%s AND b.annee=%s AND (b.region=%s OR (b.region IS NULL AND %s IS NULL))
            LIMIT %s
            """,
            (cave_id, domaine, nom, type_vin, annee, region, region, quantite),
        )
        return cur.fetchall()

    @staticmethod
    def selectionner_pour_suppression(conn, cave_id: int, domaine: str, nom: str, type_vin: str, annee: int, region: str, quantite: int):
        # Sélectionne des bouteilles à supprimer par leurs caractéristiques.
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT bc.id AS bc_id
            FROM bouteille_cave bc
            JOIN bouteille b ON b.id = bc.id_bouteille
            JOIN etagere e ON e.id = bc.id_etagere
            WHERE e.id_cave=%s AND b.domaine_viticole=%s AND b.nom=%s AND b.type=%s AND b.annee=%s AND (b.region=%s OR (b.region IS NULL AND %s IS NULL))
            LIMIT %s
            """,
            (cave_id, domaine, nom, type_vin, annee, region, region, quantite),
        )
        return cur.fetchall()


class BouteilleArchivee(Bouteille):
    # Bouteille sortie de cave avec date d'archivage, note et commentaire.
    def __init__(self, domaine_viticole: str, nom: str, type: str, annee: int, region: str, date_archivage: date, note: float = None, commentaire: str = None, utilisateur_id: int = None, photo_etiquette: str = None, prix: float = None, id_archive: Optional[int] = None, conn=None):
        super().__init__(domaine_viticole, nom, type, annee, region, photo_etiquette, prix, id_archive, conn)
        self.date_archivage = date_archivage
        self.note = note
        self.commentaire = commentaire
        self.utilisateur_id = utilisateur_id

    def sauvegarder(self, id_bouteille: int):
        # Insère une ligne d'archive liée à une bouteille existante.
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO bouteille_archivee (id_bouteille, id_utilisateur, date_archivage, note, commentaire) VALUES (%s, %s, %s, %s, %s)",
            (id_bouteille, self.utilisateur_id, self.date_archivage, self.note, self.commentaire),
        )

    @staticmethod
    def obtenir_resume_avis(conn, domaine: str, nom: str, type_vin: str, annee: int, region: str):
        # Retourne la moyenne des notes et le nombre d'avis pour un vin donné.
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT AVG(ba.note) AS moyenne, COUNT(*) AS nb_avis
            FROM bouteille_archivee ba
            JOIN bouteille b ON b.id = ba.id_bouteille
            WHERE b.domaine_viticole=%s AND b.nom=%s AND b.type=%s AND b.annee=%s AND (b.region=%s OR (b.region IS NULL AND %s IS NULL))
            """,
            (domaine, nom, type_vin, annee, region, region),
        )
        return cur.fetchone()

    @staticmethod
    def obtenir_avis_detail(conn, domaine: str, nom: str, type_vin: str, annee: int, region: str):
        # Retourne tous les avis (notes et commentaires) pour un vin donné, triés par date décroissante.
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT ba.note, ba.commentaire
            FROM bouteille_archivee ba
            JOIN bouteille b ON b.id = ba.id_bouteille
            WHERE b.domaine_viticole=%s AND b.nom=%s AND b.type=%s AND b.annee=%s AND (b.region=%s OR (b.region IS NULL AND %s IS NULL))
            ORDER BY ba.date_archivage DESC
            """,
            (domaine, nom, type_vin, annee, region, region),
        )
        return cur.fetchall()

    @staticmethod
    def obtenir_groupes_avis_avec_photos(conn):
        # Agrège les archives: moyenne/nb avis par vin + photo d'étiquette quand dispo.
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT b.domaine_viticole, b.nom, b.type, b.annee, b.region, b.photo_etiquette,
                   AVG(ba.note) AS moyenne, COUNT(*) AS nb_avis
            FROM bouteille_archivee ba
            JOIN bouteille b ON b.id = ba.id_bouteille
            GROUP BY b.domaine_viticole, b.nom, b.type, b.annee, b.region, b.photo_etiquette
            ORDER BY b.nom, b.annee
            """
        )
        return cur.fetchall()
