import streamlit as st
import streamlit.components.v1 as stc
import openai
import os
import re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from streamlit_javascript import st_javascript
from twitter_text import parse_tweet
import urllib.parse

url = st_javascript("await fetch('').then(r => window.parent.location.href)")


openai.api_key = os.getenv("CHATGPT_API_KEY")

sKillReg = re.compile(r"^\d+\. ", re.MULTILINE)

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


def searchMusic(words, additional_word, market):
    id_list = []
    meta_list = []
    while len(words) == 1:
        words = words[0]
    for word in words:
        sq = word
        if len(additional_word):
            sq += " " + additional_word
        res = spotify.search(sq, limit=10, offset=0, type='track', market=market)
        for track in res['tracks']['items']:
            id_list.append(track['id'])
            meta_list.append({
                "id": track["id"],
                "title": track["name"],
                "artist":",".join([x["name"] for x in track["artists"]]),
                "uri": track["uri"],
            })
    features = spotify.audio_features(id_list)
    c = 0
    for f in features:
        for k in ["tempo", "energy", "instrumentalness", "duration_ms"]:
            meta_list[c][k] = f[k]
        c += 1
    return meta_list

def createPlayList(theme,meta_list,tracks_length):
    prompt = f"I am thinking of making a playlist about '{theme}'. I just searched Spotify for songs to put in the playlist and found the following {len(meta_list)} songs. Please choose {tracks_length} songs from these {len(meta_list)} songs to make a playlist. The playlist should be in the form of a Markdown numbered list,  Don't just arrange the songs, rearrange them with the order in mind. Do not include BPM in the result.\n\n"
    c = 1
    for i in meta_list:
        prompt += f"No{c}: {i['title']} - {i['artist']} BPM:{i['tempo']}\n"
        c += 1
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": prompt
            }
        ]
    )
    ressp = sKillReg.sub("", res["choices"][0]["message"]["content"]).split("\n")
    result_ids = []
    for m in ressp:
        sp = m.split(" - ")
        title_match = list(filter(lambda x:x["title"] == sp[0],meta_list))
        if len(title_match):
            title_artist_match =  list(filter(lambda x:x["artist"] == sp[1],title_match))
            if len(title_artist_match):
                result_ids.append(title_artist_match[0])
            else:
                result_ids.append(title_match[0])

    return result_ids


def generate(theme,tracks_length,market,additional_word):
    words = getSearchWords(theme),
    searchResult = searchMusic(words,additional_word,market)
    playlist = createPlayList(theme,searchResult,tracks_length)
    return playlist



st.title("PlaylistGPT")
st.header('ChatGPTにSpotifyのプレイリストを作らせてみる')
st.caption(
    "ChatGPT APIで作りました。プレイリストと言ってもSpotify APIと連携するのが面倒だったので曲を羅列しているだけです。作者のOpenAI APIが無料枠上限に達するまでは動きますが、それ以降は残骸です。残骸が嫌なら[お金をください](https://www.buymeacoffee.com/qwegat)。")
inputed_theme = st.text_input("テーマ", value="工事現場", max_chars=20, placeholder="工事現場")
inputed_tracks_length = st.number_input("曲数", min_value=1, max_value=50, value=10)
selected_market = st.selectbox("マーケット", ["jp", "us"])
with st.expander("高度な設定"):
    inputed_additional_word = st.text_input("追加の検索ワード", value="",placeholder="year:2020")
if st.button("生成"):
    if len(inputed_theme):
        playlist = None
        with st.spinner("プレイリストを作成中…"):
            playlist = generate(inputed_theme,inputed_tracks_length,selected_market,inputed_additional_word)
        st.markdown(f"## 「{inputed_theme}」のプレイリスト")
        outText = f"{url}\n「{inputed_theme}」をテーマに#PlaylistGPT でプレイリストを作成しました\n"
        c = 0
        d = str(c+1)+". "+playlist[c]["title"]+" - "+playlist[c]["artist"]+"\n"
        while parse_tweet(outText+d).asdict()["weightedLength"] <= 277:
            outText += d
            c += 1
            d = str(c+1)+". "+playlist[c]["title"]+" - "+playlist[c]["artist"]+"\n"
            if len(playlist) <= c:
                break
        outText += "\n…"
        stc.html(
    f"""
        <a href="https://twitter.com/share?text={urllib.parse.quote(outText)}">
        Tweet
        </a>
    """
)
        for t in playlist:
            stc.html(
                f'<iframe style="border-radius:12px" src="https://open.spotify.com/embed/track/{t["id"]}" width="100%" height="80" frameBorder="0" allowtransparency="true" allow="encrypted-media"></iframe>',height=90)
