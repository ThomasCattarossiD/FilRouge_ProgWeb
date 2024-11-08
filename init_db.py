import sqlite3

DATABASE = '2024_M1.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE user (
            user_id CHAR(8) PRIMARY KEY,
            user_login TEXT NOT NULL,
            user_password TEXT NOT NULL,
            user_mail TEXT NOT NULL UNIQUE,
            user_date_new TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_date_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
