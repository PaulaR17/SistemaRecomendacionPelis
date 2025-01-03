import pandas as pd
import re  # regular expression operations
import nltk
import numpy as np
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity


# Initialize lemmatizer and stopwords
nltk.download('stopwords')
nltk.download('wordnet')
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()


def preprocess_1():
    # Function for text preprocessing
    def preprocess_text(text):
        text = text.lower()  # Convertimos todo el texto en minúsculas
        text = re.sub(r'[^\w\s\d]', '', text)  # Eliminamos caracteres especiales
        tokens = text.split()  # Dividimos el texto en palabras individuales
        tokens = [word for word in tokens if word not in stop_words]  # Eliminamos stop words
        tokens = [lemmatizer.lemmatize(word) for word in tokens]  # Lemmatizamos cada palabra
        return ' '.join(tokens)  # Unimos las palabras procesadas en una sola cadena

    # Load the original CSV file
    df = pd.read_csv("CSV/peliculas.csv")
    print("Dimensiones originales del dataset:", df.shape)

    # Identify and remove duplicates based on the title
    duplicates = df[df.duplicated(subset=['title'], keep=False)]
    print("Duplicados encontrados:")
    print(duplicates)

    df = df.drop_duplicates(subset=['title'], keep='first')
    print("Dimensiones después de eliminar duplicados:", df.shape)

    # Create a copy for preprocessing
    df_preprocess = df.copy()
    df_preprocess = df_preprocess.drop('link', axis=1)  # Eliminamos la columna 'link'

    df_preprocess = df_preprocess[['id','synopsis', 'consensus', 'type', 'critic_score', 'people_score', 'rating', 'genre',
                                   'original_language', 'director', 'producer', 'writer',
                                   'production_co', 'aspect_ratio', 'crew']]

    # Fill NULL values
    categorical_columns = df_preprocess.select_dtypes(include='object').columns
    print(f"Columnas categoricas{categorical_columns}")
    df_preprocess[categorical_columns] = df_preprocess[categorical_columns].fillna("Unknown")  # Text as "Unknown"

    numerical_columns = df_preprocess.select_dtypes(include=['float64', 'int64']).columns
    print(f"Columnas numericas {numerical_columns}")
    df_preprocess[numerical_columns] = df_preprocess[numerical_columns].fillna(0)  # Numbers as 0

    # Process non-numerical columns
    for col in categorical_columns:
        df_preprocess[col] = df_preprocess[col].apply(preprocess_text)

    print("Preprocesamiento COMPLETADO YAY!")
    return df_preprocess


def tf_idf_2(df_preprocessed):
    # 1) Columnas de texto
    categorical_columns = df_preprocessed.select_dtypes(include='object').columns

    # Combinar texto en 'combined_text'
    df_preprocessed['combined_text'] = df_preprocessed[categorical_columns].astype(str).agg(' '.join, axis=1)

    # Vectorizar con TF-IDF
    tfidf_vectorizer = TfidfVectorizer(max_features=10000)
    tfidf_matrix = tfidf_vectorizer.fit_transform(df_preprocessed['combined_text'])

    # 2) Columnas numéricas
    numerical_columns = df_preprocessed.select_dtypes(include=['float64', 'int64']).columns
    print("Columnas numéricas:", numerical_columns)

    scaler = MinMaxScaler()
    scaled_numerical = scaler.fit_transform(df_preprocessed[numerical_columns])

    # 3) Asignación de pesos
    # Ajusta estos valores según lo que desees
    text_weight = 0.7  # <--- peso para la parte TF-IDF (texto)
    numeric_weight = 0.3  # <--- peso para la parte numérica

    # Convertimos a array para multiplicar
    tfidf_array = tfidf_matrix.toarray()

    # Aplicamos los pesos a cada bloque
    tfidf_array_weighted = tfidf_array * text_weight
    scaled_numerical_weighted = scaled_numerical * numeric_weight

    # 4) Concatenar ambas partes en un solo array de features
    combined_features = np.hstack((tfidf_array_weighted, scaled_numerical_weighted))
    print("Combined feature matrix shape:", combined_features.shape)

    # Opcionalmente, puedes guardar el resultado como CSV (por si lo quieres verificar):
    combined_df = pd.DataFrame(combined_features)
    combined_df.to_csv("combined_features_weighted.csv", index=False)
    print("Combined features saved to 'combined_features_weighted.csv'.")

    return combined_df


def calculate_similarity_3(df_preprocessed,combined_df):
    # Calculate cosine similarity
    similarity_matrix = cosine_similarity(combined_df)

    # Convert similarity matrix to DataFrame
    similarity_df = pd.DataFrame(
        similarity_matrix,
        index=df_preprocessed['id'],
        columns=df_preprocessed['id']
    )

    # Save the updated similarity matrix
    similarity_df.to_csv("./CSV/similarity_matrix.csv", index=True)
    print("similarity matrix saved as 'similarity_matrix.csv'")


if __name__ == "__main__":
    df_preprocessed = preprocess_1()
    combined_df = tf_idf_2(df_preprocessed)
    calculate_similarity_3(df_preprocessed,combined_df)

