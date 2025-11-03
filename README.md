Mini projet ETRS711 : Application pour la gestion d’une cave à vin
=================================

Description
------

Fonctionnalités clés
--------------------
- Authentification: inscription/connexion, gestion de session.
- Caves: créer une cave, lister ses caves, explorer toutes les caves.
- Étagères: créer/supprimer (suppression protégée si des bouteilles sont présentes).
- Bouteilles: ajout (avec upload d’image PNG/JPG/JPEG), quantité et prix optionnel.
- Archivage: archiver des bouteilles avec note (/20) et commentaire.
- Avis: vue communautaire des archives, moyenne des notes par vin, détails des avis.
- Tri/Filtrage visuel: cliquez sur un en-tête de colonne dans la page d’une cave pour trier.

Structure du projet
-------------------
- `Code/app.py`           Routes Flask principales
- `Code/db.py`            Connexion MySQL (mysql-connector)
- `Code/GestionCave.py`   Modèles métier (Utilisateur, Cave, Étagère, Bouteille, etc.)
- `Code/templates/`       Templates Jinja2 (HTML)
- `Code/static/images/`   Uploads d’étiquettes (images)
- `Code/gestioncave.sql`  Script de création/peuplement de la base

Prérequis
---------


Lancement rapide de l'application
-------------------
Copier le dossier code
Installer les dépendances 

Créer la base de donné 
Configurer la connexion MySQL dans tel et tel fichier

lancer app.py
L’application démarre sur: http://127.0.0.1:5000 -> donc copier cet URL dans un navigateur



Notes d’utilisation
-------------------
- Uploads: taille max 16MB; extensions autorisées: png, jpg, jpeg.
- Les images sont enregistrées dans `Code/static/images/` avec un nom unique.
- Pour trier, cliquez sur les en-têtes de colonnes (ex: Domaine, Nom, Type, Année...).
- L’archivage demande une note et/ou un commentaire, groupés visuellement avec le bouton Archiver.


État du projet
-------------------
Projet pédagogique. Version finale. A adapter si besoin de plus de sécurité par exemple.

Crédit
-------------------
- Louis ALEXANDRE — Responsable
- D. Telisson
