from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import date
import os
import uuid
from werkzeug.utils import secure_filename
from db import DB
from GestionCave import Utilisateur, Cave, Etagere, Bouteille, BouteilleCave, BouteilleArchivee

app = Flask(__name__)
db = DB()
conn = db.conn  # Connexion MySQL partagée

app.secret_key = "dev-secret"  # Clé de session (à sécuriser en production)

# Configuration pour l'upload d'images
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

ALLOWED_TYPES = ["Rouge", "Blanc", "Rosé", "Champagne"]  # Types de vins acceptés

def allowed_file(filename):
    # Vérifie l'extension autorisée pour l'upload d'image
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    # Page d'accueil: redirige vers login si non connecté
    if not session.get("user_id"):
        return redirect(url_for("login"))
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Authentification par nom/prénom/mdp
    if request.method == "POST":
        nom = request.form.get("nom")
        prenom = request.form.get("prenom")
        mot_de_passe = request.form.get("mot_de_passe")
        user = Utilisateur(nom, prenom, mot_de_passe, conn=conn)
        u = user.trouver_par_identifiants()
        if u:
            session["user_id"] = u.id_utilisateur
            session["user_nom"] = u.nom
            session["user_prenom"] = u.prenom
            return redirect(url_for("index"))
        flash("Identifiants invalides")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    # Création d'un compte utilisateur
    if request.method == "POST":
        nom = request.form.get("nom")
        prenom = request.form.get("prenom")
        mot_de_passe = request.form.get("mot_de_passe")
        user = Utilisateur(nom, prenom, mot_de_passe, conn=conn)
        user.sauvegarder()
        flash("Compte créé. Vous pouvez vous connecter.")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/logout")
def logout():
    # Déconnexion: nettoyage de la session
    session.clear()
    return redirect(url_for("index"))


@app.route("/caves/creer", methods=["GET", "POST"])
def creer_cave():
    # Création d'une nouvelle cave (réservé aux utilisateurs connectés)
    if request.method == "POST":
        if "user_id" not in session:
            return redirect(url_for("login"))
        nom = request.form.get("nom")
        cave = Cave(nom, session["user_id"], conn=conn)
        cave.sauvegarder()
        return redirect(url_for("mes_caves"))
    return render_template("creer_cave.html")


@app.route("/caves/mes")
def mes_caves():
    # Liste des caves de l'utilisateur connecté
    if "user_id" not in session:
        return redirect(url_for("login"))
    c = Cave("", 0, conn=conn)
    caves = c.obtenir_par_utilisateur(session["user_id"])
    return render_template("mes_caves.html", caves=caves)


@app.route("/caves/explorer")
def explorer_caves():
    # Exploration de toutes les caves (vue publique)
    c = Cave("", 0, conn=conn)
    caves = c.obtenir_toutes()
    return render_template("explorer_caves.html", caves=caves, user_id=session.get("user_id"))


@app.route("/caves/<int:cave_id>")
def detail_cave(cave_id: int):
    # Détail d'une cave: listing des bouteilles groupées et actions
    c = Cave("", 0, conn=conn) 
    cave = c.trouver_par_id(cave_id)
    e = Etagere("", 0, cave_id, conn=conn)
    etageres = e.obtenir_par_cave(cave_id)
    b = BouteilleCave("", "", "", 0, "", 0, conn=conn) 
    tri = request.args.get("tri") or "nom" 
    ordre = request.args.get("ordre") or "asc" 
    groupes = b.obtenir_groupes_par_cave_par_etagere(cave_id) 
    # tri côté python sur les champs autorisés
    cles = {"nom": "nom", "domaine": "domaine_viticole", "type": "type", "annee": "annee", "region": "region", "quantite": "quantite", "etagere": "etagere_nom"}
    cle = cles.get(tri, "nom")
    groupes = sorted(groupes, key=lambda g: (g[cle] if g[cle] is not None else ""))
    if ordre == "desc":
        groupes = list(reversed(groupes))
    est_proprietaire = session.get("user_id") == cave.utilisateur_id if cave else False
    return render_template("detail_cave.html", cave=cave, etageres=etageres, groupes=groupes, est_proprietaire=est_proprietaire, tri=tri, ordre=ordre, allowed_types=ALLOWED_TYPES)


