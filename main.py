import streamlit as st
import openai
import os
import re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

openai.api_key = os.getenv("CHATGPT_API_KEY")

sKillReg = re.compile("^\d+\. |\"", re.MULTILINE)

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
ccm = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
spotify = spotipy.Spotify(client_credentials_manager=ccm)

DAMMY_RESULT = [
    "Lemon",
    "Paprika",
    "Uma to Shika",
    "Flamingo",
    "Peace Sign",
    "Diorama",
    "Orion",
    "LOSER",
    "SPiCa",
    "Loser Pop"
]

def getSearchWords(theme):
    res = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"10 words to search for on Spotify when you want to create a '{theme}' themed songs playlist:\n1. ",
        suffix="",
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return sKillReg.sub("", res["choices"][0]["text"]).split("\n")


def searchMusic(words):
    id_list = []
    meta_list = []
    for word in words:
        res = spotify.search(word, limit=10, offset=0, type='track', market="jp")
        for track in res['tracks']['items']:
            id_list.append(track['id'])
            meta_list.append({
                "artist":",".join([x["name"] for x in track["artists"]]),
                "release_date": track["release_date"]
            })
    features = spotify.audio_features(id_list)
    c = 0
    for f in features:
        for k in ["tempo", "energy", "instrumentalness", "duration_ms"]:
            meta_list[c][k] = f[k]
        c += 1
    return meta_list

st.title("Test")
for i in searchMusic(DAMMY_RESULT):
    st.text(i["title"]+" - "+i["artist"])