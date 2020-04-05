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

CREATE TABLE metrics_band.genre_set(
    genre_set_id SERIAL PRIMARY KEY,
	genre1 INT REFERENCES genre(genre_id),
	genre2 INT REFERENCES genre(genre_id),
	genre3 INT REFERENCES genre(genre_id),
	genre4 INT REFERENCES genre(genre_id),
	genre5 INT REFERENCES genre(genre_id),
	genre6 INT REFERENCES genre(genre_id),
	genre7 INT REFERENCES genre(genre_id),
	genre8 INT REFERENCES genre(genre_id)
);

CREATE TABLE metrics_band.artist(
    artist_id SERIAL PRIMARY KEY,
	name VARCHAR(40),
    spotify_id VARCHAR(40) UNIQUE,
	genre_set_id INT REFERENCES genre_set(genre_set_id)
);

CREATE TABLE metrics_band.artist_set(
    artist_set_id SERIAL PRIMARY KEY,
	artist1 INT REFERENCES artist(artist_id),
	artist2 INT REFERENCES artist(artist_id),
	artist3 INT REFERENCES artist(artist_id),
	artist4 INT REFERENCES artist(artist_id),
	artist5 INT REFERENCES artist(artist_id),
	artist6 INT REFERENCES artist(artist_id),
	artist7 INT REFERENCES artist(artist_id),
	artist8 INT REFERENCES artist(artist_id)
);

CREATE TABLE metrics_band.song(
    song_id SERIAL PRIMARY KEY,
	spotify_id VARCHAR(40) UNIQUE,
	artist_set_id INT REFERENCES artist_set(artist_set_id),
	duration INT,
	features_populated BOOLEAN,
	popularity INT,
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

CREATE TABLE metrics_band.listen_history(
    listen_id SERIAL PRIMARY KEY,
    enduser_id INT REFERENCES enduser(enduser_id),
	song_id INT REFERENCES song(song_id),
	timestamp TIMESTAMP default current_timestamp
);

COMMIT;
/* ROLLBACK; */