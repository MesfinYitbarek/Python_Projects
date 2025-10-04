import streamlit as st
import requests
import json
import os

# -----------------------------
# CONFIGURATION
# -----------------------------
API_KEY = "549d23dd092603b06a2388815c4fd544"  # 🔑 Replace with your TMDB key
BASE_URL = "https://api.themoviedb.org/3"
FAV_FILE = "favorites.json"  # Local file for saving favorites

st.set_page_config(page_title="🎬 Movie Explorer Dashboard", layout="wide")

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def get_movies(endpoint):
    """Fetch movies from TMDB API endpoint."""
    url = f"{BASE_URL}/{endpoint}?api_key={API_KEY}&language=en-US&page=1"
    response = requests.get(url).json()
    return response.get("results", [])


def search_movie(query):
    """Search for a movie by name."""
    url = f"{BASE_URL}/search/movie?api_key={API_KEY}&query={query}"
    response = requests.get(url).json()
    return response.get("results", [])


def get_similar_movies(movie_id):
    """Fetch similar/recommended movies."""
    url = f"{BASE_URL}/movie/{movie_id}/similar?api_key={API_KEY}&language=en-US&page=1"
    response = requests.get(url).json()
    return response.get("results", [])


def get_poster(path):
    """Return movie poster URL or a placeholder if none."""
    if path:
        return f"https://image.tmdb.org/t/p/w500{path}"
    return "https://via.placeholder.com/300x450?text=No+Image"


def load_favorites():
    """Load favorites from JSON file."""
    if os.path.exists(FAV_FILE):
        with open(FAV_FILE, "r") as f:
            return json.load(f)
    return []


def save_favorites(favorites):
    """Save favorites to JSON file."""
    with open(FAV_FILE, "w") as f:
        json.dump(favorites, f)


def add_to_favorites(movie):
    """Add a movie to favorites."""
    favorites = load_favorites()
    if movie not in favorites:
        favorites.append(movie)
        save_favorites(favorites)
        st.success(f"✅ Added '{movie['title']}' to favorites!")


def remove_from_favorites(title):
    """Remove a movie from favorites."""
    favorites = load_favorites()
    updated = [m for m in favorites if m["title"] != title]
    save_favorites(updated)
    st.info(f"🗑️ Removed '{title}' from favorites.")


# -----------------------------
# HEADER
# -----------------------------
st.markdown("<h1 style='text-align:center;'>🎬 Movie Explorer Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Discover trending movies, find your favorites, and get smart recommendations! 🍿</p>", unsafe_allow_html=True)
st.markdown("---")

# -----------------------------
# RATING FILTER
# -----------------------------
rating_filter = st.slider("⭐ Minimum Rating", 0.0, 10.0, 6.0, 0.5, key="rating_slider_main")

# -----------------------------
# SECTION 1: TRENDING MOVIES
# -----------------------------
st.subheader("🔥 Trending Today")

trending = get_movies("trending/movie/day")
filtered_trending = [m for m in trending if m.get("vote_average", 0) >= rating_filter]

cols = st.columns(5)
for i, movie in enumerate(filtered_trending[:10]):
    with cols[i % 5]:
        st.image(get_poster(movie.get("poster_path")), width=160)
        st.caption(f"🎞️ {movie['title']} ({movie.get('release_date', '')[:4]})")
        st.caption(f"⭐ {movie.get('vote_average', 0):.1f}/10")
        if st.button("❤️ Add to Favorites", key=f"fav_trend_{i}"):
            add_to_favorites(movie)

# -----------------------------
# SECTION 2: NOW PLAYING
# -----------------------------
st.subheader("🎟️ Now Playing in Theaters")

now_playing = get_movies("movie/now_playing")
filtered_playing = [m for m in now_playing if m.get("vote_average", 0) >= rating_filter]

cols = st.columns(5)
for i, movie in enumerate(filtered_playing[:10]):
    with cols[i % 5]:
        st.image(get_poster(movie.get("poster_path")), width=160)
        st.caption(f"{movie['title']} ({movie.get('release_date', '')[:4]})")
        st.caption(f"⭐ {movie.get('vote_average', 0):.1f}/10")
        if st.button("❤️ Add", key=f"fav_now_{i}"):
            add_to_favorites(movie)

# -----------------------------
# SECTION 3: SEARCH
# -----------------------------
st.subheader("🔎 Search Any Movie")

query = st.text_input("Enter movie name:", placeholder="e.g. Inception, Titanic, Avatar", key="search_box")

if query:
    results = search_movie(query)
    if not results:
        st.warning("No results found.")
    else:
        movie = results[0]
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(get_poster(movie.get("poster_path")), width=200)
        with col2:
            st.write(f"### {movie['title']} ({movie.get('release_date', '')[:4]})")
            st.write(f"⭐ Rating: {movie.get('vote_average', 0):.1f}/10")
            st.write(f"📝 {movie.get('overview', 'No description available.')}")
            if st.button("❤️ Add to Favorites", key=f"fav_search_{movie['id']}"):
                add_to_favorites(movie)

        # Recommendations
        similar = get_similar_movies(movie["id"])
        if similar:
            st.subheader("🍿 You might also like:")
            cols = st.columns(5)
            for i, sim in enumerate(similar[:5]):
                with cols[i % 5]:
                    st.image(get_poster(sim.get("poster_path")), width=160)
                    st.caption(f"{sim['title']} ({sim.get('release_date', '')[:4]})")
                    st.caption(f"⭐ {sim.get('vote_average', 0):.1f}/10")
                    if st.button(f"❤️ Add {i}", key=f"fav_sim_{i}"):
                        add_to_favorites(sim)

# -----------------------------
# SECTION 4: FAVORITES
# -----------------------------
st.subheader("❤️ Your Favorites")

favorites = load_favorites()
if not favorites:
    st.info("You have no favorite movies yet. Add some above!")
else:
    cols = st.columns(5)
    for i, fav in enumerate(favorites):
        with cols[i % 5]:
            st.image(get_poster(fav.get("poster_path")), width=160)
            st.caption(f"{fav['title']} ({fav.get('release_date', '')[:4]})")
            st.caption(f"⭐ {fav.get('vote_average', 0):.1f}/10")
            if st.button(f"🗑️ Remove {i}", key=f"rem_{i}"):
                remove_from_favorites(fav["title"])
                st.experimental_rerun()
