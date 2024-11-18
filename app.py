from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
import sqlite3
import random
import string

app = Flask(__name__)
app.secret_key = 'your_secret_key'
bcrypt = Bcrypt(app)
DATABASE = '2024_M1.db'

def query_db(query, args=(), one=False):
    with sqlite3.connect(DATABASE) as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(query, args)
        rv = cur.fetchall()
        con.commit()
        cur.close()
        return (rv[0] if rv else None) if one else rv

# Fonction de génération d'un user_id de 8 caractères aléatoires
def generate_user_id():
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choices(characters, k=8))

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        # Générer un user_id unique
        user_id = generate_user_id()
        
        # Vérifier si le nom d'utilisateur ou l'email existe déjà
        user = query_db('SELECT * FROM user WHERE user_login = ? OR user_mail = ?', [username, email], one=True)
        if user:
            flash("Le nom d'utilisateur ou l'email existe déjà.")
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        query_db('INSERT INTO user (user_id, user_login, user_password, user_mail) VALUES (?, ?, ?, ?)', 
                 [user_id, username, hashed_password, email])
        flash("Enregistrement réussi. Vous pouvez maintenant vous connecter.")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form['identifier']  # Peut être user_login ou email
        password = request.form['password']
        
        # Rechercher par nom d'utilisateur ou email
        user = query_db('SELECT * FROM user WHERE user_login = ? OR user_mail = ?', [identifier, identifier], one=True)
        if user is None:
            flash("Identifiant ou email incorrect.")
            return redirect(url_for('login'))

        if bcrypt.check_password_hash(user['user_password'], password):
            session['username'] = user['user_login']
            flash("Connexion réussie.")
            return redirect(url_for('inventaire'))
        else:
            flash("Mot de passe incorrect.")
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/profile')
def profile():
    if 'username' not in session:
        flash("Vous devez vous connecter pour accéder à cette page.")
        return redirect(url_for('login'))
    return f"Bonjour, {session['username']}! Bienvenue sur votre profil."

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Vous avez été déconnecté.")
    return redirect(url_for('login'))

@app.route('/inventaire', methods=['GET'])
def inventaire():
    if 'username' not in session:
        flash("Vous devez vous connecter pour accéder à votre inventaire.")
        return redirect(url_for('login'))
    
    user = query_db('SELECT * FROM user WHERE user_login = ?', [session['username']], one=True)
    user_id = user['user_id']
    inventaire_items = query_db('''
        SELECT i.objet_id, o.nom, o.description, i.quantite 
        FROM Inventaire i
        JOIN Objet o ON i.objet_id = o.objet_id
        WHERE i.user_id = ?
    ''', [user_id])
    return render_template('inventaire.html', inventaire_items=inventaire_items)

@app.route('/ajouter_objet', methods=['POST'])
def ajouter_objet():
    if 'username' not in session:
        flash("Vous devez vous connecter pour ajouter des objets.")
        return redirect(url_for('login'))
    
    objet_nom = request.form['objet_nom']
    description = request.form['description']
    quantite = int(request.form['quantite'])

    # Vérifier si l'objet existe déjà
    objet = query_db('SELECT * FROM Objet WHERE nom = ?', [objet_nom], one=True)
    if not objet:
        query_db('INSERT INTO Objet (nom, description) VALUES (?, ?)', [objet_nom, description])
        objet = query_db('SELECT * FROM Objet WHERE nom = ?', [objet_nom], one=True)
    
    objet_id = objet['objet_id']
    user = query_db('SELECT * FROM user WHERE user_login = ?', [session['username']], one=True)
    user_id = user['user_id']

    # Vérifier si l'utilisateur a déjà cet objet
    inventaire_item = query_db('SELECT * FROM Inventaire WHERE user_id = ? AND objet_id = ?', [user_id, objet_id], one=True)
    if inventaire_item:
        flash("Cet objet est déjà dans l'inventaire. Utilisez la mise à jour pour changer la quantité.")
    else:
        query_db('INSERT INTO Inventaire (user_id, objet_id, quantite) VALUES (?, ?, ?)', [user_id, objet_id, quantite])
        flash("Objet ajouté à l'inventaire.")
    
    return redirect(url_for('inventaire'))

@app.route('/supprimer_objet/<int:objet_id>', methods=['POST'])
def supprimer_objet(objet_id):
    if 'username' not in session:
        flash("Vous devez vous connecter pour gérer votre inventaire.")
        return redirect(url_for('login'))

    user = query_db('SELECT * FROM user WHERE user_login = ?', [session['username']], one=True)
    user_id = user['user_id']
    query_db('DELETE FROM Inventaire WHERE user_id = ? AND objet_id = ?', [user_id, objet_id])
    flash("Objet supprimé de l'inventaire.")
    return redirect(url_for('inventaire'))

@app.route('/mettre_a_jour_objet/<int:objet_id>', methods=['POST'])
def mettre_a_jour_objet(objet_id):
    if 'username' not in session:
        flash("Vous devez vous connecter pour gérer votre inventaire.")
        return redirect(url_for('login'))

    nouvelle_quantite = int(request.form['quantite'])
    if nouvelle_quantite <= 0:
        flash("La quantité doit être strictement positive.")
        return redirect(url_for('inventaire'))

    user = query_db('SELECT * FROM user WHERE user_login = ?', [session['username']], one=True)
    user_id = user['user_id']
    query_db('UPDATE Inventaire SET quantite = ? WHERE user_id = ? AND objet_id = ?', [nouvelle_quantite, user_id, objet_id])
    flash("Quantité de l'objet mise à jour.")
    return redirect(url_for('inventaire'))

if __name__ == '__main__':
    app.run(debug=True)
