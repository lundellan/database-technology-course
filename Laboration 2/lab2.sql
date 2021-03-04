PRAGMA foreign_keys=OFF;

DROP TABLE IF EXISTS theaters;
DROP TABLE IF EXISTS movies;
DROP TABLE IF EXISTS screenings;
DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS users;

PRAGMA foreign_keys=ON;

CREATE TABLE theaters (
	theaterName		TEXT,
	capacity		REAL,
	PRIMARY KEY 	(theaterName)
);

CREATE TABLE movies (
	imdbKey			TEXT,
	title			TEXT,
	runningTime		REAL,
	productionYear	REAL,
	PRIMARY KEY 	(imdbKey)
);

CREATE TABLE screenings (
	time			TIME,
	date			DATE,
	theaterName		TEXT,
	imdbKey			TEXT,
	PRIMARY KEY 	(time, date),
	FOREIGN KEY		(theaterName) REFERENCES theaters(theaterName),
	FOREIGN KEY		(imdbKey) REFERENCES movies(imdbKey)
);

CREATE TABLE tickets (
	id				TEXT DEFAULT (lower(hex(randomblob(16)))),
	theaterName		TEXT,
	imdbKey			TEXT,
	username		TEXT,
	time			TIME,
	date			DATE,
	PRIMARY KEY 	(id),
	FOREIGN KEY		(theaterName) REFERENCES theaters(theaterName),
	FOREIGN KEY		(imdbKey) REFERENCES movies(imdbKey)
	FOREIGN KEY		(username) REFERENCES users(username)
	FOREIGN KEY		(time, date) REFERENCES screenings(time, date)
);

CREATE TABLE users (
	username		TEXT,
	fullName		TEXT,
	password		TEXT,
	PRIMARY KEY 	(username)
);

INSERT INTO theaters (theaterName, capacity)
VALUES ('Filmstaden Helsingborg', 200), 
('Filmstaden Lund', 300), 
('Royal', 500), 
('Kino', 70), 
('Biohuset', 40);

INSERT INTO movies (imdbKey, title, runningTime, productionYear)
VALUES ('tt1375666', 'Inception', 148, 2010),
('tt0068646', 'The Godfather', 175, 1972),
('tt0198781', 'Monsters Inc', 92, 2001),
('tt1467304', 'The Human Centipede', 92, 2009),
('tt7131622', 'Once Upon a Time in Hollywood', 161, 2019);

INSERT INTO screenings (time, date, theaterName, imdbKey)
VALUES ('12:30', '2021-02-09', 'Filmstaden Helsingborg', 'tt1375666'),
('20:00', '2021-02-10', 'Filmstaden Lund', 'tt0068646'),
('17:00', '2021-02-11', 'Biohuset', 'tt0198781'),
('19:00', '2021-02-12', 'Royal', 'tt7131622'),
('21:00', '2021-02-13', 'Biohuset', 'tt1467304'),
('17:00', '2021-02-14', 'Kino', 'tt1467304');

INSERT INTO users (username, fullName, password)
VALUES ('Killa1963420', 'Brad Pitt', '123456'),
('XxLordDudexX', 'Leonardo DiCaprio', 'qwerty'),
('dutchessofnewjersey', 'Margot Robbie', 'iloveyou'),
('oboy1939', 'Per Albin Hansson', 'dragon'),
('travisb', 'Robert De Niro', 'princess');