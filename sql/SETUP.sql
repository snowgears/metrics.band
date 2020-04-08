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

CREATE VIEW metrics_band.select_all_view AS
select lh.listen_id,lh.timestamp,eu.email,
		s.song_name, ar.name as artist_name,
		al.album_name, al.release_date,
		ge.name as genre_name,
		s.duration, s.key, s.mode, s.acousticness, s.danceability, s.energy, s.instrumentalness, s.loudness, s.speechiness, s.valence, s.tempo
from metrics_band.listen_history lh
join metrics_band.enduser eu on lh.enduser_id=eu.enduser_id
join metrics_band.song s on lh.song_id=s.song_id
join metrics_band.song_artist sa on lh.song_id=sa.song_id
join metrics_band.album al on al.album_id=s.album_id
join metrics_band.artist ar on ar.artist_id=sa.artist_id
join metrics_band.artist_genre ag on ag.artist_id=ar.artist_id
join metrics_band.genre ge on ge.genre_id=ag.genre_id
order by lh.listen_id;

COMMIT;
-- ROLLBACK;