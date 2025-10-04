# movie_dashboard_dark.py
import streamlit as st
import requests
import json
import os
from datetime import datetime

# -----------------------------
# CONFIG
# -----------------------------
API_KEY = "549d23dd092603b06a2388815c4fd544"  # <-- Replace with your TMDB API key
BASE_URL = "https://api.themoviedb.org/3"
FAV_FILE = "favorites.json"

# Streamlit page config
st.set_page_config(page_title="🎬 Movie Explorer (Dark)", layout="wide")

# -----------------------------
# DARK THEME + STYLES
# -----------------------------
st.markdown(
    """
    <style>
    :root {
      --bg: #0f1720;
      --card: #111827;
      --muted: #9ca3af;
      --accent: #ef4444;
      --text: #e6eef6;
    }
    .stApp {
      background-color: var(--bg);
      color: var(--text);
    }
    .card {
      background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
      border: 1px solid rgba(255,255,255,0.04);
      padding: 10px;
      border-radius: 10px;
      box-shadow: 0 6px 18px rgba(2,6,23,0.6);
    }
    .movie-title { font-weight:700; color: var(--text); font-size:16px; }
    .muted { color: var(--muted); font-size:13px; }
    .small { font-size:13px; }
    .fav-btn { background: none; border: 1px solid rgba(255,255,255,0.06); color: var(--text); padding:6px 8px; border-radius:8px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Helper Functions
# -----------------------------
def tmdb_get(path, params=None):
    if params is None:
        params = {}
    params.update({"api_key": API_KEY, "language": "en-US", "page": 1})
    url = f"{BASE_URL}/{path}"
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error("Network/API error. Check API key and connection.")
        return None

def get_movies(endpoint):
    data = tmdb_get(endpoint)
    return data.get("results", []) if data else []

def search_movie(query):
    data = tmdb_get("search/movie", {"query": query})
    return data.get("results", []) if data else []

def get_similar(movie_id):
    data = tmdb_get(f"movie/{movie_id}/similar")
    return data.get("results", []) if data else []

def get_genres():
    data = tmdb_get("genre/movie/list")
    return data.get("genres", []) if data else []

def get_poster(path, w=300):
    if path:
        return f"https://image.tmdb.org/t/p/w{w}{path}"
    return "https://via.placeholder.com/300x450?text=No+Image"

def load_favorites():
    if os.path.exists(FAV_FILE):
        try:
            with open(FAV_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_favorites(favs):
    with open(FAV_FILE, "w", encoding="utf-8") as f:
        json.dump(favs, f, ensure_ascii=False, indent=2)

def add_to_favorites(movie):
    favs = load_favorites()
    if movie["id"] not in [m["id"] for m in favs]:
        # store only necessary fields to keep file small
        item = {
            "id": movie["id"],
            "title": movie.get("title"),
            "poster_path": movie.get("poster_path"),
            "vote_average": movie.get("vote_average"),
            "release_date": movie.get("release_date"),
        }
        favs.append(item)
        save_favorites(favs)
        st.success(f"Added '{movie.get('title')}' to favorites.")

def remove_from_favorites(movie_id):
    favs = load_favorites()
    updated = [m for m in favs if m["id"] != movie_id]
    save_favorites(updated)
    st.info("Removed from favorites.")

# -----------------------------
# Load genre list (for filters)
# -----------------------------
genres_list = get_genres()
genre_map = {g["name"]: g["id"] for g in genres_list}
genre_options = ["Any"] + sorted([g["name"] for g in genres_list])

# -----------------------------
# Session: favorites (load once)
# -----------------------------
if "favorites" not in st.session_state:
    st.session_state["favorites"] = load_favorites()

# -----------------------------
# Layout: header + sidebar
# -----------------------------
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("<h1 style='color: #e6eef6;'>🎬 Movie Explorer — Dark</h1>", unsafe_allow_html=True)
    st.markdown("<div class='muted'>Trending, Now Playing, Search, Filters, Favorites & Recommendations</div>", unsafe_allow_html=True)
with col2:
    st.markdown("<div style='text-align:right;color:var(--muted)'>Updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "</div>", unsafe_allow_html=True)

st.markdown("---")

# -----------------------------
# Sidebar: controls & navigation
# -----------------------------
st.sidebar.title("Controls")
menu = st.sidebar.radio("Navigate", ["Home", "Trending", "Now Playing", "Search", "Favorites"], index=0, key="menu_radio")

# Filters
st.sidebar.markdown("### Filters")
min_rating = st.sidebar.slider("Minimum rating", 0.0, 10.0, 6.0, 0.1, key="min_rating_slider")
genre_choice = st.sidebar.selectbox("Genre", genre_options, index=0, key="genre_select")
year_min, year_max = st.sidebar.slider("Release year range", 1950, datetime.now().year, (2000, datetime.now().year), key="year_slider")
st.sidebar.markdown("---")
st.sidebar.caption("Built with TMDB • Dark theme")

# Helper: apply filters
def apply_filters(movies):
    out = []
    for m in movies:
        rating = m.get("vote_average") or 0
        rd = m.get("release_date") or ""
        try:
            y = int(rd.split("-")[0]) if rd else 0
        except:
            y = 0
        # genre filter
        if genre_choice != "Any":
            wanted_id = genre_map.get(genre_choice)
            if not wanted_id:
                continue
            if wanted_id not in m.get("genre_ids", []):
                continue
        if rating < min_rating:
            continue
        if not (year_min <= y <= year_max):
            continue
        out.append(m)
    return out

# Card renderer
def render_movie_card(movie, show_add_fav=True, btn_key_prefix=""):
    poster = get_poster(movie.get("poster_path"), w=300)
    title = movie.get("title")
    score = movie.get("vote_average", 0)
    release = movie.get("release_date", "")[:4]
    overview = movie.get("overview", "")[:320]
    # card structure with two columns
    c1, c2 = st.columns([1, 2])
    with c1:
        st.image(poster, use_column_width=True)
    with c2:
        st.markdown(f"<div class='movie-title'>{title} <span class='muted'>({release})</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='muted small'>⭐ {score:.1f} / 10</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='small muted'>{overview}</div>", unsafe_allow_html=True)
        # action buttons
        row = st.columns([1,1,1])
        if show_add_fav:
            if row[0].button("❤️ Add to Favorites", key=f"{btn_key_prefix}_add_{movie['id']}"):
                add_to_favorites(movie)
        if row[1].button("🔁 Similar", key=f"{btn_key_prefix}_sim_{movie['id']}"):
            sims = get_similar(movie["id"])
            if sims:
                sims = apply_filters(sims)
                st.markdown("### Similar movies", unsafe_allow_html=True)
                cols = st.columns(4)
                for i, s in enumerate(sims[:8]):
                    with cols[i % 4]:
                        st.image(get_poster(s.get("poster_path")), width=140)
                        st.caption(f"{s.get('title')} ({s.get('release_date','')[:4]})")
            else:
                st.info("No similar movies found.")
        if row[2].button("🔗 Details (TMDB)", key=f"{btn_key_prefix}_link_{movie['id']}"):
            st.write(f"https://www.themoviedb.org/movie/{movie['id']}")

# -----------------------------
# Page: Home (combo)
# -----------------------------
if menu == "Home":
    st.subheader("Trending & Now Playing — quick view")
    trending = get_movies("trending/movie/day") or []
    now_playing = get_movies("movie/now_playing") or []

    trending = apply_filters(trending)
    now_playing = apply_filters(now_playing)

    st.markdown("#### 🔥 Trending")
    if trending:
        cols = st.columns(3)
        for i, m in enumerate(trending[:9]):
            with cols[i % 3]:
                st.image(get_poster(m.get("poster_path")), width=200)
                st.markdown(f"**{m.get('title')}**")
                st.markdown(f"⭐ {m.get('vote_average', 0):.1f} | {m.get('release_date','')[:4]}")
                if st.button("Add", key=f"home_trend_{m['id']}"):
                    add_to_favorites(m)
    else:
        st.info("No trending movies available.")

    st.markdown("---")
    st.markdown("#### 🎬 Now Playing")
    if now_playing:
        cols = st.columns(3)
        for i, m in enumerate(now_playing[:9]):
            with cols[i % 3]:
                st.image(get_poster(m.get("poster_path")), width=200)
                st.markdown(f"**{m.get('title')}**")
                st.markdown(f"⭐ {m.get('vote_average', 0):.1f} | {m.get('release_date','')[:4]}")
                if st.button("Add", key=f"home_now_{m['id']}"):
                    add_to_favorites(m)
    else:
        st.info("No now-playing movies available.")

# -----------------------------
# Page: Trending
# -----------------------------
elif menu == "Trending":
    st.subheader("🔥 Trending Movies (Today)")
    trending = get_movies("trending/movie/day") or []
    trending = apply_filters(trending)
    if trending:
        for m in trending[:30]:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            render_movie_card(m, show_add_fav=True, btn_key_prefix="trend")
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No trending data. Check API key or internet connection.")

# -----------------------------
# Page: Now Playing
# -----------------------------
elif menu == "Now Playing":
    st.subheader("🎟️ Now Playing in Theaters")
    playing = get_movies("movie/now_playing") or []
    playing = apply_filters(playing)
    if playing:
        for m in playing[:30]:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            render_movie_card(m, show_add_fav=True, btn_key_prefix="now")
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No now-playing data.")

# -----------------------------
# Page: Search
# -----------------------------
elif menu == "Search":
    st.subheader("🔎 Search Movies")
    query = st.text_input("Type movie name and press Enter", key="search_input")
    if query:
        results = search_movie(query) or []
        results = apply_filters(results)
        if not results:
            st.warning("No results found. Try another query or relax filters.")
        else:
            st.markdown(f"Found {len(results)} results — showing top {min(12, len(results))}")
            for r in results[:12]:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                render_movie_card(r, show_add_fav=True, btn_key_prefix="search")
                st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Page: Favorites
# -----------------------------
elif menu == "Favorites":
    st.subheader("❤️ Your Favorites")
    favs = load_favorites()
    if not favs:
        st.info("No favorites yet — add movies from Trending, Now Playing or Search.")
    else:
        for f in favs:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            # show saved info
            cols = st.columns([1, 2])
            with cols[0]:
                st.image(get_poster(f.get("poster_path")), width=160)
            with cols[1]:
                st.markdown(f"### {f.get('title')} ({f.get('release_date','')[:4]})", unsafe_allow_html=True)
                st.markdown(f"⭐ {f.get('vote_average',0):.1f}", unsafe_allow_html=True)
                if st.button("Remove from Favorites", key=f"remove_{f['id']}"):
                    remove_from_favorites(f["id"])
                    st.experimental_rerun()
            st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Footer / credits
# -----------------------------
st.markdown("---")
st.markdown("<div class='muted small'>Data provided by The Movie Database (TMDB). Built with Streamlit.</div>", unsafe_allow_html=True)
