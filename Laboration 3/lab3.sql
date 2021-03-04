PRAGMA foreign_keys=OFF;

DROP TABLE IF EXISTS theaters;
DROP TABLE IF EXISTS movies;
DROP TABLE IF EXISTS screenings;
DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS users;

PRAGMA foreign_keys=ON;

CREATE TABLE theaters (
	theater			TEXT,
	capacity		INT,
	UNIQUE 			(theater),
	PRIMARY KEY 	(theater)
);

CREATE TABLE movies (
	imdbKey			TEXT,
	title			TEXT,
	runningTime		INT,
	year			INT,
	UNIQUE 			(imdbKey),
	PRIMARY KEY 	(imdbKey)
);

CREATE TABLE screenings (
	performanceId   TEXT DEFAULT (lower(hex(randomblob(16)))),
	time			TIME,
	date			DATE,
	remainingSeats	INT,
	theater			TEXT,
	imdbKey			TEXT,
	PRIMARY KEY 	(time, date, theater, imdbKey),
	FOREIGN KEY		(theater) REFERENCES theaters(theater),
	FOREIGN KEY		(imdbKey) REFERENCES movies(imdbKey)
);

CREATE TABLE tickets (
	id				TEXT DEFAULT (lower(hex(randomblob(16)))),
	theater			TEXT,
	imdbKey			TEXT,
	username		TEXT,
	time			TIME,
	date			DATE,
	PRIMARY KEY 	(id),
	FOREIGN KEY		(theater) REFERENCES theaters(theater),
	FOREIGN KEY		(imdbKey) REFERENCES movies(imdbKey)
	FOREIGN KEY		(username) REFERENCES users(username)
	FOREIGN KEY		(time, date) REFERENCES screenings(time, date)
);

CREATE TABLE users (
	username		TEXT,
	fullName		TEXT,
	pwd				VARBINARY,
	UNIQUE 			(username),
	PRIMARY KEY 	(username)
);



INSERT INTO theaters (theater, capacity)
VALUES ('Filmstaden Helsingborg', 200),
('Filmstaden Lund', 300),
('Royal', 500),
('Kino', 70),
('Biohuset', 40);

INSERT INTO movies (imdbKey, title, runningTime, year)
VALUES ('tt1375666', 'Inception', 148, 2010),
('tt0068646', 'The Godfather', 175, 1972),
('tt0198781', 'Monsters Inc', 92, 2001),
('tt1467304', 'The Human Centipede', 92, 2009),
('tt7131622', 'Once Upon a Time in Hollywood', 161, 2019);


INSERT INTO screenings (time, date, remainingSeats, theater, imdbKey)
VALUES ('12:30', '2021-02-09', 200, 'Filmstaden Helsingborg', 'tt1375666');

INSERT INTO users (username, fullName, pwd)
VALUES ('Killa1963420', 'Brad Pitt', '123456'),
('XxLordDudexX', 'Leonardo DiCaprio', 'qwerty'),
('dutchessofnewjersey', 'Margot Robbie', 'iloveyou'),
('oboy1939', 'Per Albin Hansson', 'dragon'),
('travisb', 'Robert De Niro', 'princess');
