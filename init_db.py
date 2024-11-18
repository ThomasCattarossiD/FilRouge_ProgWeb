import sqlite3

# Nom de la base de données
DATABASE = '2024_M1.db'

# Lire le fichier schema.sql pour récupérer les instructions SQL
with open('schema.sql', 'r') as f:
    schema_sql = f.read()

# Créer la base de données et exécuter le script SQL
with sqlite3.connect(DATABASE) as conn:
    cursor = conn.cursor()
    cursor.executescript(schema_sql)  # Exécuter tout le script SQL
    conn.commit()

print("La base de données a été initialisée avec succès.")
