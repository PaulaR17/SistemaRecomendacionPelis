import pandas as pd

# Load original CSV to get the correct movie titles
original_csv_path = "CSV/peliculas.csv"
original_df = pd.read_csv(original_csv_path)

# Load updated similarity matrix
similarity_matrix_path = "CSV/updated_similarity_matrix.csv"
updated_similarity_df = pd.read_csv(similarity_matrix_path)

# Map the original titles to the similarity matrix
corrected_titles = original_df['title'].drop_duplicates().reset_index(drop=True)
updated_similarity_df['title'] = corrected_titles

# Save the corrected similarity matrix
corrected_similarity_matrix_path = "CSV/corrected_similarity_matrix.csv"
updated_similarity_df.to_csv(corrected_similarity_matrix_path, index=False)

print(f"Corrected similarity matrix saved to {corrected_similarity_matrix_path}")
