from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

# Load combined features and titles
df_features = pd.read_csv("./CSV/combined_features.csv")
df_titles = pd.read_csv("./CSV/preprocessed_peliculas.csv")['title']

# Calculate cosine similarity
similarity_matrix = cosine_similarity(df_features)

# Convert similarity matrix to DataFrame
similarity_df = pd.DataFrame(similarity_matrix, index=df_titles, columns=df_titles)

# Save the updated similarity matrix
similarity_df.to_csv("./CSV/updated_similarity_matrix.csv", index=True)
print("Updated similarity matrix saved as 'updated_similarity_matrix.csv'")
