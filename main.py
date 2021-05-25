from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
import pprint


def read_billboard_site(date="2004-06-19"):
    url = f'https://www.billboard.com/charts/hot-100/{date}'

    response = requests.get(url)
    billboard_site = response.text

    soup = BeautifulSoup(billboard_site, "html.parser")

    print(soup.title)

    songs_tags = soup.find_all(name="span", class_="chart-element__information__song text--truncate color--primary")
    artists_tags = soup.find_all(name="span",
                                 class_="chart-element__information__artist text--truncate color--secondary")

    artists = [tag.getText() for tag in artists_tags]
    songs = [tag.getText() for tag in songs_tags]

    print(artists)
    print(songs)
    return songs, artists


def read_metalstorm(year=2020):
    url = f'http://www.metalstorm.net/bands/albums_top.php?album_year={year}'
    response = requests.get(url)

    ms_site = response.text

    soup = BeautifulSoup(ms_site, "html.parser")
    print(soup.title)

    artist_tags = soup.select(selector="b a")
    songs_tags = soup.select(selector="td.hidden-xs a")

    artists = [tag.getText() for tag in artist_tags]
    songs = [tag.getText() for tag in songs_tags]

    print(artists)
    print(songs)
    return songs, artists


def spotify_login():
    scope = "playlist-modify-private"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    return sp


def create_playlist(sp_client: spotipy.Spotify, name='1990-08-24 Billboard 100'):
    response = sp_client.user_playlist_create('luintinuviel', name, public=False)
    playlist_id = response['id']
    return playlist_id



def find_song(sp_client: spotipy.Spotify, song, artist):
    query = f'{song} artist:{artist}'
    search_result = sp_client.search(query, type='track', limit=1)
    try:
        uri = search_result['tracks']['items'][0]['uri']
    except Exception as e:
        print(f"Error:\n{e}")
        print(f"Can't find song: {artist} - {song}")
        return None
    else:
        print(f"Found uri for: {artist} - {song} = {uri}")
        return uri

def find_album(sp_client: spotipy.Spotify, album, artist):
    query = f'album:{album} artist:{artist}'
    search_result = sp_client.search(query, type='album', limit=1)
    try:
        uri = search_result['albums']['items'][0]['uri']
    except Exception as e:
        print(f"Error:\n{e}")
        print(f"Can't find album: {artist} - {album}")
        return None
    else:
        print(f"Found uri for: {artist} - {album} = {uri}")
        return uri

def add_songs(sp_client: spotipy.Spotify, playlist_id, tracks):
    try:
        sp_client.playlist_add_items(playlist_id=playlist_id, items=tracks)
    except Exception as e:
        print(f"Error:\n{e}")

def prepare_playlist(sp_client: spotipy.Spotify, playlist_id, songs, artists):
    songs_uri = []
    for song, artist in zip(songs, artists):
        uri = find_song(sp_client, song, artist)
        if uri:
            print(f"Received uri from function for {artist} - {song} = {uri}")
            songs_uri.append(uri)
        elif "Featuring" in artist:
            artist_split = artist.split(" ")
            shortened_artist = ""
            for word in artist_split:
                if word == "Featuring":
                    break
                else:
                    if shortened_artist == "":
                        shortened_artist += word
                    else:
                        shortened_artist += f" {word}"
            print(f"Trying to find artist with shortened artist name: {shortened_artist}")
            uri = find_song(sp_client, song, shortened_artist)
            if uri:
                print(f"Received uri from function for {artist} - {song} = {uri}")
                songs_uri.append(uri)
    add_songs(sp_client, playlist_id, songs_uri)


def prepare_metalstorm_playlist(sp_client: spotipy.Spotify, playlist_id, albums, artists):
    albums_uri = []
    for album, artist in zip(albums, artists):
        uri = find_album(sp_client, album, artist)
        if uri:
            print(f"Received uri from function for {artist} - {album} = {uri}")
            tracks = find_album_tracks(sp_client, uri)
            if tracks:
                add_songs(sp_client, playlist_id, tracks)

    # add_albums(sp_client, playlist_id, albums_uri)

def find_album_tracks(sp_client: spotipy.Spotify, uri):
    tracks_uris = []
    try:
        tracks = sp_client.album_tracks(uri)['items']
    except Exception as e:
        print(f"Error:\n{e}")
    else:
        for track in tracks:
            print(track['uri'])
            tracks_uris.append(track['uri'])
    finally:
        return tracks_uris

if __name__ == "__main__":
    # date = str(input("Which year do You want to travel to? Type the date in this format YYYY-MM-DD:     "))
    # songs, artists = read_billboard_site(date)
    # sp = spotify_login()
    # playlist_id = create_playlist(sp, name=f'{date} Billboard 100')
    # prepare_playlist(sp, playlist_id, songs, artists)

    albums, artists = read_metalstorm(2020)
    sp = spotify_login()
    playlist_id = create_playlist(sp, name=f'Metalstorm best albums of 2020')
    prepare_metalstorm_playlist(sp, playlist_id, albums, artists)