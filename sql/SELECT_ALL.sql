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