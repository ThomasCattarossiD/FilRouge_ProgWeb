CREATE TABLE user (
    user_id CHAR(8) PRIMARY KEY,
    user_login TEXT NOT NULL,
    user_password TEXT NOT NULL,
    user_mail TEXT NOT NULL UNIQUE,
    user_date_new TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_date_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE objet (
    objet_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    description TEXT
);

CREATE TABLE inventaire (
    user_id CHAR(8) NOT NULL,
    objet_id INTEGER NOT NULL,
    quantite INTEGER NOT NULL CHECK(quantite > 0),
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE,
    FOREIGN KEY (objet_id) REFERENCES objet(objet_id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, objet_id)
);
