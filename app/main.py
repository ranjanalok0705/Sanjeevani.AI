from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pymongo import MongoClient

app = FastAPI()

# Serve static files (CSS, JS, images, etc.)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# MongoDB connection setup
client = MongoClient("mongodb+srv://alokranjan700003:%40Alok123@sanjeevani.eu281.mongodb.net/")  # Adjust MongoDB URI if needed
db = client["disaster_db"]  # Replace with your actual database name
disasters_collection = db["ngo_dataset"]  # Replace with your collection name

# Set up Jinja2 for templating HTML
templates = Jinja2Templates(directory="app/static")

# Route for the index page (home page)
@app.get("/", response_class=HTMLResponse)
async def read_home():
    with open("app/static/index.html", "r") as file:
        return HTMLResponse(content=file.read())

# Route for the NGOs page
@app.get("/ngos", response_class=HTMLResponse)
async def read_ngos(request: Request):
    # Fetch disaster data from MongoDB
    disasters_data = disasters_collection.find()  # Retrieves all the documents in the collection
    
    # Convert the MongoDB data into a list of dictionaries
    disasters_list = list(disasters_data)

    # Pass the data to the template
    return templates.TemplateResponse("ngos.html", {"request": request, "disasters": disasters_list})
