import requests
from time import sleep

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'

def get_current_track_info(token):
    # should handle if no track is being played
    headers = {
        'Authorization': f"Bearer {token}"
    }

    response = requests.get('https://api.spotify.com/v1/me/player', headers=headers)
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

    return current_track_info

def jump_to_progress(token, progress):
    headers = {
        'Authorization': f"Bearer {token}"
    }
    url ='https://api.spotify.com/v1/me/player/seek'
    query = f'?position_ms={progress}'
    query_url = url + query
    requests.put(url=query_url, headers=headers)

#unfortunately, spotify api doesnt differentiate between "queue" and "next up"
def get_queue(token, original_song_uri):
    queue = []
    headers = {
        'Authorization': f"Bearer {token}"
    }

    response = requests.get('https://api.spotify.com/v1/me/player/queue', headers=headers).json()['queue']
    for x in range(len(response)):
        if response[x]['uri'] != original_song_uri:
            queue.append(response[x]['uri'])

    return queue

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

# doesnt handle if host isnt playing a song...
def join(host_token, joiner_token):
    host_track = get_current_track_info(host_token)
    headers = {
        'Authorization': f'Bearer {joiner_token}',
        'Content-Type': 'application/json'
    }
    json_data = {
        'uris': [host_track['uri']],
        'position_ms': host_track['progress']
    }
    requests.put(url='https://api.spotify.com/v1/me/player/play', headers=headers, json=json_data)

# if both users add songs at the same time, thats probably bad. maybe fixed by calling more frequent?
def update(user1_token, user2_token):
    user1_initial_track = get_current_track_info(user1_token)
    update_unwrapped(user1_token, user2_token, False, user1_initial_track['uri'], user1_initial_track['progress'], user1_initial_track['uri'])

# how do you make wrapper functions lol
def update_unwrapped(user1_token, user2_token, is_playing, prev_song_uri, prev_progress, initial_track_uri):
    print('loop')
    user1_track = get_current_track_info(user1_token)
    user2_track = get_current_track_info(user2_token)
    user1_queue = get_queue(user1_token, initial_track_uri)
    user2_queue = get_queue(user2_token, initial_track_uri)

    #update the queue
    #limited to adding one song per cycle, so cant add songs too fast
    if user1_track['uri'] == user2_track['uri']:
        for song in user1_queue:
            if song not in user2_queue:
                add_to_queue(user2_token, song)

        for song in user2_queue:
            if song not in user1_queue:
                add_to_queue(user1_token, song)

    #allows for changing songs by checking if the tracks arent the same
    buffer_ms = 2500
    if user1_track['uri'] != user2_track['uri']:
        if not user1_track['duration'] - user1_track['progress'] < buffer_ms or user2_track['duration'] - user2_track['progress'] < buffer_ms:
            if user1_track['uri'] != prev_song_uri:
                skip_to_next(user2_token)
            elif user2_track['uri'] != prev_song_uri:
                skip_to_next(user1_token)
                
    # align the progress for both players, incase they are too far away from each other
    # also allows for users to change the progress of the song
    max_progress_diff = 2500
    if user1_track['uri'] == user2_track['uri']:
        if abs(user1_track['progress'] - prev_progress) > max_progress_diff:
            join(user1_token, user2_token)
            prev_progress = user1_track['progress']
        elif abs(user2_track['progress'] - prev_progress) > max_progress_diff:
            join(user2_token, user1_token)
            prev_progress = user2_track['progress']
        else:
            prev_progress = (user1_track['progress'] + user2_track['progress'])/2

    #set prev_song_uri to new song, if there is one
    if user1_track['uri'] != prev_song_uri:
        prev_song_uri = user1_track['uri']
    elif user2_track['uri'] != prev_song_uri:
        prev_song_uri = user2_track['uri']

    #allows for pausing/resuming
    #also the recursive step
    sleep_time = .7
    if is_playing:
        if not user1_track['is_playing']:
            pause(user2_token)
            sleep(.7)
            update_unwrapped(user1_token, user2_token, False, prev_song_uri, prev_progress, initial_track_uri)
        elif not user2_track['is_playing']:
            pause(user1_token)
            sleep(.7)
            update_unwrapped(user1_token, user2_token, False, prev_song_uri, prev_progress, initial_track_uri)
        else:
            sleep(.7)
            update_unwrapped(user1_token, user2_token, is_playing, prev_song_uri, prev_progress, initial_track_uri)
    else:
        if user1_track['is_playing']:
            resume(user2_token)
            sleep(.7)
            update_unwrapped(user1_token, user2_token, True, prev_song_uri, prev_progress, initial_track_uri)
        elif user2_track['is_playing']:
            resume(user1_token)
            sleep(.7)
            update_unwrapped(user1_token, user2_token, True, prev_song_uri, prev_progress, initial_track_uri)
        else:
            sleep(.7)
            update_unwrapped(user1_token, user2_token, is_playing, prev_song_uri, prev_progress, initial_track_uri)
            