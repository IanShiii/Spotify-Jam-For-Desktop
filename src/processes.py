import requests
from time import sleep

import spotifyAPI as spotify

# joins, then starts the sync cycle
# gives priority to user 1 (if both are playing a track, they join user 1)
def join(user1_token, user2_token):
    user1_is_active, user1_track = spotify.get_current_track_info(user1_token)
    user2_is_active, user2_track = spotify.get_current_track_info(user2_token)

    if not (user1_is_active and user2_is_active):
        print('waiting for both users to have active devices')
        sleep(2)
        join(user1_token, user2_token)
        return
    
    if user1_track['is_playing']:
        headers = {
            'Authorization': f'Bearer {user2_token}',
            'Content-Type': 'application/json'
        }
        json_data = {
            'uris': [user1_track['uri']],
            'position_ms': user1_track['progress']
        }
        requests.put(url='https://api.spotify.com/v1/me/player/play', headers=headers, json=json_data)
        sync(user1_token, user2_token, 1)
    elif user2_track['is_playing']:
        headers = {
            'Authorization': f'Bearer {user1_token}',
            'Content-Type': 'application/json'
        }
        json_data = {
            'uris': [user2_track['uri']],
            'position_ms': user2_track['progress']
        }
        requests.put(url='https://api.spotify.com/v1/me/player/play', headers=headers, json=json_data)
        sync(user1_token, user2_token, 2)
    else:
        print('waiting for someone to start a track')
        sleep(2)
        join(user1_token, user2_token)

def join_to_specific_user(host_token, joiner_token):
    host_is_active, host_track = spotify.get_current_track_info(host_token)
    joiner_is_active, joiner_track = spotify.get_current_track_info(joiner_token)

    if not (host_is_active and joiner_is_active):
        print('waiting for both users to have active devices')
        sleep(2)
        join_to_specific_user(host_token, joiner_token)
        return
    
    if host_track['is_playing']:
        headers = {
            'Authorization': f'Bearer {joiner_token}',
            'Content-Type': 'application/json'
        }
        json_data = {
            'uris': [host_track['uri']],
            'position_ms': host_track['progress']
        }
        requests.put(url='https://api.spotify.com/v1/me/player/play', headers=headers, json=json_data)
    else:
        print('waiting for host to start a track')
        sleep(2)
        join_to_specific_user(host_token, joiner_token)

def sync(user1_token, user2_token, host_user):
    user1_initial_track = spotify.get_current_track_info(user1_token)[1]
    user2_initial_track = spotify.get_current_track_info(user2_token)[1]
    if host_user == 1:
        is_playing = False
        prev_song_uri = user1_initial_track['uri']
        prev_progress = user1_initial_track['progress']
        while True:
            new_values = update(user1_token, user2_token, is_playing, prev_song_uri, prev_progress)
            is_playing = new_values[0]
            prev_song_uri = new_values[1]
            prev_progress = new_values[2]
            sleep(.55)
    elif host_user == 2:
        is_playing = False
        prev_song_uri = user2_initial_track['uri']
        prev_progress = user2_initial_track['progress']
        while True:
            new_values = update(user1_token, user2_token, is_playing, prev_song_uri, prev_progress)
            is_playing = new_values[0]
            prev_song_uri = new_values[1]
            prev_progress = new_values[2]
            sleep(.55)
    else:
        print('invalid host_user')

# return tuple (is_playing, prev_song_uri, prev_progress)
def update(user1_token, user2_token, is_playing, prev_song_uri, prev_progress):
    print('update')
    user1_track = spotify.get_current_track_info(user1_token)[1]
    user2_track = spotify.get_current_track_info(user2_token)[1]
    user1_queue = spotify.get_queue(user1_token)
    user2_queue = spotify.get_queue(user2_token)

    #allows for changing/skipping songs by checking if the tracks arent the same
    buffer_ms = 3000
    if user1_track['uri'] != user2_track['uri']: 
        #check if someone is near the end of their song
        if not (user1_track['duration'] - user1_track['progress'] < buffer_ms or user2_track['duration'] - user2_track['progress'] < buffer_ms):
            if user1_track['uri'] != prev_song_uri:
                if user1_track['uri'] != user2_queue[0]:
                    join_to_specific_user(user1_token, user2_token)
                    # give time for spotify to update queue
                    sleep(1)
                    user2_queue = spotify.get_queue(user2_token)
                else:
                    spotify.skip_to_next(user2_token)
                    # give time for spotify to update queue
                    sleep(2)
                    user2_queue = spotify.get_queue(user2_token)
            elif user2_track['uri'] != prev_song_uri:
                if user2_track['uri'] != user1_queue[0]:
                    join_to_specific_user(user2_token, user1_token)
                    # give time for spotify to update queue
                    sleep(1)
                    user1_queue = spotify.get_queue(user1_token)
                else:
                    spotify.skip_to_next(user1_token)
                    # give time for spotify to update queue
                    sleep(2)
                    user1_queue = spotify.get_queue(user1_token)
        else: # reupdate the queues once both are at the same song
            while user1_track['uri'] != user2_track['uri']: 
                user1_track = spotify.get_current_track_info(user1_token)[1]
                user2_track = spotify.get_current_track_info(user2_token)[1]
                sleep(1)
            sleep(1)
            user1_queue = spotify.get_queue(user1_token)
            user2_queue = spotify.get_queue(user2_token)

    #update the queue
    #only one person can add to queue per cycle, in order to keep both in sync
    # if user1_track['uri'] == user2_track['uri']:
    for song in user1_queue:
        if song not in user2_queue:
            spotify.add_to_queue(user2_token, song)
            sleep(.15)

    for song in user2_queue:
        if song not in user1_queue:
            spotify.add_to_queue(user1_token, song)
            sleep(.15)
                
    # align the progress for both players, incase they are too far away from each other
    # also allows for users to change the progress of the song
    max_progress_diff = 2500
    if user1_track['uri'] == user2_track['uri']:
        if abs(user1_track['progress'] - prev_progress) > max_progress_diff:
            spotify.jump_to_progress(user2_token, user1_track['progress'])
            prev_progress = user1_track['progress']
        elif abs(user2_track['progress'] - prev_progress) > max_progress_diff:
            spotify.jump_to_progress(user1_token, user2_track['progress'])
            prev_progress = user2_track['progress']
        else:
            prev_progress = (user1_track['progress'] + user2_track['progress'])/2

    #set prev_song_uri to new song, if there is one
    if user1_track['uri'] != prev_song_uri:
        prev_song_uri = user1_track['uri']
    elif user2_track['uri'] != prev_song_uri:
        prev_song_uri = user2_track['uri']

    #allows for pausing/resuming
    is_playing = update_pause_resume(user1_token, user2_token, is_playing, user1_track['is_playing'], user2_track['is_playing'])
    
    return is_playing, prev_song_uri, prev_progress

# pauses/resumes both users if someone decides to do that
# returns the state that both players should be in (True for playing, False for not playing)
def update_pause_resume(user1_token, user2_token, prev_is_playing, user1_is_playing, user2_is_playing):
    if prev_is_playing:
        if not user1_is_playing:
            spotify.pause(user2_token)
            return False
        elif not user2_is_playing:
            spotify.pause(user1_token)
            return False
    else:
        if user1_is_playing:
            spotify.resume(user2_token)
            return True
        elif user2_is_playing:
            spotify.resume(user1_token)
            return True
        
    return prev_is_playing
            