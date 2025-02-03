# Import necessary libraries
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import os
from pymongo import MongoClient

# MongoDB connection setup
client = MongoClient("mongodb+srv://alokranjan700003:%40Alok123@sanjeevani.eu281.mongodb.net/")  # Adjust MongoDB URI if needed
db = client["disaster_db"]  # Replace with your actual database name
disasters_collection = db["ngo_dataset"]  # Replace with your collection name
users_collection = db["users"]  # Replace with your actual collection name

# Retrieve the NGO data from MongoDB
disasters_data = disasters_collection.find()

# Convert the MongoDB data into a list of dictionaries
disasters_list = list(disasters_data)

# Convert the list of dictionaries into a pandas DataFrame
df = pd.DataFrame(disasters_list)

# Ensure the 'Disaster Categories' column exists and is of type string
df['category'] = df['category'].astype(str)

vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(df['category'])

# Ensure directory exists
os.makedirs("models", exist_ok=True)

# Save vectorizer and matrix
joblib.dump(vectorizer, "models/vectorizer.pkl")
joblib.dump(tfidf_matrix, "models/tfidf_matrix.pkl")

print("TF-IDF model saved successfully in 'models/' directory.")

# Function to predict similar NGOs based on user input
def predict_ngos(user_input, top_n=10):
    # Transform the user input using the same vectorizer
    user_tfidf = vectorizer.transform([user_input])
    
    # Compute cosine similarity between the user input and the NGOs' disaster categories
    similarities = cosine_similarity(user_tfidf, tfidf_matrix).flatten()
    
    # Get the indices of the top N most similar NGOs
    top_indices = similarities.argsort()[::-1][:top_n]
    
    # Return the top N most similar NGOs
    return df.iloc[top_indices][['NGO Name','City','Contact','Email','category']]

# Test the model with an example user input
user_input = input('enter ur issue:')
predicted_ngos = predict_ngos(user_input)
print(predicted_ngos)
