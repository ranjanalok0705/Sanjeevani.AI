from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pymongo import MongoClient
from fastapi import Form
from starlette.responses import RedirectResponse



app = FastAPI()

# Serve static files (CSS, JS, images, etc.)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# MongoDB connection setup
client = MongoClient("mongodb+srv://alokranjan700003:%40Alok123@sanjeevani.eu281.mongodb.net/")  # Adjust MongoDB URI if needed
db = client["disaster_db"]  # Replace with your actual database name
disasters_collection = db["ngo_dataset"]  # Replace with your collection name
users_collection = db["users"]  # Replace with your actual collection name


# Set up Jinja2 for templating HTML
templates = Jinja2Templates(directory="app/static")

# Route for the index page (home page)
@app.get("/", response_class=HTMLResponse)
async def read_home():
    with open("app/static/index.html", "r") as file:
        return HTMLResponse(content=file.read())

# Route for the index page (home page)       
@app.get("/userwelcome", response_class=HTMLResponse)
async def read_home():
    with open("app/static/userwelcome.html", "r") as file:
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

@app.get("/orgLogin", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("orgLogin.html", {"request": request})

# Route for Login form submission (POST)
@app.post("/orgLogin")
async def login(email: str = Form(...), password: str = Form(...)):
    user = users_collection.find_one({"email": email, "password": password})
    if user:
        return RedirectResponse(url="/", status_code=302)
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
    return RedirectResponse(url="/login", status_code=302)

