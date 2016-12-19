from __future__ import unicode_literals
import logging
from mopidy import models

logger = logging.getLogger(__name__)

ROOT_DIR = models.Ref.directory(
    uri='subsonic:directory', name='Subsonic')

_ROOT_DIR_CONTENTS = [
    models.Ref.directory(
        uri='subsonic:artists', name='Artists'),
    models.Ref.directory(
        uri='subsonic:debug', name='debug'),
]


def _get_artist_albums(remote, uri):
    artist_id = uri.split(':')[2]

    albums = remote.id_to_albums(artist_id)
    return albums


def _album_to_ref(album):
    name = album.get('title', 'Unknown Album')
    uri = 'subsonic:album:%s' % album.get('id')
    return models.Ref.directory(uri=uri, name=name)


def _track_to_ref(remote, track, with_track_no=False):
    name = ''
    try:
        if with_track_no and track.get('track') > 0:
            name = '%d - ' % track.get('track')
        name += track.get('title', 'Unknown Title')
        uri = 'subsonic://%s' % track.get('id')
    except:
        uri = track.uri
        name = track.name
    return models.Ref.track(uri=uri, name=name)


def _get_artist_tracks(remote, uri):
    artist_id = uri.split(':')[2]
    tracks = remote.get_tracks_by_artist_id(artist_id)
    return tracks


def _browse_artist_all_tracks(remote, uri):
    refs = []
    for track in _get_artist_tracks(remote, uri):
        trackref = _track_to_ref(remote, track)
        refs.append(trackref)
    return refs


def _get_album_tracks(remote, uri):
    album_id = uri.split(':')[2]

    tracks = remote.id_to_dir(album_id)
    return tracks


def _browse_album(remote, uri):
    refs = []
    for track in _get_album_tracks(remote, uri):
        trackref = _track_to_ref(remote, track, True)
        refs.append(trackref)
    return refs


def _browse_artist(remote, uri):
        refs = []
        for album in _get_artist_albums(remote, uri):
            refs.append(_album_to_ref(album))
            refs.sort(key=lambda ref: ref.name)
        if len(refs) > 0:
            refs.insert(0, models.Ref.directory(uri=uri + ':all',
                                                name='All Tracks'))
            return refs
        else:
            # Show all tracks if no album is available
            return _browse_artist_all_tracks(remote, uri)


def _artist_to_ref(artist):
    artist_name = next(iter(artist.artists))
    if artist_name.name:
        name = artist_name.name
    else:
        name = 'Unknown artist'

    artist_id = artist.uri.split('//')[-1]
    uri = 'subsonic:artist:%s' % artist_id
    return models.Ref.directory(uri=uri, name=name)


def _browse_artists(remote):
    refs = []
    for artist in remote.get_artists():
        refs.append(_artist_to_ref(artist))
        refs.sort(key=lambda ref: ref.name)
    return refs


def browse(remote, uri):

    parts = uri.split(':')

    logger.debug('GOT URI |%s|' % uri)

    if uri == ROOT_DIR.uri:
        return _ROOT_DIR_CONTENTS
    if uri == 'subsonic:artists':
        return _browse_artists(remote)

    if len(parts) == 3 and parts[1] == 'artist':
        return _browse_artist(remote, uri)

    if len(parts) == 3 and parts[1] == 'album':
        return _browse_album(remote, uri)

    if len(parts) == 4 and parts[1] == 'artist' and parts[3] == 'all':
        return _browse_artist_all_tracks(remote, uri)
