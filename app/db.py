from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from .config import get_database_url
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON, Numeric
from datetime import datetime

DATABASE_URL = get_database_url()

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ============= USER & CHAT HISTORY TABLES =============
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    chat_sessions = relationship("ChatSession", back_populates="user")


class TokenBlacklist(Base):
    """Store revoked JWT tokens (for logout)"""
    __tablename__ = 'token_blacklist'
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, nullable=False, index=True)
    blacklisted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)


class ChatSession(Base):
    """Track conversation sessions for each user"""
    __tablename__ = 'chat_sessions'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_message_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    session_title = Column(String, nullable=True)  # e.g., "Searching for property in Vancouver"
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    """Store individual messages in chat"""
    __tablename__ = 'chat_messages'
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('chat_sessions.id'), nullable=False)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    query_type = Column(String, nullable=True)  # e.g., 'assessment', 'schools', 'transit'
    property_address = Column(String, nullable=True)  # Extracted address if applicable
    api_endpoint = Column(String, nullable=True)  # Which endpoint was called
    response_data = Column(JSON, nullable=True)  # Store the API response
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")


# ============= PROPERTY & ASSESSMENT (MOCK DATA) =============
class Property(Base):
    """Master property table for mock data"""
    __tablename__ = 'properties'
    
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, unique=True, nullable=False, index=True)
    city = Column(String, nullable=False)
    postal_code = Column(String, nullable=True)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    property_type = Column(String, nullable=True)  # Detached, Condo, Townhouse
    year_built = Column(Integer, nullable=True)
    lot_size_sqft = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    assessment = relationship("Assessment", back_populates="property", uselist=False)
    listing = relationship("Listing", back_populates="property", uselist=False)


class Assessment(Base):
    """BC Assessment values (MOCK DATA)"""
    __tablename__ = 'assessments'
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey('properties.id'), unique=True, nullable=False)
    assessed_value = Column(Numeric(12, 2), nullable=False)  # e.g., 2450000.00
    land_value = Column(Numeric(12, 2), nullable=False)
    improvement_value = Column(Numeric(12, 2), nullable=False)
    assessment_year = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    property = relationship("Property", back_populates="assessment")


# ============= ZONING (MOCK DATA) =============
class Zoning(Base):
    """Zoning information (MOCK DATA)"""
    __tablename__ = 'zoning'
    
    id = Column(Integer, primary_key=True, index=True)
    zone_code = Column(String, unique=True, nullable=False, index=True)  # e.g., "RS-5"
    zone_name = Column(String, nullable=False)  # e.g., "One-Family Dwelling"
    zone_type = Column(String, nullable=False)  # Residential, Commercial, Mixed
    description = Column(Text, nullable=True)
    permitted_uses = Column(Text, nullable=False)  # Comma-separated or JSON
    city = Column(String, nullable=False)  # Vancouver, Burnaby, etc.


class PropertyZoning(Base):
    """Link properties to their zoning"""
    __tablename__ = 'property_zoning'
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey('properties.id'), nullable=False)
    zone_code = Column(String, ForeignKey('zoning.zone_code'), nullable=False)


# ============= LISTINGS (MOCK DATA) =============
class Listing(Base):
    """Property listings (MOCK DATA)"""
    __tablename__ = 'listings'
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey('properties.id'), unique=True, nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    beds = Column(Integer, nullable=True)
    baths = Column(Float, nullable=True)  # 2.5 baths possible
    area_sqft = Column(Integer, nullable=True)
    property_img = Column(String, nullable=True)  # URL
    listing_url = Column(String, nullable=True)
    status = Column(String, default='active')  # active, sold, pending
    listed_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    property = relationship("Property", back_populates="listing")


# ============= DEMOGRAPHICS (MOCK DATA) =============
class Demographics(Base):
    """Neighborhood demographics (MOCK DATA)"""
    __tablename__ = 'demographics'
    
    id = Column(Integer, primary_key=True, index=True)
    neighborhood = Column(String, unique=True, nullable=False, index=True)
    city = Column(String, nullable=False)
    population = Column(Integer, nullable=True)
    median_income = Column(Numeric(12, 2), nullable=True)
    median_age = Column(Float, nullable=True)
    education_levels = Column(JSON, nullable=True)  # {"University": 60, "College": 25, ...}
    updated_at = Column(DateTime, default=datetime.utcnow)


# ============= SCHOOLS & CATCHMENTS =============
class School(Base):
    """Schools (can be cached from API or mock)"""
    __tablename__ = 'schools'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    address = Column(String, nullable=False)
    type = Column(String, nullable=False)  # Elementary, Secondary, Private
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    school_district = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    catchments = relationship("SchoolCatchment", back_populates="school")


class SchoolCatchment(Base):
    """School catchment boundaries"""
    __tablename__ = 'school_catchments'
    
    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey('schools.id'), nullable=False)
    catchment_name = Column(String, nullable=False)
    boundary = Column(JSON, nullable=True)  # GeoJSON or list of coordinates
    
    # Relationships
    school = relationship("School", back_populates="catchments")


# ============= TRANSIT (OPTIONAL CACHE) =============
class TransitStop(Base):
    """Cache transit stops (optional)"""
    __tablename__ = 'transit_stops'
    
    id = Column(Integer, primary_key=True, index=True)
    stop_id = Column(String, unique=True, nullable=False)  # From TransLink API
    name = Column(String, nullable=False, index=True)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    type = Column(String, nullable=False)  # bus_stop, skytrain_station
    routes = Column(JSON, nullable=True)  # List of route numbers
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ============= AMENITIES (OPTIONAL CACHE) =============
class Amenity(Base):
    """Cache parks and community centers (optional)"""
    __tablename__ = 'amenities'
    
    id = Column(Integer, primary_key=True, index=True)
    place_id = Column(String, unique=True, nullable=False)  # Google Place ID
    name = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False)  # park, community_center
    address = Column(String, nullable=True)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    rating = Column(Float, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
