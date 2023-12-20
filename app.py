import time
import pickle
import streamlit as st
import itertools
import pandas as pd
import requests

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

def fetch_imdb_id(title):
    url = f"http://www.omdbapi.com/?t={title}&apikey=cf2cfe20"
    data = requests.get(url)
    data = data.json()
    imdb_id = data.get('imdbID')
    return imdb_id

def fetch_imdb_movie_details(imdb_id):
    url = f"http://www.omdbapi.com/?i={imdb_id}&apikey=cf2cfe20"
    data = requests.get(url)
    data = data.json()
    return data

def recommend_n_movies(movie, n=5):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_data = []
    for i in distances[1:n + 1]:
        # fetch the movie poster and IMDb URL
        movie_id = movies.iloc[i[0]].movie_id
        poster_url = fetch_poster(movie_id)
        imdb_id = fetch_imdb_id(movies.iloc[i[0]].title)
        imdb_url = f"https://www.imdb.com/title/{imdb_id}/" if imdb_id else "#"
        recommended_movie_data.append({
            'name': movies.iloc[i[0]].title,
            'poster': poster_url,
            'imdb_url': imdb_url
        })

    return recommended_movie_data

def fetch_top_movies():
    # Convert the 'tags' column to lowercase and fetch today's top movies from your dataset
    # based on tags starting with 's', 'a', or 'y'.
    # For this example, let's consider the top 5 movies based on the number of tags starting with 's', 'a', or 'y'.
    movies['tags'] = movies['tags'].str.lower()
    movies['tag_count'] = movies['tags'].apply(lambda x: sum(tag.startswith(('s', 'a', 'y')) for tag in x.split(',')))
    top_movies = movies.nlargest(5, 'tag_count')
    top_movie_names = top_movies['title'].tolist()
    top_movie_posters = [fetch_poster(movie_id) for movie_id in top_movies['movie_id']]
    return top_movie_names, top_movie_posters

st.header('Movie Recommender System')
movies = pickle.load(open('movie_list.pkl','rb'))
similarity = pickle.load(open('similarity.pkl','rb'))

st.markdown("<br><br>", unsafe_allow_html=True)

# Fetch Today's Top Movies
top_movie_names, top_movie_posters = fetch_top_movies()

# Apply custom CSS for the movie grid layout
st.markdown(
    """
    <style>
    .movie-grid-container {
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        justify-content: center;
    }
    .movie-item {
        display: flex;
        flex-direction: row;
        align-items: center;
        margin-bottom:10px;
        border: 1px solid #ccc;
    }
    .movie-data {
        flex: 1;
        padding: 20px;
    }
    .movie-poster img {
        max-height: 250px;
        object-fit: cover;
        margin-left:75px;
        border-radius: 10px;
        box-shadow: 0px 0px 8px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s;
    }
    .movie-poster img:hover {
        transform: scale(1.05);
    }
    .movie-poster {
        flex: 0 0 calc(40% - 20px);
        margin-left: 20px;
        display: inline-block;
    }
    .movie-item a {
        text-decoration: none;
        color: black;
        font-weight: bold;
    }
    .know-more-button {
        display: inline-block;
        margin-top: 10px;
        padding: 5px 10px;
        background-color: #0074e4;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    .know-more-button:hover {
        background-color: #0053a1;
    }
    
    
     /* Media Query for Tablets (768px - 1023px) */
    @media (max-width: 1023px) {
       .movie-item {
           display:flex;
    flex-direction: column-reverse;
}
        .movie-poster img {
        margin-bottom:15px;
    }
        .movie-poster {
            flex: 0 0 100%;
            margin-left: 0;
        }
        .movie-data {
            padding: 10px;
        }
        .movie-poster img {
            margin-left: 0;
            max-height: 250px;
            margin-top:20px;
        }
    }
    
    
    @media (max-width: 767px) {
        .movie-grid-container {
            justify-content: flex-start;
        }
        .movie-item {
             display:flex;
    flex-direction: column-reverse;
        }
        .movie-data {
            padding: 10px;
        }
        .movie-poster {
            flex: 0 0 100%;
            margin-left: 0;
        }
        .movie-poster img {
            
            max-height: 250px;
        }
    
    
    
    
    
    </style>
    """,
    unsafe_allow_html=True
)

st.subheader("Today's Top Movies")

# Create a container for the top movie grid layout
top_movies_container = st.container()

# Create a grid layout for top movies
with top_movies_container:
    st.markdown('<div class="movie-grid-container">', unsafe_allow_html=True)

    for top_movie_name, top_movie_poster in zip(top_movie_names, top_movie_posters):
        # Fetch IMDb ID for the top movie
        top_imdb_id = fetch_imdb_id(top_movie_name)

        if top_imdb_id:
            # Fetch IMDb movie details
            top_imdb_movie_details = fetch_imdb_movie_details(top_imdb_id)

            # Display IMDb movie details and poster in a separate div for each movie
            st.markdown(
                f"<div class='movie-item'>"
                f"<div class='movie-data'>"
                f"<p><strong>Title:</strong> {top_imdb_movie_details.get('Title')}</p>"
                f"<p><strong>IMDb Rating:</strong> {top_imdb_movie_details.get('imdbRating')}</p>"
                f"<p><strong>Genre:</strong> {top_imdb_movie_details.get('Genre')}</p>"
                f"<p><strong>Plot:</strong> {top_imdb_movie_details.get('Plot')}</p>"
                f"<p><strong>Director:</strong> {top_imdb_movie_details.get('Director')}</p>"
                f"<a href='https://www.imdb.com/title/{top_imdb_id}/' class='know-more-button' target='_blank'>Know More...</a>"

                f"</div>"
                f"<div class='movie-poster'><img src='{top_movie_poster}' alt='{top_imdb_movie_details.get('Title')}'></div>"
                f"</div>",
                unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

if st.button('Show Recommendation'):
    st.markdown("<br><br>", unsafe_allow_html=True)
    recommended_movie_data = recommend_n_movies(selected_movie, n=15)

    # Create a container for the movie grid layout
    container = st.container()

    # Split the recommended movies into batches of 5 movies
    batches_of_movies = [recommended_movie_data[i:i + 5] for i in range(0, len(recommended_movie_data), 5)]

    # Create a grid layout for recommended movies
    with container:
        st.markdown('<div class="movie-grid-container">', unsafe_allow_html=True)

        for movie_batch in batches_of_movies:
            for movie_data in movie_batch:
                # Fetch IMDb movie details
                imdb_movie_details = fetch_imdb_movie_details(fetch_imdb_id(movie_data['name']))

                # Display IMDb movie details and poster in a separate div for each movie
                st.markdown(
                    f"<div class='movie-item'>"
                    f"<div class='movie-data'>"
                    f"<p><strong>Title:</strong> {imdb_movie_details.get('Title')}</p>"
                    f"<p><strong>IMDb Rating:</strong> {imdb_movie_details.get('imdbRating')}</p>"
                    f"<p><strong>Genre:</strong> {imdb_movie_details.get('Genre')}</p>"
                    f"<p><strong>Plot:</strong> {imdb_movie_details.get('Plot')}</p>"
                    f"<p><strong>Director:</strong> {imdb_movie_details.get('Director')}</p>"
                    f"<a href='{movie_data['imdb_url']}' class='know-more-button' target='_blank'>Know More...</a>"
                    f"</div>"
                    f"<div class='movie-poster'><img src='{movie_data['poster']}' alt='{imdb_movie_details.get('Title')}'></div>"
                    f"</div>",
                    unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
