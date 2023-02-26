import requests
import json
import websocket
import os

# Spotify credentials
SPOTIFY_ACCESS_TOKEN = 'Get from Spotify - Make sure to have user-modify-playback-state scope'

# Twitch PubSub credentials
TWITCH_CHANNEL_ID = 'twitchUserID'
TWITCH_OAUTH_TOKEN = 'twitchOAuthToken'

# PubSub endpoints
TWITCH_PUBSUB_URL = 'wss://pubsub-edge.twitch.tv'
TWITCH_PUBSUB_TOPIC = 'channel-points-channel-v1.' + TWITCH_CHANNEL_ID

# Spotify endpoints
SPOTIFY_SEARCH_ENDPOINT = 'https://api.spotify.com/v1/search'
SPOTIFY_PLAY_ENDPOINT = 'https://api.spotify.com/v1/me/player/queue?uri='

# Set up the websocket connection
ws = websocket.WebSocket()
ws.connect(TWITCH_PUBSUB_URL)

# Subscribe to the Twitch PubSub topic
data = {
    "type": "LISTEN",
    "data": {
        "topics": [TWITCH_PUBSUB_TOPIC],
        "auth_token": TWITCH_OAUTH_TOKEN
    }
}
ws.send(json.dumps(data))

# Debugging function
def debug(message):
    print("[DEBUG] " + message)

# Spotify search function
def search_spotify(query):
    headers = {
        'Authorization': 'Bearer ' + SPOTIFY_ACCESS_TOKEN
    }
    params = {
        'q': query,
        'type': 'track',
        'limit': 1
    }
    response = requests.get(SPOTIFY_SEARCH_ENDPOINT, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if 'tracks' in data and 'items' in data['tracks'] and len(data['tracks']['items']) > 0:
            track = data['tracks']['items'][0]
            uri = track['uri']
            debug(f"Found track '{track['name']}' by '{track['artists'][0]['name']}' with URI '{uri}'")
            return uri
        else:
            debug(f"No track found for query '{query}'")
            return None
    else:
        debug(f"Spotify search failed with status code {response.status_code}")
        return None

# Spotify play function
def play_spotify(uri):
    print(uri)
    headers = {
        'Authorization': 'Bearer ' + SPOTIFY_ACCESS_TOKEN,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    response = requests.post(f'{SPOTIFY_PLAY_ENDPOINT}{uri}', headers=headers)
    if response.status_code == 204:
        debug(f"Added track with URI '{uri}' to Spotify queue")
    else:
        debug(f"Spotify play failed with status code {response.status_code}")

# Main loop
try:

    while True:
        message = ws.recv()
        debug(f"Received message: {message}")
        message = json.loads(message)

        # Parse the message
        if message['type'] == 'MESSAGE':
            data = json.loads(message['data']['message'])
            if message['type'] == 'MESSAGE':
                redemption_data = message['data']['message']
                redemption = json.loads(redemption_data)
                user_input = redemption['data']['redemption']['user_input']
                debug(user_input)
                track_uri = search_spotify(user_input)
                if track_uri:
                    play_spotify(track_uri)
except KeyboardInterrupt:
    print("ended.")
