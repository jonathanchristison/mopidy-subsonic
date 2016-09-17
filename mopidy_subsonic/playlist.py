
#!/usr/bin/env python2

import logging

from __future__ import unicode_literals
from mopidy import backend
from mopidy.models import Playlist, Ref

logger = logging.getLogger(__name__)

class SubsonicPlaylistsProvider(backend.PlaylistsProvider):
    def __init__(self, *args, **kwargs):
        super(SubsonicPlaylistsProvider, self).__init__(*args, **kwargs)
        self.remote = self.backend.remote
        self.playlists = self._get_playlists()

    def lookup(self, uri):
        logger.debug('Playlist lookup. uri = %s' % uri)
        id = uri.split("subsonic:playlist:")[1]
        try:
            id = int(id)

            return self.remote.playlist_id_to_playlist(id)
        except:
            return self.remote.get_smart_playlist(id)

    def playlist_to_ref(self, playlist):
        return Ref(
            uri=playlist.uri,
            name=playlist.name,
            type=Ref.PLAYLIST
        )

    def track_to_ref(self, track):
        return Ref(
            uri=track.uri,
            name=track.name,
            type=Ref.TRACK
        )

    def as_list(self):
        playlists = self._get_playlists()
        return [self.playlist_to_ref(playlist) for playlist in playlists]

    def get_items(self, uri):
        playlist = self.lookup(uri)
        return [self.track_to_ref(track) for track in playlist.tracks]

    def _get_playlists(self):
        smart_playlists = {'random': 'Random Albums',
                           'newest': 'Recently Added',
                           'highest': 'Top Rated',
                           'frequent': 'Most Played',
                           'recent': 'Recently Played',
                           'randomsongs': 'Random Songs'}
        playlists = self.remote.get_user_playlists()
        for type in smart_playlists.keys():
            playlists.append(
                Playlist(
                    uri=u'subsonic:playlist:%s' % type,
                    name='Smart Playlist: %s' % smart_playlists[type]))

        return playlists
