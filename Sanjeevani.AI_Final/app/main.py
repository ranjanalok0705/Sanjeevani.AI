from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
import requests
import joblib
import sys
import os
from model import predict_ngos
from pymongo import MongoClient
from fastapi import Form
from starlette.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from pydantic import BaseModel
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi import Depends, HTTPException
from pymongo import MongoClient
from bson import ObjectId
from starlette.middleware.sessions import SessionMiddleware
from datetime import datetime
import httpx



# Define the FastAPI app
app = FastAPI()

# Add Session Middleware
app.add_middleware(SessionMiddleware, secret_key="your_secret_key")

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
db = client["disaster_db"] 
disasters_collection = db["ngo_dataset"]  
users_collection = db["users"]  
organization=db["organization"]

vectorizer = joblib.load("app/models/vectorizer.pkl")
tfidf_matrix = joblib.load("app/models/tfidf_matrix.pkl")
ngos_data = list(disasters_collection.find({}, {"NGO ID": 1, "NGO Name": 1, "City": 1, "Contact": 1, "Email": 1, "category": 1, "request": 1}))
df = pd.DataFrame(ngos_data)

# Refresh the data in the DataFrame
def refresh_data():
    global df
    disasters_data = list(disasters_collection.find())  # Fetch fresh data
    df = pd.DataFrame(disasters_data)

# Set up Jinja2 for templating HTML
templates = Jinja2Templates(directory="app/templates")

# Route for the index page (home page)
@app.get("/", response_class=HTMLResponse)
async def read_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Route for the organization welcome page
@app.get("/orgwelcome/", response_class=HTMLResponse)
async def org_welcome(request: Request):
    org_id = request.session.get("ngoId")  # Fetch logged-in organization's ID
    if not org_id:
        raise HTTPException(status_code=401, detail="Not logged in as an organization")

    # Fetch the organization's name from the database
    organization_data = disasters_collection.find_one({"NGO ID": org_id}, {"_id": 0, "NGO Name": 1})
    if not organization_data:
        raise HTTPException(status_code=404, detail="Organization not found")

    return templates.TemplateResponse(
        "orgwelcome.html", 
        {"request": request, "org_name": organization_data.get("NGO Name", "Organization")}
    )

# Route for the NGOs page
@app.get("/ngos", response_class=HTMLResponse)
async def read_ngos(request: Request):
    disasters_data = disasters_collection.find()  # Retrieves all the documents in the collection
    disasters_list = list(disasters_data)
    return templates.TemplateResponse("ngos.html", {"request": request, "disasters": disasters_list})

