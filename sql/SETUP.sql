BEGIN;

CREATE SCHEMA metrics_band;

SET search_path TO metrics_band, public;

CREATE TABLE enduser(
    enduser_id SERIAL PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE genre(
    genre_id SERIAL PRIMARY KEY,
	name VARCHAR(40) NOT NULL UNIQUE
);

CREATE TABLE artist(
    artist_id SERIAL PRIMARY KEY,
	name VARCHAR(40),
    spotify_id VARCHAR(40) UNIQUE,
	genre_id INT REFERENCES genre(genre_id)
);

CREATE TABLE song(
    song_id SERIAL PRIMARY KEY,
	spotify_id VARCHAR(40) UNIQUE,
	artist_id INT REFERENCES artist(artist_id),
	duration INT,
	features_populated BOOLEAN,
	key INT,
	mode INT,
	time_signature INT,
	acousticness REAL,
	danceability REAL,
	energy REAL,
	instrumentalness REAL,
	liveness REAL,
	loudness REAL,
	speechiness REAL,
	valence REAL,
	tempo REAL
);

CREATE TABLE listen_history(
    listen_id SERIAL PRIMARY KEY,
    enduser_id INT REFERENCES enduser(enduser_id),
	song_id INT REFERENCES song(song_id),
	timestamp TIMESTAMP default current_timestamp
);

COMMIT;
/* ROLLBACK; */