@app.route("/etagere/creer", methods=["POST"])
def creer_etagere():
    # Ajoute une étagère dans la cave (propriétaire seulement)
    if "user_id" not in session:
        return redirect(url_for("login"))
    cave_id = int(request.form.get("cave_id"))
    c = Cave("", 0, conn=conn)
    cave = c.trouver_par_id(cave_id)
    if not cave or cave.utilisateur_id != session["user_id"]:
        flash("Action non autorisée")
        return redirect(url_for("detail_cave", cave_id=cave_id))
    nom = request.form.get("nom")
    capacite = int(request.form.get("capacite"))
    Etagere(nom, capacite, cave_id, conn=conn).sauvegarder()
    return redirect(url_for("detail_cave", cave_id=cave_id))


@app.route("/etagere/supprimer", methods=["POST"])
def supprimer_etagere():
    # Supprime une étagère vide (propriétaire seulement)
    if "user_id" not in session:
        return redirect(url_for("login"))
    cave_id = int(request.form.get("cave_id"))
    id_etagere = int(request.form.get("id_etagere"))
    c = Cave("", 0, conn=conn)
    cave = c.trouver_par_id(cave_id)
    if not cave or cave.utilisateur_id != session["user_id"]:
        flash("Action non autorisée")
        return redirect(url_for("detail_cave", cave_id=cave_id))
    e = Etagere("", 0, cave_id, id_etagere=id_etagere, conn=conn)
    if not e.supprimer_si_vide():
        flash("Impossible de supprimer : l'étagère contient des bouteilles")
    return redirect(url_for("detail_cave", cave_id=cave_id))


@app.route("/bouteilles/ajouter", methods=["POST"])
def ajouter_bouteille():
    # Ajoute N exemplaires d'une bouteille (avec upload d'image optionnel)
    if "user_id" not in session:
        return redirect(url_for("login"))
    cave_id = int(request.form.get("cave_id"))
    c = Cave("", 0, conn=conn)
    cave = c.trouver_par_id(cave_id)
    if not cave or cave.utilisateur_id != session["user_id"]:
        flash("Action non autorisée")
        return redirect(url_for("detail_cave", cave_id=cave_id))
    domaine = request.form.get("domaine_viticole")
    nom = request.form.get("nom")
    type_vin = request.form.get("type")
    if type_vin not in ALLOWED_TYPES:
        flash("Type de vin invalide")
        return redirect(url_for("detail_cave", cave_id=cave_id))
    annee = int(request.form.get("annee"))
    region = request.form.get("region")
    prix = request.form.get("prix")
    quantite = int(request.form.get("quantite", 1))
    etagere_id_raw = request.form.get("etagere_id")
    # Validation étagère: présence, existence et appartenance à la cave
    nb_etageres = Etagere.compter_par_cave(conn, cave_id)
    if nb_etageres == 0:
        flash("Aucune étagère dans cette cave. Créez d'abord une étagère.")
        return redirect(url_for("detail_cave", cave_id=cave_id))
    if not etagere_id_raw:
        flash("Veuillez sélectionner une étagère valide")
        return redirect(url_for("detail_cave", cave_id=cave_id))
    try:
        etagere_id = int(etagere_id_raw)
    except ValueError:
        flash("Identifiant d'étagère invalide")
        return redirect(url_for("detail_cave", cave_id=cave_id))
    if not Etagere.verifier_existe_dans_cave(conn, etagere_id, cave_id):
        flash("Étagère inexistante ou n'appartenant pas à cette cave")
        return redirect(url_for("detail_cave", cave_id=cave_id))

    # Gestion de l'upload d'image
    photo_filename = None
    if 'photo_etiquette' in request.files:
        file = request.files['photo_etiquette']
        if file and file.filename and allowed_file(file.filename):
            # Générer un nom unique pour éviter les conflits
            filename = secure_filename(file.filename)
            name, ext = os.path.splitext(filename)
            unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
            photo_filename = unique_filename

    # Contrôle de capacité d'étagère
    capacite = Etagere.obtenir_capacite(conn, etagere_id)
    nb_bouteilles = Etagere.compter_bouteilles_par_etagere(conn, etagere_id)
    if capacite and nb_bouteilles + quantite > capacite:
        flash("Capacité maximale atteinte pour cette étagère")
        return redirect(url_for("detail_cave", cave_id=cave_id))

    b = Bouteille(domaine, nom, type_vin, annee, region, photo_etiquette=photo_filename, prix=prix, conn=conn)
    for _ in range(quantite):
        bid = b.sauvegarder()
        bc = BouteilleCave(domaine, nom, type_vin, annee, region, etagere_id, photo_etiquette=photo_filename, prix=prix, id_bouteille=bid, conn=conn)
        bc.sauvegarder()
    return redirect(url_for("detail_cave", cave_id=cave_id))


