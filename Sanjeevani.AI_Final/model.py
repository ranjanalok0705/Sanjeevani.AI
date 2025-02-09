# Import necessary libraries
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import os
from pymongo import MongoClient
from fuzzywuzzy import process

# Load MongoDB credentials from environment variables
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://alokranjan700003:%40Alok123@sanjeevani.eu281.mongodb.net/")  # Store safely in env vars
client = MongoClient(MONGO_URI)
db = client["disaster_db"]  # Replace with actual database name
disasters_collection = db["ngo_dataset"]  # Collection with NGO data

# Retrieve the NGO data from MongoDB
disasters_data = list(disasters_collection.find())

# Convert data into a pandas DataFrame
df = pd.DataFrame(disasters_data)

# Ensure the 'category' column exists
if 'category' not in df.columns:
    raise ValueError("The dataset does not contain a 'category' column.")

df['category'] = df['category'].astype(str)

# Train the TF-IDF model
vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
tfidf_matrix = vectorizer.fit_transform(df['category'])

# Ensure the directory exists
os.makedirs("app/models", exist_ok=True)

# Save the trained model
joblib.dump(vectorizer, "app/models/vectorizer.pkl")
joblib.dump(tfidf_matrix, "app/models/tfidf_matrix.pkl")

print("TF-IDF model saved successfully.")

# Function to predict NGOs based on user input
def predict_ngos(user_input, top_n=50, threshold=70):
    user_input = user_input.lower().strip()

    # Use fuzzy matching to find best-matching disaster categories
    unique_categories = df['category'].unique()
    matched_categories = set()

    for word in user_input.split():
        match = process.extractOne(word, unique_categories)
        if match:  # Ensure a match was found
            best_match, score = match
            if score >= threshold:
                matched_categories.add(best_match)

    # If fuzzy matching found results, filter NGOs based on those categories
    if matched_categories:
        matching_ngos = df[df['category'].isin(matched_categories)].head(top_n)
        return matching_ngos[['NGO ID','NGO Name', 'City', 'Contact', 'Email', 'category','request']]

    # **No direct match found – fallback to TF-IDF similarity**
    print("No exact match found. Suggesting the closest NGOs instead...")

    # Transform user input using the same TF-IDF vectorizer
    user_vector = vectorizer.transform([user_input])

    # Compute cosine similarity between user input and NGO categories
    similarity_scores = cosine_similarity(user_vector, tfidf_matrix).flatten()

    # Get top N most similar NGOs
    top_indices = similarity_scores.argsort()[-top_n:][::-1]  # Sort in descending order

    # Retrieve NGOs based on similarity ranking
    closest_ngos = df.iloc[top_indices]

    return closest_ngos[['NGO ID','NGO Name', 'City', 'Contact', 'Email', 'category','request']]


# # Test with user input
# user_input = input("Enter disaster categories: ")
# predicted_ngos = predict_ngos(user_input)

# # Display results
# if not predicted_ngos.empty:
#     print(predicted_ngos)
# else:
#     print("No matching NGOs found.")

