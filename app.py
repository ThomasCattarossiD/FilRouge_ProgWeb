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
            return redirect(url_for('profile'))
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

if __name__ == '__main__':
    app.run(debug=True)