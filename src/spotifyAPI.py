import requests
from time import sleep

#returns a tuple (boolean for is active, data for the json data if available)
def get_current_track_info(token):
    headers = {
        'Authorization': f"Bearer {token}"
    }

    response = requests.get('https://api.spotify.com/v1/me/player/currently-playing', headers=headers)
    if response.content:
        track = response.json()

        track_id = track['item']['id']
        progress = track['progress_ms']
        track_uri = track['item']['uri']
        track_duration = track['item']['duration_ms']
        is_playing = track['is_playing']

        current_track_info = {
            "id": track_id,
            "progress": progress,
            "uri": track_uri,
            "duration": track_duration,
            "is_playing":is_playing
        }

        return True, current_track_info
    else:
        return False, None

def jump_to_progress(token, progress):
    headers = {
        'Authorization': f"Bearer {token}"
    }
    url ='https://api.spotify.com/v1/me/player/seek'
    query = f'?position_ms={progress}'
    query_url = url + query
    requests.put(url=query_url, headers=headers)

#need to test if this works
def jump_to_song(token, song_uri):
    headers = {
        'Authorization': f"Bearer {token}",
        'Content-Type': 'application/json'
    }
    data = {
        'context_uri': song_uri
    }
    requests.put(url='https://api.spotify.com/v1/me/player/play', headers=headers, data=data)

#unfortunately, spotify api doesnt differentiate between "queue" and "next up"
def get_queue(token):
    headers = {
        'Authorization': f"Bearer {token}"
    }

    response = requests.get('https://api.spotify.com/v1/me/player/queue', headers=headers)
    if response.content:
        response = response.json()['queue']
        queue = []
        for x in range(len(response)):
            if response[x]['uri'] != response[-1]['uri']:
                queue.append(response[x]['uri'])
        return queue
    else:
        print('error getting queue. Trying again in 1 second')
        return get_queue(token)

def add_to_queue(token, song_uri):
    headers = {
        'Authorization': f"Bearer {token}"
    }
    url = 'https://api.spotify.com/v1/me/player/queue'
    query = f'?uri={song_uri}' 
    query_url = url + query
    requests.post(url=query_url, headers=headers)

def skip_to_next(token):
    headers = {
        'Authorization': f"Bearer {token}"
    }
    requests.post('https://api.spotify.com/v1/me/player/next', headers=headers)

def pause(token):
    headers = {
        'Authorization': f"Bearer {token}",
    }
    requests.put(url='https://api.spotify.com/v1/me/player/pause', headers=headers)

def resume(token):
    headers = {
        'Authorization': f"Bearer {token}",
        'Content-Type': 'application/json'
    }
    requests.put(url='https://api.spotify.com/v1/me/player/play', headers=headers)