from datetime import datetime


class Track(object):
    def __init__(self, data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.added_at = self.__format_time(data.get('added_at'))
        self.added_by = data['added_by']['id']

        track = data['track']

        album = track['album']
        self.album_id = album['id']
        self.album_name = album['name']
        self.album_type = album['album_type']
        self.release_date = album['release_date']

        self.artists = track['artists']
        self.artists_names = self.__get_artists_names()

        self.duration_ms = float(track['duration_ms'])
        self.is_episode = track.get('episode', False)
        self.is_explicit = track.get('explicit', False)
        self.id = track['id']
        self.name = track['name']
        self.popularity = track['popularity']
        self.preview_url = track['preview_url']
        self.type = track['type']

    def __repr__(self):
        return self.name

    
    def __format_time(self, string):
        if string:
            time = datetime.strptime(string, '%Y-%m-%dT%H:%M:%SZ')
            return time.strftime('%d-%m-%Y %H-%M-%S')
    
    def __get_artists_names(self):
        if self.artists:
            artists_names = sorted([artist['name'] for artist in self.artists])
            return ','.join(artists_names)
        return None


