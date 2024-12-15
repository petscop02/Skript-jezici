/*CREATE TABLE users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email NORCHAR(255) UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password TEXT UNIQUE NOT NULL,
    choice TEXT NOT NULL
);*/
/*CREATE TABLE history(
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    username TEXT UNIQUE NOT NULL,
    past INTEGER NOT NULL
);*/
--INSERT INTO users(email,username,password,choice) VALUES('dimitrijegajic55@gmail.com','dimi','pass','Arduino Mega'); --dodavanje korisnika
--UPDATE users SET email='dimitrijegajic55@gmail.com' WHERE id=1; slucajno sam stavio > umesto .
--INSERT INTO users(email,username,password,choice) VALUES('email@email.com','test','pa','test'); -- test dodavanje drugog korisnika
SELECT * FROM users;
SELECT * FROM history;