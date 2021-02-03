class Playlist(object):

    def __init__(self, data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.is_collaborative = data['collaborative'] # boolean
        self.is_public = data['public'] # boolean
         
        self.description = data['description'] # string
        self.name = data['name'] # string
        self.id = data['id'] # string

        self.images = data['images'] # dict list
        self.owner = data['owner'] # dict list

        self.track_count = data['tracks']['total'] # int

    def __len__(self):
        if self.track_count:
            return self.track_count
        return None

    def __repr__(self):
        return self.name
