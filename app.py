import os
import gdown
import pickle
import streamlit as st
import requests
import pandas as pd
from dotenv import load_dotenv

# Load API key
load_dotenv()
hidden_API_KEY = os.getenv("tmdb_API_KEY") or st.secrets.get("tmdb_API_KEY")

# Google Drive direct download links
movies_dict_url = "https://drive.google.com/uc?id=1qggRTsf6x-VdRCDPoMyotn77_prJmquW"
similarity_url = "https://drive.google.com/uc?id=1Dr1jcntGoO9IlmhpU3JsNV5Z-x3XAxKg"

# Download .pkl files if missing
if not os.path.exists("movies_dict.pkl"):
    gdown.download(movies_dict_url, "movies_dict.pkl", quiet=False)

if not os.path.exists("similarity.pkl"):
    gdown.download(similarity_url, "similarity.pkl", quiet=False)

# Load pickles
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl', 'rb'))

# Centered title
st.markdown("<h1 style='text-align: center;'>Movie Recommender</h1>", unsafe_allow_html=True)

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key={}&language=en-US".format(movie_id, hidden_API_KEY)
    data = requests.get(url).json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)
    return recommended_movie_names, recommended_movie_posters

selected_movie_name = st.selectbox(
    "Select a movie for Similar Recommendation",
    movies['title'].values
)

# CSS to center all Streamlit buttons
st.markdown("""
    <style>
    div.stButton > button:first-child {
        display: block;
        margin: 0 auto;
    }
    </style>
""", unsafe_allow_html=True)

if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie_name)
    cols = st.columns(5)
    for col, name, poster in zip(cols, recommended_movie_names, recommended_movie_posters):
        with col:
            st.markdown(
                f"<div style='text-align: center; height: 3em; overflow-wrap: break-word;'>{name}</div>",
                unsafe_allow_html=True
            )
            st.image(poster, use_container_width=True)

# Credits
st.markdown("""
---
<p style='text-align: center; font-size: 14px;'>
This project uses the <a href="https://www.themoviedb.org/" target="_blank">TMDb API</a> but is not endorsed or certified by TMDb.
</p>
""", unsafe_allow_html=True)
