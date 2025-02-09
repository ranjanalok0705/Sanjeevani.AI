
# import json
# from pymongo import MongoClient

# # Connect to MongoDB
# client = MongoClient('mongodb+srv://alokranjan700003:%40Alok123@sanjeevani.eu281.mongodb.net/')  # Replace with your MongoDB connection string
# db = client['disaster_db']  # Replace with your database name
# collection = db['ngo_dataset']  # Replace with your collection name

# # Read the JSON file
# with open('data.json', mode='r', encoding='utf-8') as json_file:
#     data = json.load(json_file)  # Load JSON data into a Python list of dictionaries

# # Insert the data into MongoDB
# if data:
#     collection.insert_many(data)  # Insert all documents at once
#     print("Data inserted successfully!")
# else:
#     print("No data to insert.")

# # Close the connection
# client.close()


from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb+srv://alokranjan700003:%40Alok123@sanjeevani.eu281.mongodb.net/")
db = client["disaster_db"]
collection = db["ngo_dataset"]

# Update all documents by adding a new key-value pair
collection.update_many({}, {"$set": {"request": "Help"}})

print("Added 'request': 'Help' to all documents successfully.")
