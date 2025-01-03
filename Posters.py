import requests
import pandas as pd
import os

# Leer la API Key desde un archivo local
with open("api_key.txt", "r") as f:
    API_KEY = f.read().strip()

# Endpoint base de TMDB
BASE_URL = "https://api.themoviedb.org/3"

# Diccionario para traducir géneros
GENRE_TRANSLATION = {
    "acción": "action",
    "aventura": "adventure",
    "ciencia ficción": "sci fi",
    "comedia": "comedy",
    "drama": "drama",
    "fantasía": "fantasy",
    "horror": "horror",
    "misterio": "mystery and thriller",
    "romance": "romance",
    "animación": "animation",
    "documental": "documentary",
    "musical": "musical",
    "historia": "history",
    "guerra": "war",
    "crimen": "crime",
    "infantil": "kids and family",
    "otros": "other",
    # Añade más si es necesario
}

def translate_genres(genres):
    """Traduce los géneros de español a inglés usando GENRE_TRANSLATION."""
    if pd.isna(genres):
        return "Desconocido"  # Reemplazar géneros nulos por 'Desconocido'
    translated_genres = []
    for genre in genres.split(", "):
        genre_lower = genre.strip().lower()
        translated_genres.append(GENRE_TRANSLATION.get(genre_lower, genre_lower))  # Traduce o deja igual si no está en el diccionario
    return ", ".join(translated_genres)

def get_movie_poster(title):
    """Obtiene el póster de una película desde la API de TMDB."""
    url = f"{BASE_URL}/search/movie"
    params = {
        "api_key": API_KEY,
        "query": title
    }
    response = requests.get(url, params=params).json()

    if response.get("results"):  # Si hay resultados, toma el primer póster
        poster_path = response["results"][0].get("poster_path")
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"  # URL completa del póster
    return "No Poster Found"

# Cargar el dataset de películas
df = pd.read_csv("CSV/peliculas.csv")

# Traducir géneros al inglés
df["genre"] = df["genre"].apply(translate_genres)

# Eliminar duplicados por título
duplicates = df[df.duplicated(subset=['title'], keep=False)]
print("Duplicados encontrados:")
print(duplicates)
df = df.drop_duplicates(subset=['title'], keep='first')

# Rellenar valores nulos
categorical_columns = df.select_dtypes(include="object").columns
numerical_columns = df.select_dtypes(include=["int64", "float64"]).columns

df[categorical_columns] = df[categorical_columns].fillna("Desconocido")  # Textos como 'Desconocido'
df[numerical_columns] = df[numerical_columns].fillna(0)  # Valores numéricos como 0

# Calcular 'average_score'
if "critic_score" in df.columns and "people_score" in df.columns:
    df["average_score"] = (df["critic_score"] + df["people_score"]) / 2
else:
    df["average_score"] = 0  # Si no existen las columnas, inicializar como 0

# Agregar la columna de URLs de pósters
df['poster_url'] = df['title'].apply(get_movie_poster)

# Guardar el nuevo dataset
df.to_csv("./CSV/peliculas_with_posters.csv", index=False)
print("Posters obtenidos, géneros traducidos, nulos manejados, promedio calculado y dataset guardado.")
