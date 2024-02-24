# Spotify-Jam-For-Desktop

## Work in progress

Spotify Jam is currently only for mobile users, so this is a way for laptop users to join in :D<br>
This only supports 2 Listeners for now<br>
Spotify API does not allow to remove or clear queue. Please clear your queues before joining a Jam session so that both user's queues can match. This also means that if you want to remove a song from queue, both people have to do it...<br>
Spotify API also does not differentiate between "next up" and "queue". Turn off autoplay similar content before joining to deal with this issue.<br>

Dont skip or add songs too fast. (i'm limited by spotify API rate limit)<br>
Also if you want to go forward songs, go one at a time, dont skip 2 songs at a time (queue issues D:)<br>
If you run out of songs it stops working...<br>
Also you cant add the original song you were playing when you start the session (because of the logic for accessing the queue)<br>
Unfortunately I cant fix that because the way Spotify API works when trying to access queue (related to what was mentioned before)<br>