@app.get("/orgLogin", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("orgLogin.html", {"request": request})

# Route for About page    
@app.get("/about", response_class=HTMLResponse)
async def about_page(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

# Route for Login form submission (POST)
@app.post("/orgLogin")
async def login(request: Request,email: str = Form(...), password: str = Form(...)):
    user = disasters_collection.find_one({"Email": email, "Password": password})
    if user:
        request.session["ngoId"] = user["NGO ID"]    
        return RedirectResponse(url="/orgwelcome", status_code=302)  # Redirect to orgwelcome after successful login
    return HTMLResponse(content="Invalid credentials. Try again.")

@app.get("/userLogin", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("userLogin.html", {"request": request})

# Route for Login form submission (POST)
@app.post("/userLogin")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    user = users_collection.find_one({"email": email, "password": password})
    if user:
        request.session["user_email"] = email
        return RedirectResponse(url="/userwelcome", status_code=302)
    return HTMLResponse(content="Invalid credentials. Try again.")


@app.get("/userwelcome", response_class=HTMLResponse)
async def user_welcome(request: Request):
    return templates.TemplateResponse("userwelcome.html", {"request": request})

# Route for User Registration page (GET)
@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Route for Registration form submission (POST)
@app.post("/register")
async def register(
    name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    if users_collection.find_one({"email": email}):
        return HTMLResponse(content="User already exists.", status_code=400)
    
    users_collection.insert_one({
        "name": name,
        "phone": phone,
        "email": email,
        "password": password
    })

    return HTMLResponse(
        content="<script>alert('User registered successfully!'); window.location.href='/userLogin';</script>",
        status_code=200
    )

@app.get("/orgregister", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("orgregister.html", {"request": request})

# Route for Registration form submission (POST)
@app.post("/orgregister")
async def register(
    name: str = Form(...),
    id: str = Form(...),
    city: str = Form(...),
    category: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    if disasters_collection.find_one({"email": email}):
        return HTMLResponse(content="Organization already exists.", status_code=400)
    
    disasters_collection.insert_one({
        "NGO Name": name,
        "NGO ID": id,
        "City": city,
        "Latitude":"14.08830248",
        "Longitude":"84.96575639",
        "Contact": phone,
        "Email": email,
        "Password": password,
        "category": category,
        "request": "Help"
    })

    return HTMLResponse(
        content="<script>alert('Organization registered successfully!'); window.location.href='/orgLogin';</script>",
        status_code=200
    )

@app.post("/predict", response_class=HTMLResponse)
async def predict(request: Request, user_input: str = Form(...)):
    """Predict similar NGOs based on user input"""
    top_ngos_df = predict_ngos(user_input, top_n=20)
    top_ngos = top_ngos_df.to_dict(orient="records") if not top_ngos_df.empty else []
    return templates.TemplateResponse("predict.html", {"request": request, "user_input": user_input, "ngos": top_ngos})

class FilterRequest(BaseModel):
    city: str
    disasterCategory: str

@app.post("/filter", response_class=HTMLResponse)
async def filter_ngos(request: Request,user_input: str = Form(...), city: str = Form(...)):
    """Filter NGOs based on disaster category and city."""   
    refresh_data()
    ngos_df = predict_ngos(user_input, top_n=200)  # Get top 200 matching NGOs first

    # Convert DataFrame to list of dictionaries
    ngos_list = ngos_df.to_dict(orient="records") if not ngos_df.empty else []

    # Filter by city
    filtered_ngos = [ngo for ngo in ngos_list if ngo["City"].lower() == city.lower()]

    # Return only top 10 results after filtering
    filtered_ngos = filtered_ngos[:10]
    return templates.TemplateResponse(
        "filter.html",  
        {"request": request,  "city": city, "user_input": user_input, "ngos": filtered_ngos}
    )

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = "sanjeevani.ai.helpline@gmail.com"
SMTP_PASSWORD = "spxk aqqi kyue fwsw"  # ⚠ Ensure to use environment variables in production!
myemail="sexede6519@intady.com"

# Define request schema
class NotificationRequest(BaseModel):
    org_email: str
    message: str

def send_email(subject, message):
    """Function to send an email (replace with actual SMTP credentials)."""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    msg = MIMEMultipart()
    msg['From'] = SMTP_EMAIL
    msg['To'] = myemail
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, myemail, msg.as_string())

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email sending failed: {str(e)}")


async def get_public_ip():
    url = "https://api64.ipify.org?format=json"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json().get("ip", "N/A")


async def get_ip_location(ip: str):
    url = f"http://ip-api.com/json/{ip}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()

        # Return location data along with the original IP
        return {
            "ip": ip,  # Explicitly adding the IP
            "country": data.get("country", "N/A"),
            "region": data.get("regionName", "N/A"),
            "city": data.get("city", "N/A"),
            "latitude": data.get("lat", "N/A"),
            "longitude": data.get("lon", "N/A"),
            "isp": data.get("isp", "N/A"),
        }


from datetime import datetime

@app.post("/send-notification/")
async def send_notification(background_tasks: BackgroundTasks, request: Request, notification: dict):
    """Send an email with NGO details, user data, and IP location, and store the request in MongoDB."""

    email = request.session.get("user_email")
    if not email:
        raise HTTPException(status_code=401, detail="Not logged in")

    user = users_collection.find_one({"email": email}, {"_id": 0, "phone": 1, "name": 1, "email": 1})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get client's IP address
    client_ip = await get_public_ip()  
    ip_location = await get_ip_location(client_ip)  
    city = ip_location.get("city", "Unknown")

    # Get current date & time
    current_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")

    # Extract severity from the notification message
    message_content = notification.get("message", "")
    message_parts = message_content.split()
    print(message_parts)
    severity = message_parts[-1]
    category=message_parts[-5]
    ngo_id=message_parts[8]
    # Construct email message
    message = f"""
Dear Disaster Aid Network Team,\n\t\tWe have received an urgent help request from a user in your service area. Below are the details:
    \n
    - User Name: {user['name']}
    - Phone: 📞 {user['phone']}
    - Email:✉️ {user['email']}
    \n
    📍 User Location:
    - IP Address: {ip_location.get('ip', 'N/A')}
    - Country: {ip_location.get('country', 'N/A')}
    - Region: {ip_location.get('region', 'N/A')}
    - City:{city}
    - Latitude/Longitude:{ip_location.get('latitude', 'N/A')},{ip_location.get('longitude', 'N/A')}
    - Internet Provider: {ip_location.get('isp', 'N/A')}
    
    \n
    🏢 Assigned NGO Details: 
    {message_content}
    \n
    🚀 Immediate Action Required:\nPlease coordinate with the user at the earliest and provide the necessary assistance. Kindly update us on the status of this request once action is taken.
\n
For any further queries, feel free to reach out.
\n
Best Regards,
Sanjeevani AI -- Disaster Management Team
📞 +91 62054 62054
📧 sanjeevani.ai.helpline@gmail.com
    """

    # Insert the request into the MongoDB organization collection
    organization.insert_one({
        "place_of_request": city,
        "date_time": current_time,
        "severity_level": severity,
        "category":category,
        "ngoId": ngo_id
        })

    background_tasks.add_task(send_email, "🚨 Urgent Help Request 🚨", message)
    
    return {"message": "Email notification sent successfully and request stored in the database!"}



@app.get("/recent-requests/")
async def get_recent_requests(request: Request):
    """Fetch the 5 most recent requests for the logged-in organization."""
    
    org_id = request.session.get("ngoId")  # Fetch logged-in organization ID
    if not org_id:
        raise HTTPException(status_code=401, detail="Not logged in as an organization")

    # Fetch the last 5 requests sorted by date_time (newest first)
    recent_requests = list(
        organization.find({"ngoId": org_id})
        .sort("date_time", -1)
        .limit(3)
    )

    # Convert ObjectId to string and format response
    for req in recent_requests:
        req["_id"] = str(req["_id"])

    return JSONResponse(content={"requests": recent_requests})



@app.get("/all_requests/",response_class=HTMLResponse)
async def get_all_requests(request: Request):
    """Fetch  all  requests for the logged-in organization."""
    
    org_id = request.session.get("ngoId")  # Fetch logged-in organization ID
    if not org_id:
        raise HTTPException(status_code=401, detail="Not logged in as an organization")

    # Fetch the organization's name from the database
    organization_data = disasters_collection.find_one({"NGO ID": org_id}, {"_id": 0, "NGO Name": 1})
    if not organization_data:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Fetch the last 5 requests sorted by date_time (newest first)
    recent_requests = list(
        organization.find({"ngoId": org_id})
        .sort("date_time", -1)
    )

    # Convert ObjectId to string and format response
    for req in recent_requests:
        req["_id"] = str(req["_id"])

    return templates.TemplateResponse(
        "orgrequests.html", 
        {"request": request, "requests": recent_requests,"org_name": organization_data.get("NGO Name", "Organization")}
    )