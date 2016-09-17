#!/usr/bin/env python2

import logging
import pykka

from mopidy import backend
from __future__ import unicode_literals
from .library import SubsonicLibraryProvider
from .playlist import SubsonicPlaylistsProvider
from .client import SubsonicRemoteClient

logger = logging.getLogger(__name__)

class SubsonicBackend(pykka.ThreadingActor, backend.Backend):

    def __init__(self, config, audio):
        super(SubsonicBackend, self).__init__()

        self.remote = SubsonicRemoteClient(
            config['subsonic']['hostname'],
            config['subsonic']['port'],
            config['subsonic']['username'],
            config['subsonic']['password'],
            config['subsonic']['ssl'],
            config['subsonic']['context'],
            config['subsonic']['legacy_auth'])

        self.config = config
        self.library = SubsonicLibraryProvider(backend=self)
        self.playback = SubsonicPlaybackProvider(audio=audio, backend=self)
        self.playlists = SubsonicPlaylistsProvider(backend=self)

        self.uri_schemes = ['subsonic']


class SubsonicPlaybackProvider(backend.PlaybackProvider):

    def translate_uri(self, uri):
        logger.debug('Getting info for track %s' % uri)
        id = uri.split('subsonic:song:')[1]
        real_uri = self.backend.remote.build_url_from_song_id(id)
        return real_uri
