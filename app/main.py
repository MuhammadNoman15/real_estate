import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .db import get_db, User, TokenBlacklist
from pydantic import BaseModel
from passlib.context import CryptContext
from dotenv import load_dotenv
import requests
from geopy.distance import geodesic
import csv
from datetime import date, datetime, timedelta
import openai  # Import the OpenAI library
import re  # Import the re module for regex
from jose import JWTError, jwt
from typing import Optional

load_dotenv()

# API Keys
GEOCODING_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
PLACES_API_KEY = os.getenv("NEXT_PUBLIC_GOOGLE_PLACES_API_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Debug print (mask key for safety)
print("GEOCODING_API_KEY loaded:", bool(GEOCODING_API_KEY))
print("PLACES_API_KEY loaded:", bool(PLACES_API_KEY))
print("OPENAI_API_KEY loaded:", bool(openai.api_key))
print("JWT_SECRET_KEY loaded:", bool(JWT_SECRET_KEY))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

app = FastAPI(title="Real Estate Search MVP")


# ============= PYDANTIC MODELS =============
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    confirm_password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

class TokenData(BaseModel):
    email: Optional[str] = None


# ============= PASSWORD UTILITIES =============
def get_password_hash(password):
    return pwd_context.hash(password[:72])


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# ============= JWT UTILITIES =============
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str, db: Session) -> Optional[dict]:
    """Verify JWT token and check if it's blacklisted"""
    try:
        # Check if token is blacklisted
        blacklisted = db.query(TokenBlacklist).filter(TokenBlacklist.token == token).first()
        if blacklisted:
            return None
        
        # Decode and verify token
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return payload
    except JWTError:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    
    payload = verify_token(token, db)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


# ============= ENDPOINTS =============
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/query")
def query_router(
    payload: dict,
    current_user: User = Depends(get_current_user)
):
    # Placeholder: will implement deterministic parsing and SQL calls
    return {"message": "Query endpoint stub", "input": payload}


@app.post("/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash the password
    hashed_password = get_password_hash(user.password)
    
    new_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}


@app.post("/login", response_model=Token)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    """Login endpoint - returns JWT token"""
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email, "user_id": db_user.id},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email
        }
    }


