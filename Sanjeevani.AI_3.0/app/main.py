from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
import joblib
from pymongo import MongoClient
from fastapi import Form
from starlette.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from pydantic import BaseModel


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (use specific domains in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)
# Serve static files (CSS, JS, images, etc.)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# MongoDB connection setup
client = MongoClient("mongodb+srv://alokranjan700003:%40Alok123@sanjeevani.eu281.mongodb.net/")  # Adjust MongoDB URI if needed
db = client["disaster_db"]  # Replace with your actual database name
disasters_collection = db["ngo_dataset"]  # Replace with your collection name
users_collection = db["users"]  # Replace with your actual collection name

vectorizer = joblib.load("app/models/vectorizer.pkl")
tfidf_matrix = joblib.load("app/models/tfidf_matrix.pkl")
ngos_data = list(disasters_collection.find({}, {"NGO ID": 1, "NGO Name": 1, "City": 1, "Contact": 1, "Email": 1, "category": 1}))
df = pd.DataFrame(ngos_data)

# Set up Jinja2 for templating HTML
templates = Jinja2Templates(directory="app/templates")

# Route for the index page (home page)
@app.get("/", response_class=HTMLResponse)
async def read_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Route for the organization welcome page
@app.get("/orgwelcome", response_class=HTMLResponse)
async def org_welcome(request: Request):
    return templates.TemplateResponse("orgwelcome.html", {"request": request})

# Route for the NGOs page
@app.get("/ngos", response_class=HTMLResponse)
async def read_ngos(request: Request):
    disasters_data = disasters_collection.find()  # Retrieves all the documents in the collection
    disasters_list = list(disasters_data)
    return templates.TemplateResponse("ngos.html", {"request": request, "disasters": disasters_list})

@app.get("/orgLogin", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("orgLogin.html", {"request": request})

# Route for Login form submission (POST)
@app.post("/orgLogin")
async def login(email: str = Form(...), password: str = Form(...)):
    user = users_collection.find_one({"email": email, "password": password})
    if user:
        return RedirectResponse(url="/orgwelcome", status_code=302)  # Redirect to orgwelcome after successful login
    return HTMLResponse(content="Invalid credentials. Try again.")

@app.get("/userLogin", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("userLogin.html", {"request": request})

# Route for Login form submission (POST)
@app.post("/userLogin")
async def login(email: str = Form(...), password: str = Form(...)):
    user = users_collection.find_one({"email": email, "password": password})
    if user:
        return RedirectResponse(url="/userwelcome", status_code=302)
    return HTMLResponse(content="Invalid credentials. Try again.")


@app.get("/userwelcome", response_class=HTMLResponse)
async def user_welcome(request: Request):
    return templates.TemplateResponse("userwelcome.html", {"request": request})

# Route for Registration page (GET)
@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Route for Registration form submission (POST)
@app.post("/register")
async def register(name: str = Form(...), email: str = Form(...), password: str = Form(...), userType: str = Form(...)):
    if users_collection.find_one({"email": email}):
        return HTMLResponse(content="User already exists.", status_code=400)
    users_collection.insert_one({"name": name, "email": email, "password": password, "userType": userType})
    return HTMLResponse(content="<script>alert('User registered successfully!'); window.location.href='/userLogin';</script>", status_code=200)

@app.post("/predict", response_class=HTMLResponse)
async def predict(request: Request, user_input: str = Form(...)):
    """Predict similar NGOs based on user input"""
    user_tfidf = vectorizer.transform([user_input])
    similarities = cosine_similarity(user_tfidf, tfidf_matrix).flatten()
    top_indices = similarities.argsort()[::-1][:10]
    top_ngos = df.iloc[top_indices].to_dict(orient="records")
    return templates.TemplateResponse("predict.html", {"request": request, "user_input": user_input, "ngos": top_ngos})



@app.post("/filter", response_class=HTMLResponse)
async def filter_ngos(request: Request, city: str = Form(...), disasterCategory: str = Form(...)):
    """Filter NGOs based on disaster category and city."""
    user_tfidf = vectorizer.transform([disasterCategory])
    similarities = cosine_similarity(user_tfidf, tfidf_matrix).flatten()

    # Get top 10 similar NGOs based on disaster category
    top_indices = similarities.argsort()[::-1][:50]
    top_ngos = df.iloc[top_indices]

    # Filter NGOs by selected city
    filtered_ngos = top_ngos[top_ngos["City"].str.lower() == city.lower()]

    return templates.TemplateResponse(
        "filter.html",  
        {"request": request, "city": city, "disasterCategory": disasterCategory, "ngos": filtered_ngos.to_dict(orient="records")}
    )
