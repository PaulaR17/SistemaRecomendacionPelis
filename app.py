import streamlit as st
import pandas as pd

def run_app():
    # Encabezado de la app
    st.markdown("<h1 style='text-align: center;'>Bienvenido a Movie Recommender 🎥</h1>",
                unsafe_allow_html=True)

    # Botón de cerrar sesión
    if st.button("Cerrar sesión", key="logout_button"):
        st.session_state.current_page = "login"
        st.session_state.user_data = None
        st.experimental_rerun()

    # --------------------------------------------------------------------
    # 1) Cargar el dataset de películas con posters
    # --------------------------------------------------------------------
    df = pd.read_csv("./CSV/peliculas_with_posters.csv")

    # Renombrar si fuera necesario
    if "Unnamed: 0" in df.columns:
        df.rename(columns={"Unnamed: 0": "movie_id"}, inplace=True)
    # Asegurarnos de tener la columna de average_score
    if "average_score" not in df.columns:
        df["average_score"] = (df["critic_score"] + df["people_score"]) / 2

    # --------------------------------------------------------------------
    # 2) Cargar la matriz de similitud
    # --------------------------------------------------------------------
    # Suponiendo que la guardaste con "movie_id" como índice:
    similarity_df = pd.read_csv("./CSV/updated_similarity_matrix.csv", index_col=0)
    # A veces es index_col="movie_id", depende de cómo la guardaste. Ajusta según tu caso.
    # Lo importante es que similarity_df.index sean los IDs de la película.

    # --------------------------------------------------------------------
    # 3) Mostrar Películas más populares (por average_score)
    # --------------------------------------------------------------------
    st.subheader("🎥 Películas más populares")
    popular_movies = df.sort_values(by="average_score", ascending=False).head(5)

    # Ajustar columnas dinámicamente
    num_movies = len(popular_movies)
    cols = st.columns(min(num_movies, 5))  # Hasta 5 columnas
    for index, (_, row) in enumerate(popular_movies.iterrows()):
        with cols[index % len(cols)]:
            st.markdown(
                f"""
                <div style="text-align: center;">
                    <img src="{row['poster_url']}" alt="{row['title']}" style="width: 80%; border-radius: 10px;">
                    <h4>{row['title']}</h4>
                    <p><strong>Media de Ratings:</strong> {row['average_score']:.1f}/10</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            # Botón para ir a detalles
            if st.button(f"Ver más sobre {row['title']}", key=f"movie_{row['movie_id']}"):
                st.session_state.current_page = "movie_details"
                st.session_state.current_movie_id = row["movie_id"]
                st.experimental_rerun()

    # --------------------------------------------------------------------
    # 4) Mostrar Películas según los géneros que el usuario eligió
    # --------------------------------------------------------------------
    st.subheader("🎬 Películas que coinciden con tus géneros favoritos")

    user_data = st.session_state.get("user_data", None)

    if user_data is not None:
        # Cargar la info de usuarios
        users = pd.read_csv("./CSV/users.csv")
        # Filtrar el usuario actual
        current_user = user_data["username"]
        user_index = users[users["username"] == current_user].index[0]

        # Las preferencias están en la columna "preferences" -> string "action,drama,comedy..."
        user_prefs_str = users.at[user_index, "preferences"]
        # Convertir a lista
        # Suponiendo que en "preferences" hay algo como "action,drama"
        # o "action,drama,romance"
        user_prefs = user_prefs_str.split(",")

        # Filtramos en df las películas que contengan alguno de esos géneros
        # OJO: Dependiendo de cómo esté guardado 'genre' en df, puede requerir otro approach
        # Ejemplo simple: comprueba que alguno de los prefs aparezca en el 'genre'
        mask = df["genre"].apply(
            lambda g: any(pref.lower() in str(g).lower() for pref in user_prefs)
        )
        df_genre_filtered = df[mask].copy()

        # Ordenar por average_score para mostrar las "mejores"
        df_genre_filtered = df_genre_filtered.sort_values(by="average_score", ascending=False).head(5)

        if df_genre_filtered.empty:
            st.info("No encontramos películas que coincidan con tus géneros favoritos.")
        else:
            cols = st.columns(min(len(df_genre_filtered), 5))
            for index, (_, row) in enumerate(df_genre_filtered.iterrows()):
                with cols[index % len(cols)]:
                    st.markdown(
                        f"""
                        <div style="text-align: center;">
                            <img src="{row['poster_url']}" alt="{row['title']}" style="width: 80%; border-radius: 10px;">
                            <h4>{row['title']}</h4>
                            <p><strong>Media de Ratings:</strong> {row['average_score']:.1f}/10</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    if st.button(f"Ver más sobre {row['title']}", key=f"genre_movie_{row['movie_id']}"):
                        st.session_state.current_page = "movie_details"
                        st.session_state.current_movie_id = row["movie_id"]
                        st.experimental_rerun()

    else:
        st.info("Inicia sesión para ver películas según tus géneros favoritos.")

    # --------------------------------------------------------------------
    # 5) Recomendaciones personalizadas según ratings
    # --------------------------------------------------------------------
    st.subheader("⭐ Recomendaciones basadas en tus calificaciones")

    if user_data is not None:
        # Volvemos a obtener el user, etc.
        users = pd.read_csv("./CSV/users.csv")
        current_user = user_data["username"]
        user_index = users[users["username"] == current_user].index[0]

        # Intentar cargar el diccionario de películas valoradas
        try:
            rated_movies = eval(users.at[user_index, "rated_movies"]) \
                if pd.notna(users.at[user_index, "rated_movies"]) else {}
        except (SyntaxError, ValueError):
            rated_movies = {}

        # Filtrar solo las películas que el usuario haya calificado con >= 4
        high_rated_movie_ids = [
            m_id for m_id, rating in rated_movies.items() if rating >= 4
        ]

        # Construir un DataFrame con las películas recomendadas
        recommendations = pd.DataFrame()

        for movie_id in high_rated_movie_ids:
            # Verificamos que 'movie_id' exista en la matriz de similitud
            if str(movie_id) in similarity_df.index:
                # similarity_df.loc[str(movie_id)] debería tener la fila
                # con similitudes respecto a esa película
                similar_scores = similarity_df.loc[str(movie_id)]
                # Ordenar desc y quedarnos con top 10
                top_similars = similar_scores.sort_values(ascending=False).head(10)

                # Convertir los índices a enteros (si la matrix usa str)
                # para cruzarlos con df
                top_sim_ids = top_similars.index.astype(int)

                # Sacamos la info de esas películas de df
                sim_movies_data = df[df["movie_id"].isin(top_sim_ids)]
                recommendations = pd.concat([recommendations, sim_movies_data])

        # Quitar duplicados y ordenar
        recommendations = recommendations.drop_duplicates() \
                                         .sort_values(by="average_score", ascending=False) \
                                         .head(5)

        if recommendations.empty:
            st.warning("No encontramos recomendaciones basadas en tus calificaciones.")
        else:
            cols = st.columns(min(len(recommendations), 5))
            for index, (_, row) in enumerate(recommendations.iterrows()):
                with cols[index % len(cols)]:
                    st.markdown(
                        f"""
                        <div style="text-align: center;">
                            <img src="{row['poster_url']}" alt="{row['title']}" style="width: 80%; border-radius: 10px;">
                            <h4>{row['title']}</h4>
                            <p><strong>Media de Ratings:</strong> {row['average_score']:.1f}/10</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    if st.button(f"Ver más sobre {row['title']}", key=f"rec_movie_{row['movie_id']}"):
                        st.session_state.current_page = "movie_details"
                        st.session_state.current_movie_id = row["movie_id"]
                        st.experimental_rerun()

    else:
        st.info("Inicia sesión para obtener recomendaciones personalizadas.")
