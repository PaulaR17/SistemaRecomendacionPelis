import streamlit as st
import pandas as pd

def show_movie_details():
    # Verificar si hay una película seleccionada
    movie_id = st.session_state.get("current_movie_id")
    if movie_id is None:
        st.error("No se seleccionó ninguna película.")
        st.stop()

    # Cargar dataset
    df = pd.read_csv("./CSV/peliculas_with_posters.csv")

    # Renombrar si es necesario
    if "Unnamed: 0" in df.columns:
        df.rename(columns={"Unnamed: 0": "movie_id"}, inplace=True)
    if "average_score" not in df.columns:
        df["average_score"] = (df["critic_score"] + df["people_score"]) / 2

    # Filtrar la película
    # Ojo: si movie_id es int, asegúrate de no tenerlo en str en df, o viceversa.
    # Aquí asumo que movie_id es int.
    movie_id = int(movie_id)

    movie = df[df["movie_id"] == movie_id]
    if movie.empty:
        st.error("No se encontró la película con ese ID.")
        st.stop()

    movie = movie.iloc[0]  # Tomar la fila

    # ... (tu estilo CSS, layout, etc.)

    st.markdown(f"<h1 class='movie-title'>{movie['title']}</h1>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(movie["poster_url"], width=200)
    with col2:
        st.markdown(f"<p class='movie-details'><strong>Género:</strong> {movie['genre']}</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='movie-details'><strong>Puntuación promedio:</strong> {movie['average_score']:.1f}/10</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='movie-synopsis'><strong>Sinopsis:</strong> {movie['synopsis']}</p>", unsafe_allow_html=True)

    # Sistema de rating
    rating = st.radio(
        "Califica esta película:",
        options=[1, 2, 3, 4, 5],
        index=2,
        format_func=lambda x: "★" * x + "☆" * (5 - x),
        horizontal=True
    )

    if st.button("Enviar calificación", key="submit_rating"):
        update_user_rating(movie_id, rating)
        st.success(f"¡Gracias por tu calificación de {rating} estrellas!")
        st.experimental_rerun()


def update_user_rating(movie_id, rating):
    # Cargar archivo de usuarios
    users = pd.read_csv("./CSV/users.csv")
    current_user = st.session_state.user_data["username"]

    # Obtener índice
    user_index = users[users["username"] == current_user].index[0]

    # Manejo del diccionario 'rated_movies'
    try:
        rated_movies = eval(users.at[user_index, "rated_movies"]) \
            if pd.notna(users.at[user_index, "rated_movies"]) else {}
    except (SyntaxError, ValueError):
        rated_movies = {}

    # Actualizar y guardar
    rated_movies[movie_id] = rating
    users.at[user_index, "rated_movies"] = str(rated_movies)
    users.to_csv("./CSV/users.csv", index=False)