@app.route("/bouteilles/archiver", methods=["POST"])
def archiver_bouteille():
    # Archive des exemplaires (avec note/commentaire) et les retire de la cave
    if "user_id" not in session:
        return redirect(url_for("login"))
    id_bouteille = request.form.get("id_bouteille")
    note = request.form.get("note")
    commentaire = request.form.get("commentaire")
    cave_id = int(request.form.get("cave_id"))
    domaine = request.form.get("domaine_viticole")
    nom = request.form.get("nom")
    type_vin = request.form.get("type")
    if type_vin and type_vin not in ALLOWED_TYPES:
        flash("Type de vin invalide")
        return redirect(url_for("detail_cave", cave_id=cave_id))
    annee = int(request.form.get("annee"))
    region = request.form.get("region")
    quantite = int(request.form.get("quantite", 1))

    c = Cave("", 0, conn=conn)
    cave = c.trouver_par_id(cave_id)
    if not cave or cave.utilisateur_id != session["user_id"]:
        flash("Action non autorisée")
        return redirect(url_for("detail_cave", cave_id=cave_id))

    rows = BouteilleCave.selectionner_pour_archivage(conn, cave_id, domaine, nom, type_vin, annee, region, quantite)

    for row in rows:
        b = Bouteille(row["domaine_viticole"], row["nom"], row["type"], row["annee"], row["region"], row.get("photo_etiquette"), float(row["prix"]) if row.get("prix") is not None else None, row["id"], conn)
        ba = BouteilleArchivee(b.domaine_viticole, b.nom, b.type, b.annee, b.region, date.today(),
                               note=float(note) if note else None, commentaire=commentaire,
                               utilisateur_id=session["user_id"], prix=b.prix, id_archive=None, conn=conn)
        ba.sauvegarder(b.id_bouteille)
        BouteilleCave.supprimer_bouteille_cave(conn, row["bc_id"])
    return redirect(url_for("detail_cave", cave_id=cave_id))


@app.route("/bouteilles/supprimer", methods=["POST"])
def supprimer_bouteille():
    # Supprime N exemplaires d'un groupe de bouteilles sans archivage
    if "user_id" not in session:
        return redirect(url_for("login"))
    cave_id = int(request.form.get("cave_id"))
    domaine = request.form.get("domaine_viticole")
    nom = request.form.get("nom")
    type_vin = request.form.get("type")
    if type_vin and type_vin not in ALLOWED_TYPES:
        flash("Type de vin invalide")
        return redirect(url_for("detail_cave", cave_id=cave_id))
    annee = int(request.form.get("annee"))
    region = request.form.get("region")
    quantite = int(request.form.get("quantite", 1))

    c = Cave("", 0, conn=conn)
    cave = c.trouver_par_id(cave_id)
    if not cave or cave.utilisateur_id != session["user_id"]:
        flash("Action non autorisée")
        return redirect(url_for("detail_cave", cave_id=cave_id))

    # Sélectionne les bouteilles à supprimer par leurs caractéristiques
    rows = BouteilleCave.selectionner_pour_suppression(conn, cave_id, domaine, nom, type_vin, annee, region, quantite)
    for row in rows:
        BouteilleCave.supprimer_bouteille_cave(conn, row["bc_id"])
    return redirect(url_for("detail_cave", cave_id=cave_id))


@app.route("/avis")
def avis():
    # Page communautaire: vue agrégée des archives
    groupes = BouteilleArchivee.obtenir_groupes_avis_avec_photos(conn)
    return render_template("avis.html", groupes=groupes)


@app.route("/avis/details")
def avis_details():
    # Détails des avis pour un vin spécifique
    domaine = request.args.get("domaine_viticole")
    nom = request.args.get("nom")
    type_vin = request.args.get("type")
    annee = int(request.args.get("annee"))
    region = request.args.get("region")

    resume = BouteilleArchivee.obtenir_resume_avis(conn, domaine, nom, type_vin, annee, region)
    avis = BouteilleArchivee.obtenir_avis_detail(conn, domaine, nom, type_vin, annee, region)
    return render_template("avis_detail.html", domaine=domaine, nom=nom, type=type_vin, annee=annee, region=region, resume=resume, avis=avis)


if __name__ == "__main__":
    # Démarrage du serveur de développement Flask
    app.run(debug=True)
