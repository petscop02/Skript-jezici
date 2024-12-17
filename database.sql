/*CREATE TABLE users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email NORCHAR(255) UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password TEXT UNIQUE NOT NULL,
    choice TEXT NOT NULL,
    why TEXT NOT NULL
);*/
/*CREATE TABLE history(
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    username TEXT UNIQUE NOT NULL,
    choice TEXT NOT NULL,
    why TEXT NOT NULL,
    past INTEGER NOT NULL
);*/
SELECT * FROM users;
SELECT * FROM history;