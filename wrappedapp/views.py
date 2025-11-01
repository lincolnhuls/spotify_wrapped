import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from django.shortcuts import render, redirect
from dotenv import load_dotenv
from wrappedapp.models import SpotifyToken
from django.utils import timezone
from datetime import timedelta


load_dotenv()

def get_spotify_oauth():
    return SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope=os.getenv("SPOTIPY_SCOPE"),
    )

def get_spotipy_client(request):
    access_token = request.session.get('access_token')
    if not access_token:
        return None
    return spotipy.Spotify(auth=access_token)

def get_user_display_name(sp):
    try:
        return sp.current_user()['display_name']
    except Exception:
        return None

# Create your views here.
def home(request): 
    return render(request, 'wrappedapp/home.html')

def login(request): 
    sp_oauth = get_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

def callback(request): 
    sp_oauth = get_spotify_oauth()
    code = request.GET.get('code')
    token_info = sp_oauth.get_access_token(code)
    access_token = token_info['access_token']
    sp = spotipy.Spotify(auth=access_token)
    user_info = sp.current_user()
    spotify_user_id = user_info['id']

    existing_token = SpotifyToken.objects.filter(spotify_user_id=spotify_user_id).first()
    if existing_token:
        existing_token.access_token = token_info['access_token']
        existing_token.refresh_token = token_info['refresh_token']
        existing_token.token_type = token_info['token_type']
        existing_token.expires_at = timezone.now() + timedelta(seconds=token_info['expires_in'])
        existing_token.save()
    else:
        SpotifyToken.objects.create(
            spotify_user_id=spotify_user_id,
            access_token=token_info['access_token'],
            refresh_token=token_info['refresh_token'],
            token_type=token_info['token_type'],
            expires_at=timezone.now() + timedelta(seconds=token_info['expires_in'])
        )

    request.session['spotify_user_id'] = spotify_user_id
    request.session['access_token'] = access_token
    
    user_name = get_user_display_name(sp)

    return render(request, 'wrappedapp/callback.html', context={'user': user_info, 'user_name': user_name})

def dashboard(request): 
    time = request.GET.get("time_range")
    songs = request.GET.get("limit")
    if time is None:
        time = "medium_term"
    if songs is None:
        songs = 5
    sp = get_spotipy_client(request)
    if not sp:
        return redirect('home')
    top_songs = sp.current_user_top_tracks(limit=songs, time_range=time)
    user_name = get_user_display_name(sp)
    context = {'range': time, 'tracks': top_songs['items'], 'limit': songs, 'user_name': user_name}
    return render(request, 'wrappedapp/dashboard.html', context)

def artists(request):
    artists = []
    time = request.GET.get("time_range")
    if time is None:
        time = "medium_term"
    sp = get_spotipy_client(request)
    if not sp:
        return redirect('home')
    user_name = get_user_display_name(sp)
    top_songs = sp.current_user_top_tracks(time_range=time)
    for song in top_songs['items']:
        artist_id = song['artists'][0]['id']
        if sp.artist(artist_id) not in artists:
            artists.append(sp.artist(artist_id))
    # This is faster but I don't know if I like it, my version pulls the artists from top songs
    # top_artists = sp.current_user_top_artists()
    # for artist in top_artists['items']:
    #     artists.append(artist)
    context = {'range': time, 'user_name': user_name, 'artists': artists}
    return render(request, 'wrappedapp/artists.html', context)

def genres(request):
    return render(request, 'wrappedapp/genres.html')

def logout(request):
    request.session.flush() 
    return redirect('home')  
