import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd

# Spotify API credentials
CLIENT_ID = ""
CLIENT_SECRET = ""
REDIRECT_URI = ""
USERNAME = ""

#Authentication with Spotify API
scope = "user-top-read user-read-recently-played playlist-modify-public"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=scope, username=USERNAME))

#Fetch top tracks (short term; last 4 weeks)
def get_top_tracks(limit=10):
    results = sp.current_user_top_tracks(time_range='long_term', limit=limit)
    top_tracks = [(track['name'], track['id']) for track in results['items']]
    return top_tracks

#Fetch recently played tracks
def get_recently_played(limit=20):
    results = sp.current_user_recently_played(limit=limit)
    track_counts = {}
    for item in results['items']:
        track_id = item['track']['id']
        track_counts[track_id] = track_counts.get(track_id, 0) + 1
    
    #Sort tracks by play count
    sorted_tracks = sorted(track_counts.items(), key=lambda x: x[1], reverse=True)
    return [(sp.track(track[0])['name'], track[0]) for track in sorted_tracks[:10]]

#Get similar song recommendations
def get_recommendations(seed_tracks, limit=10):
    if not seed_tracks:
        print("🚨 No seed tracks found! Skipping recommendations.")
        return []
    
    seed_track_ids = [track[1] for track in seed_tracks[:4]]  # Use up to 5 seed tracks
    print(f"🔍 Using Seed Tracks: {seed_track_ids}")  # Debugging

    try:
        recommendations = sp.recommendations(seed_tracks=seed_track_ids, limit=limit)
        return [(track['name'], track['id']) for track in recommendations['tracks']]
    except spotipy.exceptions.SpotifyException as e:
        print(f"❌ Error fetching recommendations: {e}")
        return []

#Get or create "Most Played + Recommendations" playlist
def get_or_create_playlist(playlist_name="Most Played & Recommended"):
    playlists = sp.current_user_playlists()
    for playlist in playlists['items']:
        if playlist['name'] == playlist_name:
            return playlist['id']
    
    #Create playlist if it doesn't exist
    new_playlist = sp.user_playlist_create(user=USERNAME, name=playlist_name, public=True)
    return new_playlist['id']

#Update playlist with most played and recommended tracks
def update_playlist():
    playlist_id = get_or_create_playlist()

    top_tracks = get_top_tracks()
    recent_tracks = get_recently_played()
    recommended_tracks = get_recommendations(top_tracks + recent_tracks, limit=10)

    #Merge lists and remove duplicates
    all_tracks = list(dict.fromkeys([track[1] for track in top_tracks + recent_tracks + recommended_tracks]))

    #Update playlist
    sp.playlist_replace_items(playlist_id, all_tracks)
    print(f"Playlist updated, with {len(all_tracks)} songs added!")

#Test functions
top_tracks = get_top_tracks()
recent_tracks = get_recently_played()
recommended_tracks = get_recommendations(top_tracks + recent_tracks, limit=10)

print("🎵 Top Tracks:", top_tracks)  
print("Recently Played Tracks:", recent_tracks)  
print("Recommended Tracks:", recommended_tracks)  

#Main function
if __name__ == "__main__":
    update_playlist()