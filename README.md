# Spotify-Jam-For-Desktop

## Work in progress

Spotify Jam is currently only for mobile users, so this is a way for laptop users to join in :D<br>
This only supports 2 Listeners for now<br>
Spotify API does not allow to remove or clear queue. Please clear your queues before joining a Jam session so that both user's queues can match. This also means that you cant remove a song from queue, since I cant remove it from the other person's queue. You can just skip once you get to that song<br>
Spotify API also does not differentiate between "next up" and "queue". Turn off autoplay similar content before joining to deal with this issue.<br>

## Limitations (trying to improve these)

- Dont skip songs too fast
- Try to only have one person add songs to queue at a time
- If you want to go forward songs, go one at a time, dont skip 2 songs at a time (queue issues D:)
- If you run out of songs it stops working...
- You cant add the original song you were playing when you start the session. Unfortunately I cant fix that because the way Spotify API works when trying to access queue (related to what was mentioned before)
