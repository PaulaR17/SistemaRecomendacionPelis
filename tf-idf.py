from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import numpy as np

# Read the preprocessed DataFrame
df_preprocessed = pd.read_csv("./CSV/preprocessed_peliculas.csv")
print("Shape of df_preprocessed:", df_preprocessed.shape)

# Identify categorical columns
categorical_columns = df_preprocessed.select_dtypes(include='object').columns

# Combine all categorical text into a single string per row
df_preprocessed['combined_text'] = df_preprocessed[categorical_columns].astype(str).agg(' '.join, axis=1)

# Vectorize the combined text column with TF-IDF
tfidf_vectorizer = TfidfVectorizer(max_features=10000)
tfidf_matrix = tfidf_vectorizer.fit_transform(df_preprocessed['combined_text'])

# Normalize numerical columns
numerical_columns = df_preprocessed.select_dtypes(include=['float64', 'int64']).columns
scaler = MinMaxScaler()
scaled_numerical = scaler.fit_transform(df_preprocessed[numerical_columns])

# Combine the scaled numerical data with the TF-IDF matrix
combined_features = np.hstack((tfidf_matrix.toarray(), scaled_numerical))
print("Combined feature matrix shape:", combined_features.shape)

# Save the combined features to a new CSV
combined_df = pd.DataFrame(combined_features)
combined_df.to_csv("./CSV/combined_features.csv", index=False)
print("Combined features saved.")
