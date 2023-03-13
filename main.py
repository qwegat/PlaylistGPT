import streamlit as st
import openai
import os
import re

openai.api_key = os.getenv("CHATGPT_API_KEY")

sKillReg = re.compile("^\d+\. ")

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
    print(sKillReg.sub("",res["choices"][0]["text"]))


getSearchWords("Kenshi Yonezu")