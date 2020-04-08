BEGIN;

CREATE SCHEMA metrics_band;

SET search_path TO metrics_band, public;

CREATE TABLE metrics_band.enduser(
    enduser_id SERIAL PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE metrics_band.genre(
    genre_id SERIAL PRIMARY KEY,
	name VARCHAR(40) NOT NULL UNIQUE
);

CREATE TABLE metrics_band.artist(
    artist_id SERIAL PRIMARY KEY,
	name VARCHAR(40),
    spotify_id VARCHAR(40) UNIQUE
);

CREATE TABLE metrics_band.artist_genre(
    artist_genre_id SERIAL PRIMARY KEY,
	artist_id INT REFERENCES artist(artist_id),
	genre_id INT REFERENCES genre(genre_id),
	CONSTRAINT CST_ARTIST_GENRE UNIQUE (artist_id, genre_id)
);

CREATE TABLE metrics_band.album(
    album_id SERIAL PRIMARY KEY,
	spotify_id VARCHAR(40) UNIQUE,
	album_name VARCHAR(60),
	release_date DATE
);

CREATE TABLE metrics_band.song(
    song_id SERIAL PRIMARY KEY,
	spotify_id VARCHAR(40) UNIQUE,
	song_name VARCHAR(60),
	album_id INT REFERENCES album(album_id),
	duration INT,
	features_populated BOOLEAN,
	key INT,
	mode INT,
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

CREATE TABLE metrics_band.song_artist(
   	song_artist_id SERIAL PRIMARY KEY,
	song_id INT REFERENCES song(song_id),
	artist_id INT REFERENCES artist(artist_id),
	CONSTRAINT CST_SONG_ARTIST UNIQUE (song_id,artist_id)
);

CREATE TABLE metrics_band.listen_history(
    listen_id SERIAL PRIMARY KEY,
    enduser_id INT REFERENCES enduser(enduser_id),
	song_id INT REFERENCES song(song_id),
	timestamp TIMESTAMP default current_timestamp
);

COMMIT;
-- ROLLBACK;