@app.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Logout endpoint - blacklists the JWT token"""
    token = credentials.credentials
    
    # Verify token first
    payload = verify_token(token, db)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # Get token expiration
    exp_timestamp = payload.get("exp")
    expires_at = datetime.fromtimestamp(exp_timestamp)
    
    # Add token to blacklist
    blacklisted_token = TokenBlacklist(
        token=token,
        expires_at=expires_at
    )
    db.add(blacklisted_token)
    db.commit()
    
    return {"message": "Successfully logged out"}





class AddressQuery(BaseModel):
    address: str

@app.post("/assessment")
async def get_bc_assessment(
    query: AddressQuery,
    current_user: User = Depends(get_current_user)
):
    address = query.address
    geocoding_data = get_geocoding_data(address, GEOCODING_API_KEY)
    if geocoding_data:
        place_id = geocoding_data.get('place_id')
        places_data = get_places_data(place_id, PLACES_API_KEY)
        if places_data:
            # Placeholder for BC Assessment value
            return {
                "query": "BC Assessment Value",
                "data": {
                    "property_address": geocoding_data.get('formatted_address'),
                    "assessed_value": "$2,450,000",  # Placeholder value
                    "land_value": "$1,700,000",  # Placeholder value
                    "improvement_value": "$750,000",  # Placeholder value
                    "assessment_year": 2024,  # Placeholder year
                    "lat": geocoding_data.get('geometry', {}).get('location', {}).get('lat'),
                    "lng": geocoding_data.get('geometry', {}).get('location', {}).get('lng')
                }
            }
    raise HTTPException(status_code=404, detail="Unable to retrieve BC Assessment value.")


def get_geocoding_data(address, api_key):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": api_key
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            return data['results'][0]  # Return the first result
    return None


def get_places_data(place_id, api_key):
    base_url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "key": api_key
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            return data['result']
    return None



def get_nearby_schools(lat, lng, api_key, radius=1000):
    base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "type": "school",
        "key": api_key
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            return data['results']
    return []

@app.post("/nearby-schools")
async def nearby_schools(
    query: AddressQuery,
    current_user: User = Depends(get_current_user)
):
    address = query.address
    geocoding_data = get_geocoding_data(address, GEOCODING_API_KEY)
    if geocoding_data:
        lat = geocoding_data.get('geometry', {}).get('location', {}).get('lat')
        lng = geocoding_data.get('geometry', {}).get('location', {}).get('lng')
        schools = get_nearby_schools(lat, lng, PLACES_API_KEY)
        return {
            "query": "Nearby Schools",
            "data": [
                {
                    "name": school.get('name'),
                    "address": school.get('vicinity')
                    
                }
                for school in schools
            ]
        }
    raise HTTPException(status_code=404, detail="Unable to retrieve nearby schools.")

@app.post("/school-catchment")
async def school_catchment(
    query: AddressQuery,
    current_user: User = Depends(get_current_user)
):
    address = query.address
    geocoding_data = get_geocoding_data(address, GEOCODING_API_KEY)
    if geocoding_data:
        lat = geocoding_data.get('geometry', {}).get('location', {}).get('lat')
        lng = geocoding_data.get('geometry', {}).get('location', {}).get('lng')
        catchment_data = get_school_catchment(lat, lng)
        return {
            "query": "School Catchment",
            "data": catchment_data
        }
    raise HTTPException(status_code=404, detail="Unable to retrieve school catchment.")

def get_school_catchment(lat, lng):
    base_url = "https://opendata.vancouver.ca/api/explore/v2.1/catalog/datasets/schools/records"
    params = {"limit": 194}
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        closest_school = find_closest_school(lat, lng, data['results'])
        if closest_school:
            return {
                "school_name": closest_school['school_name'],
                "category": closest_school['school_category'],
                "address": closest_school['address'],
                "geo_local_area": closest_school['geo_local_area']
            }
    return "No nearby school catchment found."

def find_closest_school(lat, lng, schools):
    min_distance = float('inf')
    closest_school = None
    for school in schools:
        school_lat = school['geo_point_2d']['lat']
        school_lon = school['geo_point_2d']['lon']
        distance = geodesic((lat, lng), (school_lat, school_lon)).kilometers
        if distance < min_distance:
            min_distance = distance
            closest_school = school
    return closest_school



def get_nearby_transit_stations(lat, lng, api_key, radius=1000):
    base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "type": "transit_station",
        "key": api_key
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            return data['results']
    return []

@app.post("/nearest-transit")
async def nearest_transit(
    query: AddressQuery,
    current_user: User = Depends(get_current_user)
):
    address = query.address
    geocoding_data = get_geocoding_data(address, GEOCODING_API_KEY)
    if geocoding_data:
        lat = geocoding_data.get('geometry', {}).get('location', {}).get('lat')
        lng = geocoding_data.get('geometry', {}).get('location', {}).get('lng')
        
        # Find nearby transit stations
        transit_stations = get_nearby_transit_stations(lat, lng, PLACES_API_KEY)
        
        return {
            "query": "Nearest Transit Stations",
            "data": [
                {
                    "name": station['name']
                   
                }
                for station in transit_stations
            ]
        }
    raise HTTPException(status_code=404, detail="Unable to retrieve transit stations.")

@app.post("/nearby-parks-and-centres")
async def nearby_parks_and_centres(
    query: AddressQuery,
    current_user: User = Depends(get_current_user)
):
    address = query.address
    geocoding_data = get_geocoding_data(address, GEOCODING_API_KEY)
    if geocoding_data:
        lat = geocoding_data.get('geometry', {}).get('location', {}).get('lat')
        lng = geocoding_data.get('geometry', {}).get('location', {}).get('lng')

        # Retrieve and filter parks
        parks_data = get_nearby_places(lat, lng, PLACES_API_KEY, 'park', keyword="park|playground|trail|dog_park")
        parks = filter_places(parks_data, lat, lng, {"park", "playground", "trail", "dog_park"})

        # Retrieve and filter community centres
        centres_data = get_nearby_places(lat, lng, PLACES_API_KEY, 'establishment', keyword="community center|recreation center")
        centres = filter_places(centres_data, lat, lng, {"community_center", "recreation_center"})

        return {
            "query": "Nearby Parks and Community Centres",
            "address": address,
            "radius_m": 1000,
            "results": {
                "parks": parks,
                "communities": centres
            },
            "source": "Google Places",
            "last_updated": date.today().isoformat()
        }
    raise HTTPException(status_code=404, detail="Unable to retrieve nearby parks and community centres.")

def filter_places(places_data, lat, lng, allowed_types):
    filtered = []
    seen = set()
    for place in places_data:
        if any(t in allowed_types for t in place.get('types', [])):
            place_lat = place['geometry']['location']['lat']
            place_lng = place['geometry']['location']['lng']
            distance_m = int(geodesic((lat, lng), (place_lat, place_lng)).meters)
            walking_time_min = int(distance_m / 80)  # Average walking speed ~80 m/min
            if place['name'] not in seen:
                place_address = place.get('vicinity') or "No address available"
                seen.add(place['name'])
                filtered.append({
                    "name": place['name'],
                    "type": "community_centre" if "community_center" in place.get('types', []) else "park",
                    "address": place_address,
                    "latitude": round(place_lat, 4),
                    "longitude": round(place_lng, 4),
                    "distance_m": distance_m,
                    "walking_time_min": walking_time_min,
                    "maps_url": f"https://maps.google.com/?q={place_lat},{place_lng}"
                })

    # Sort and limit to top 5
    filtered.sort(key=lambda x: x['distance_m'])
    filtered = filtered[:5]
    for i, place in enumerate(filtered):
        place['rank'] = i + 1

    return filtered

def get_nearby_places(lat, lng, api_key, place_type, radius=1500, keyword=None):
    base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "type": place_type,
        "key": api_key
    }
    if keyword:
        params["keyword"] = keyword
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            return data['results']
    return []

# Load OpenAI API key securely from .env file or environment
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.post("/chat")
async def chat_with_ai(
    query: dict,
    current_user: User = Depends(get_current_user)
):
    user_query = query.get("query")

    if not user_query:
        raise HTTPException(status_code=400, detail="No query provided")

    # Determine the API action based on the user query
    api_response = await determine_api_action(user_query)

    return api_response

async def determine_api_action(user_query: str):
    try:
        from openai import OpenAI
        import json
        client = OpenAI()  # uses the OPENAI_API_KEY from env

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an intelligent assistant that maps natural language queries "
                        "to API endpoints for a real estate assistant app.\n\n"
                        "Available endpoints:\n"
                        "- 'schools': For nearby schools queries\n"
                        "- 'school_catchment': For school catchment area queries\n"
                        "- 'transit': For nearby transit, bus stops, skytrain stations\n"
                        "- 'parks': For nearby parks, community centres, trails, recreation\n"
                        "- 'assessment': For BC assessment value, property value queries\n"
                        "- 'unsupported': For any other query type (hospitals, restaurants, etc.)\n\n"
                        "Respond ONLY with the endpoint name from the list above. "
                        "Do not include any explanation or extra text."
                    ),
                },
                {
                    "role": "user",
                    "content": f"User query: {user_query}\n\nWhich endpoint?",
                },
            ],
            max_tokens=20,
        )

        # Get the action from LLM
        action = response.choices[0].message.content.strip().lower()
        
        # Debug: print what the LLM determined
        print(f"DEBUG - User Query: {user_query}")
        print(f"DEBUG - LLM Endpoint: {action}")

        # Await the address extraction
        address = await extract_address_from_query(user_query)
        print(f"DEBUG - Extracted Address: {address}")

        # Route based on LLM's decision
        if action == "schools":
            return await nearby_schools(AddressQuery(address=address))
        elif action == "school_catchment":
            return await school_catchment(AddressQuery(address=address))
        elif action == "transit":
            return await nearest_transit(AddressQuery(address=address))
        elif action == "parks":
            return await nearby_parks_and_centres(AddressQuery(address=address))
        elif action == "assessment":
            return await get_bc_assessment(AddressQuery(address=address))
        else:
            return {
                "message": f"Query type not supported yet. Currently available: schools, transit, parks, assessment value.",
                "query": user_query,
                "action_determined": action,
                "address_extracted": address,
                "hint": "Try asking about nearby schools, transit stations, parks, or property assessment value."
            }

    except Exception as e:
        return {"error": str(e)}


def call_nearby_schools_endpoint(query: str):
    # Extract the address from the query and call the /nearby-schools endpoint
    address = extract_address_from_query(query)
    if not address:
        return {"message": "Unable to extract address from query"}

    # Normally call your existing endpoint logic here
    response = nearby_schools(AddressQuery(address=address))
    return response

def call_nearby_transit_endpoint(query: str):
    address = extract_address_from_query(query)
    if not address:
        return {"message": "Unable to extract address from query"}
    response = nearest_transit(AddressQuery(address=address))
    return response

def call_nearby_parks_and_centres_endpoint(query: str):
    address = extract_address_from_query(query)
    if not address:
        return {"message": "Unable to extract address from query"}
    response = nearby_parks_and_centres(AddressQuery(address=address))
    return response

def call_bc_assessment(query: str):
    address = extract_address_from_query(query)
    if not address:
        return {"message": "Unable to extract address from query"}
    response = get_bc_assessment(AddressQuery(address=address))
    return response

def call_zoning_info(query: str):
    # Placeholder for zoning info endpoint
    return {"message": "Zoning info endpoint stub", "query": query}

def call_demographic_profile(query: str):
    # Placeholder for demographic profile endpoint
    return {"message": "Demographic profile endpoint stub", "query": query}

def call_homes_listing(query: str):
    # Placeholder for a home listings call, implement as needed
    return {"message": "Call to homes listing API based on parsed data"}

def regex_extract_address(query: str) -> str:
    street_pattern = re.compile(
        r'\b\d{1,5}\s+[A-Za-z0-9]+(?:\s[A-Za-z0-9]+){0,4}\b(?:\s(?:St|Street|Avenue|Ave|Rd|Road|Blvd|Boulevard|Lane|Ln|Drive|Dr|Court|Ct|Way))?',
        re.IGNORECASE
    )
    match = street_pattern.search(query)
    if match:
        return match.group(0)

    postal_pattern = re.compile(r'\b[ABCEGHJKLMNPRSTVXY]\d[ABCEGHJKLMNPRSTVWXYZ][ -]?\d[ABCEGHJKLMNPRSTVWXYZ]\d\b', re.IGNORECASE)
    match = postal_pattern.search(query)
    if match:
        return match.group(0)

    for city in BC_CITIES:
        if city.lower() in query.lower():
            return city

    intersection_pattern = re.compile(r'\b([A-Za-z0-9]+)\s*&\s*([A-Za-z0-9]+)\b')
    match = intersection_pattern.search(query)
    if match:
        return match.group(0)

    return ""

async def llm_extract_address(query: str) -> str:
    prompt = (
        "You are a real estate assistant. Extract only the property address, "
        "street, city, or postal code from the following user query. "
        "Do not add any extra text, explanation, or punctuation:\n\n"
        f"User query: {query}\nAddress:"
    )

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=30
    )

    address = response.choices[0].message.content.strip()
    return address

async def extract_address_from_query(query: str) -> str:
    address = regex_extract_address(query)
    if address:
        return address

    address = await llm_extract_address(query)
    return address

BC_CITIES = [
    "Vancouver", "West Vancouver", "North Vancouver", "Burnaby",
    "Richmond", "Surrey", "Coquitlam", "Delta", "Langley"
]