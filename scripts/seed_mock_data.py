"""
Seed script to populate mock data for testing all real estate queries.

Usage:
    python -m scripts.seed_mock_data

This will populate:
- Properties
- Assessments
- Zoning
- Property-Zoning links
- Listings
- Demographics
- Schools
- School Catchments
- Transit Stops
- Amenities
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db import (
    engine, Base, SessionLocal,
    Property, Assessment, Zoning, PropertyZoning,
    Listing, Demographics, School, SchoolCatchment,
    TransitStop, Amenity
)


def clear_all_data(db):
    """Clear all existing data (CAUTION: This deletes everything!)"""
    print("⚠️  Clearing all existing mock data...")
    db.query(PropertyZoning).delete()
    db.query(SchoolCatchment).delete()
    db.query(Assessment).delete()
    db.query(Listing).delete()
    db.query(Property).delete()
    db.query(Zoning).delete()
    db.query(Demographics).delete()
    db.query(School).delete()
    db.query(TransitStop).delete()
    db.query(Amenity).delete()
    db.commit()
    print("✅ Cleared all mock data")


def seed_properties(db):
    """Create sample properties across Vancouver neighborhoods"""
    print("\n📍 Seeding Properties...")
    
    properties = [
        # Vancouver - Kitsilano
        Property(
            address="2150 Balsam St, Vancouver, BC V6K 3Z5",
            city="Vancouver",
            postal_code="V6K 3Z5",
            lat=49.2685,
            lng=-123.1552,
            property_type="Townhouse",
            year_built=2010,
            lot_size_sqft=2500,
        ),
        Property(
            address="3456 West 4th Ave, Vancouver, BC V6R 1P2",
            city="Vancouver",
            postal_code="V6R 1P2",
            lat=49.2683,
            lng=-123.1615,
            property_type="Detached",
            year_built=1965,
            lot_size_sqft=5200,
        ),
        # Vancouver - Yaletown
        Property(
            address="1288 Marinaside Crescent, Vancouver, BC V6Z 2W5",
            city="Vancouver",
            postal_code="V6Z 2W5",
            lat=49.2750,
            lng=-123.1207,
            property_type="Condo",
            year_built=2015,
            lot_size_sqft=950,
        ),
        Property(
            address="1255 Seymour St, Vancouver, BC V6B 3N8",
            city="Vancouver",
            postal_code="V6B 3N8",
            lat=49.2748,
            lng=-123.1194,
            property_type="Condo",
            year_built=2019,
            lot_size_sqft=1050,
        ),
        # Vancouver - Mount Pleasant
        Property(
            address="456 East Broadway, Vancouver, BC V5T 1X5",
            city="Vancouver",
            postal_code="V5T 1X5",
            lat=49.2633,
            lng=-123.1018,
            property_type="Townhouse",
            year_built=2016,
            lot_size_sqft=1800,
        ),
        # Vancouver - Fairview/Oak St
        Property(
            address="4500 Oak St, Vancouver, BC V6H 3N1",
            city="Vancouver",
            postal_code="V6H 3N1",
            lat=49.2440,
            lng=-123.1337,
            property_type="Condo",
            year_built=2018,
            lot_size_sqft=1100,
        ),
        # Vancouver - West End
        Property(
            address="1250 Barclay St, Vancouver, BC V6E 1H3",
            city="Vancouver",
            postal_code="V6E 1H3",
            lat=49.2878,
            lng=-123.1352,
            property_type="Condo",
            year_built=2012,
            lot_size_sqft=850,
        ),
        # Vancouver - Coal Harbour
        Property(
            address="588 Broughton St, Vancouver, BC V6G 3K3",
            city="Vancouver",
            postal_code="V6G 3K3",
            lat=49.2897,
            lng=-123.1258,
            property_type="Condo",
            year_built=2017,
            lot_size_sqft=1250,
        ),
        # Vancouver - Kerrisdale
        Property(
            address="2088 West 41st Ave, Vancouver, BC V6M 1Z4",
            city="Vancouver",
            postal_code="V6M 1Z4",
            lat=49.2341,
            lng=-123.1582,
            property_type="Detached",
            year_built=1988,
            lot_size_sqft=6500,
        ),
        # Vancouver - Dunbar
        Property(
            address="4321 Dunbar St, Vancouver, BC V6S 2G3",
            city="Vancouver",
            postal_code="V6S 2G3",
            lat=49.2485,
            lng=-123.1851,
            property_type="Detached",
            year_built=1975,
            lot_size_sqft=7200,
        ),
        # West Vancouver
        Property(
            address="2458 Ottawa Ave, West Vancouver, BC V7V 2T1",
            city="West Vancouver",
            postal_code="V7V 2T1",
            lat=49.3400826,
            lng=-123.1808462,
            property_type="Detached",
            year_built=1985,
            lot_size_sqft=8500,
        ),
        # North Vancouver
        Property(
            address="1455 Lonsdale Ave, North Vancouver, BC V7M 2J2",
            city="North Vancouver",
            postal_code="V7M 2J2",
            lat=49.3156,
            lng=-123.0779,
            property_type="Condo",
            year_built=2020,
            lot_size_sqft=920,
        ),
    ]
    
    db.add_all(properties)
    db.commit()
    print(f"✅ Added {len(properties)} properties")
    return properties


def seed_assessments(db, properties):
    """Create BC Assessment data for properties"""
    print("\n💰 Seeding Assessments...")
    
    assessment_data = [
        (1250000, 850000, 400000),    # Kitsilano Townhouse
        (2150000, 1850000, 300000),   # Kitsilano Detached
        (895000, 200000, 695000),     # Yaletown Condo 1
        (1050000, 230000, 820000),    # Yaletown Condo 2
        (980000, 320000, 660000),     # Mount Pleasant Townhouse
        (725000, 250000, 475000),     # Fairview/Oak St Condo
        (815000, 180000, 635000),     # West End Condo
        (1450000, 290000, 1160000),   # Coal Harbour Condo
        (2680000, 2100000, 580000),   # Kerrisdale Detached
        (2350000, 1950000, 400000),   # Dunbar Detached
        (2450000, 1700000, 750000),   # West Vancouver
        (920000, 220000, 700000),     # North Vancouver Condo
    ]
    
    assessments = []
    for i, prop in enumerate(properties):
        assessed, land, improvement = assessment_data[i]
        assessments.append(Assessment(
            property_id=prop.id,
            assessed_value=assessed,
            land_value=land,
            improvement_value=improvement,
            assessment_year=2024
        ))
    
    db.add_all(assessments)
    db.commit()
    print(f"✅ Added {len(assessments)} assessments")


def seed_zoning(db):
    """Create zoning designations"""
    print("\n🏘️  Seeding Zoning...")
    
    zoning_data = [
        {
            "zone_code": "RS-5",
            "zone_name": "One-Family Dwelling",
            "zone_type": "Residential",
            "description": "Single-family residential with secondary suite allowed",
            "permitted_uses": "Single-family dwelling, home occupation, secondary suite, laneway house",
            "city": "West Vancouver"
        },
        {
            "zone_code": "RS-1",
            "zone_name": "One-Family Dwelling",
            "zone_type": "Residential",
            "description": "Traditional single-family residential",
            "permitted_uses": "Single-family dwelling, home occupation",
            "city": "Vancouver"
        },
        {
            "zone_code": "RM-4",
            "zone_name": "Residential Multiple Dwelling",
            "zone_type": "Residential",
            "description": "Low-rise multiple dwelling units",
            "permitted_uses": "Townhouses, rowhouses, low-rise apartments (max 4 storeys)",
            "city": "Vancouver"
        },
        {
            "zone_code": "CD-1",
            "zone_name": "Comprehensive Development",
            "zone_type": "Mixed",
            "description": "High-density mixed residential and commercial",
            "permitted_uses": "High-rise residential, retail, office, community facilities",
            "city": "Vancouver"
        },
        {
            "zone_code": "R2",
            "zone_name": "Two-Family Dwelling",
            "zone_type": "Residential",
            "description": "Duplex and two-family residential",
            "permitted_uses": "Duplex, two-family dwelling, secondary suite",
            "city": "Burnaby"
        },
        {
            "zone_code": "RM1",
            "zone_name": "Residential Multiple Family",
            "zone_type": "Residential",
            "description": "Medium-density residential",
            "permitted_uses": "Townhouses, apartments, condominiums",
            "city": "Richmond"
        },
        {
            "zone_code": "RF",
            "zone_name": "Single Family Residential",
            "zone_type": "Residential",
            "description": "Low-density single family",
            "permitted_uses": "Single-family dwelling, home business",
            "city": "Surrey"
        },
    ]
    
    zones = [Zoning(**z) for z in zoning_data]
    db.add_all(zones)
    db.commit()
    print(f"✅ Added {len(zones)} zoning designations")
    return zones


def seed_property_zoning(db, properties):
    """Link properties to their zoning"""
    print("\n🔗 Linking Properties to Zoning...")
    
    # Map properties to zoning codes
    property_zone_map = [
        (1, "RM-4"),   # Kitsilano Townhouse
        (2, "RS-1"),   # Kitsilano Detached
        (3, "CD-1"),   # Yaletown Condo 1
        (4, "CD-1"),   # Yaletown Condo 2
        (5, "RM-4"),   # Mount Pleasant Townhouse
        (6, "CD-1"),   # Fairview/Oak St Condo
        (7, "CD-1"),   # West End Condo
        (8, "CD-1"),   # Coal Harbour Condo
        (9, "RS-1"),   # Kerrisdale Detached
        (10, "RS-1"),  # Dunbar Detached
        (11, "RS-5"),  # West Vancouver
        (12, "CD-1"),  # North Vancouver Condo
    ]
    
    pz_links = [
        PropertyZoning(property_id=pid, zone_code=zcode)
        for pid, zcode in property_zone_map
    ]
    
    db.add_all(pz_links)
    db.commit()
    print(f"✅ Linked {len(pz_links)} properties to zones")


def seed_listings(db, properties):
    """Create property listings"""
    print("\n🏠 Seeding Listings...")
    
    listing_data = [
        (1395000, 3, 2.5, 1850, "https://images.unsplash.com/photo-1564013799919-ab600027ffc6"),  # Kits Townhouse
        (2495000, 4, 3, 3200, "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9"),  # Kits Detached
        (995000, 2, 2, 950, "https://images.unsplash.com/photo-1567496898669-ee935f5f647a"),   # Yaletown 1
        (1185000, 2, 2, 1050, "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00"),    # Yaletown 2
        (1095000, 2, 2, 1800, "https://images.unsplash.com/photo-1580587771525-78b9dba3b914"), # Mount Pleasant
        (725000, 2, 2, 1100, "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267"),  # Fairview
        (895000, 1, 1, 850, "https://images.unsplash.com/photo-1502672260066-6bc2557c89d5"),   # West End
        (1650000, 2, 2, 1250, "https://images.unsplash.com/photo-1512917774080-9991f1c4c750"), # Coal Harbour
        (2895000, 5, 4, 3800, "https://images.unsplash.com/photo-1613977257363-707ba9348227"),  # Kerrisdale
        (2650000, 4, 3.5, 3600, "https://images.unsplash.com/photo-1570129477492-45c003edd2be"), # Dunbar
        (3495000, 5, 4.5, 4200, "https://images.unsplash.com/photo-1583608205776-bfd35f0d9f83"), # West Van
        (1025000, 2, 2, 920, "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00"),    # North Van
    ]
    
    listings = []
    for i, prop in enumerate(properties):
        price, beds, baths, sqft, img = listing_data[i]
        listings.append(Listing(
            property_id=prop.id,
            price=price,
            beds=beds,
            baths=baths,
            area_sqft=sqft,
            property_img=img,
            listing_url=f"https://realtor.ca/listing/{prop.id}",
            status="active",
            listed_date=datetime.utcnow() - timedelta(days=i*5)
        ))
    
    db.add_all(listings)
    db.commit()
    print(f"✅ Added {len(listings)} listings")


def seed_demographics(db):
    """Create neighborhood demographics"""
    print("\n👥 Seeding Demographics...")
    
    demographics = [
        Demographics(
            neighborhood="Kitsilano",
            city="Vancouver",
            population=40000,
            median_income=85000,
            median_age=38.5,
            education_levels={"University": 70, "College": 18, "High School": 10, "Trade": 2}
        ),
        Demographics(
            neighborhood="Yaletown",
            city="Vancouver",
            population=15000,
            median_income=95000,
            median_age=35.2,
            education_levels={"University": 75, "College": 15, "High School": 8, "Trade": 2}
        ),
        Demographics(
            neighborhood="Mount Pleasant",
            city="Vancouver",
            population=28000,
            median_income=72000,
            median_age=33.8,
            education_levels={"University": 68, "College": 20, "High School": 10, "Trade": 2}
        ),
        Demographics(
            neighborhood="Fairview",
            city="Vancouver",
            population=35000,
            median_income=78000,
            median_age=36.4,
            education_levels={"University": 72, "College": 18, "High School": 8, "Trade": 2}
        ),
        Demographics(
            neighborhood="West End",
            city="Vancouver",
            population=44000,
            median_income=68000,
            median_age=40.2,
            education_levels={"University": 65, "College": 22, "High School": 11, "Trade": 2}
        ),
        Demographics(
            neighborhood="Coal Harbour",
            city="Vancouver",
            population=12000,
            median_income=125000,
            median_age=42.5,
            education_levels={"University": 80, "College": 12, "High School": 6, "Trade": 2}
        ),
        Demographics(
            neighborhood="Kerrisdale",
            city="Vancouver",
            population=15000,
            median_income=110000,
            median_age=48.7,
            education_levels={"University": 75, "College": 15, "High School": 8, "Trade": 2}
        ),
        Demographics(
            neighborhood="Dunbar-Southlands",
            city="Vancouver",
            population=22000,
            median_income=105000,
            median_age=45.3,
            education_levels={"University": 73, "College": 17, "High School": 8, "Trade": 2}
        ),
        Demographics(
            neighborhood="West Vancouver",
            city="West Vancouver",
            population=42473,
            median_income=150000,
            median_age=52.3,
            education_levels={"University": 65, "College": 20, "High School": 12, "Trade": 3}
        ),
        Demographics(
            neighborhood="Lower Lonsdale",
            city="North Vancouver",
            population=38000,
            median_income=82000,
            median_age=37.6,
            education_levels={"University": 69, "College": 19, "High School": 10, "Trade": 2}
        ),
    ]
    
    db.add_all(demographics)
    db.commit()
    print(f"✅ Added {len(demographics)} demographic profiles")


def seed_schools(db):
    """Create school data"""
    print("\n🎓 Seeding Schools...")
    
    schools = [
        School(
            name="Sentinel Secondary School",
            address="1250 Chartwell Dr, West Vancouver, BC",
            type="Secondary",
            lat=49.3343,
            lng=-123.1542,
            school_district="SD45 West Vancouver"
        ),
        School(
            name="Hollyburn Elementary",
            address="235 Keith Rd W, West Vancouver, BC",
            type="Elementary",
            lat=49.3289,
            lng=-123.1668,
            school_district="SD45 West Vancouver"
        ),
        School(
            name="Kitsilano Secondary School",
            address="2550 W 10th Ave, Vancouver, BC",
            type="Secondary",
            lat=49.2629,
            lng=-123.1583,
            school_district="SD39 Vancouver"
        ),
        School(
            name="General Gordon Elementary",
            address="2268 Bayswater St, Vancouver, BC",
            type="Elementary",
            lat=49.2661,
            lng=-123.1577,
            school_district="SD39 Vancouver"
        ),
        School(
            name="Burnaby South Secondary",
            address="5455 Rumble St, Burnaby, BC",
            type="Secondary",
            lat=49.2205,
            lng=-123.0066,
            school_district="SD41 Burnaby"
        ),
        School(
            name="Richmond Secondary School",
            address="7171 Minoru Blvd, Richmond, BC",
            type="Secondary",
            lat=49.1726,
            lng=-123.1371,
            school_district="SD38 Richmond"
        ),
    ]
    
    db.add_all(schools)
    db.commit()
    print(f"✅ Added {len(schools)} schools")
    return schools


def seed_school_catchments(db, schools):
    """Create school catchment boundaries"""
    print("\n📍 Seeding School Catchments...")
    
    catchments = [
        SchoolCatchment(
            school_id=schools[0].id,
            catchment_name="Sentinel Secondary Catchment",
            boundary={"type": "Polygon", "coordinates": [[[-123.20, 49.35], [-123.14, 49.35], [-123.14, 49.32], [-123.20, 49.32]]]}
        ),
        SchoolCatchment(
            school_id=schools[1].id,
            catchment_name="Hollyburn Elementary Catchment",
            boundary={"type": "Polygon", "coordinates": [[[-123.18, 49.34], [-123.15, 49.34], [-123.15, 49.32], [-123.18, 49.32]]]}
        ),
        SchoolCatchment(
            school_id=schools[2].id,
            catchment_name="Kitsilano Secondary Catchment",
            boundary={"type": "Polygon", "coordinates": [[[-123.17, 49.28], [-123.14, 49.28], [-123.14, 49.25], [-123.17, 49.25]]]}
        ),
    ]
    
    db.add_all(catchments)
    db.commit()
    print(f"✅ Added {len(catchments)} school catchments")


def seed_transit_stops(db):
    """Create transit stop data"""
    print("\n🚌 Seeding Transit Stops...")
    
    transit_stops = [
        TransitStop(
            stop_id="50001",
            name="Broadway-City Hall Station",
            lat=49.2632,
            lng=-123.1157,
            type="skytrain_station",
            routes=["Canada Line", "99 B-Line"]
        ),
        TransitStop(
            stop_id="50002",
            name="Waterfront Station",
            lat=49.2857,
            lng=-123.1116,
            type="skytrain_station",
            routes=["Expo Line", "Canada Line", "West Coast Express", "SeaBus"]
        ),
        TransitStop(
            stop_id="50003",
            name="Yaletown-Roundhouse Station",
            lat=49.2747,
            lng=-123.1218,
            type="skytrain_station",
            routes=["Canada Line"]
        ),
        TransitStop(
            stop_id="50004",
            name="Burrard Station",
            lat=49.2859,
            lng=-123.1201,
            type="skytrain_station",
            routes=["Expo Line"]
        ),
        TransitStop(
            stop_id="50005",
            name="Oak St & 41st Ave",
            lat=49.2345,
            lng=-123.1303,
            type="bus_stop",
            routes=["17", "41"]
        ),
        TransitStop(
            stop_id="50006",
            name="Broadway & Macdonald",
            lat=49.2639,
            lng=-123.1564,
            type="bus_stop",
            routes=["9", "99 B-Line"]
        ),
        TransitStop(
            stop_id="50007",
            name="Marine Dr & 25th St",
            lat=49.3395,
            lng=-123.1815,
            type="bus_stop",
            routes=["250", "257"]
        ),
        TransitStop(
            stop_id="50008",
            name="Lonsdale Quay",
            lat=49.3103,
            lng=-123.0810,
            type="bus_stop",
            routes=["SeaBus", "229", "236", "239"]
        ),
    ]
    
    db.add_all(transit_stops)
    db.commit()
    print(f"✅ Added {len(transit_stops)} transit stops")


def seed_amenities(db):
    """Create amenity data (parks & community centers)"""
    print("\n🌳 Seeding Amenities...")
    
    amenities = [
        Amenity(
            place_id="ChIJ1_Park_Kits",
            name="Kitsilano Beach Park",
            type="park",
            address="1499 Arbutus St, Vancouver, BC",
            lat=49.2748,
            lng=-123.1562,
            rating=4.8
        ),
        Amenity(
            place_id="ChIJ2_Community_Kits",
            name="Kitsilano Community Centre",
            type="community_center",
            address="2690 Larch St, Vancouver, BC",
            lat=49.2639,
            lng=-123.1568,
            rating=4.6
        ),
        Amenity(
            place_id="ChIJ3_Park_Yaletown",
            name="David Lam Park",
            type="park",
            address="1300 Pacific Blvd, Vancouver, BC",
            lat=49.2740,
            lng=-123.1245,
            rating=4.7
        ),
        Amenity(
            place_id="ChIJ4_Park_Stanley",
            name="Stanley Park",
            type="park",
            address="Vancouver, BC V6G 1Z4",
            lat=49.3042,
            lng=-123.1443,
            rating=4.9
        ),
        Amenity(
            place_id="ChIJ5_Community_WestEnd",
            name="West End Community Centre",
            type="community_center",
            address="870 Denman St, Vancouver, BC",
            lat=49.2874,
            lng=-123.1407,
            rating=4.5
        ),
        Amenity(
            place_id="ChIJ6_Park_MountPleasant",
            name="Jonathan Rogers Park",
            type="park",
            address="110 W 7th Ave, Vancouver, BC",
            lat=49.2631,
            lng=-123.1071,
            rating=4.6
        ),
        Amenity(
            place_id="ChIJ7_Park_Kerrisdale",
            name="Kerrisdale Centennial Park",
            type="park",
            address="5760 East Boulevard, Vancouver, BC",
            lat=49.2345,
            lng=-123.1504,
            rating=4.5
        ),
        Amenity(
            place_id="ChIJ8_Community_Kerrisdale",
            name="Kerrisdale Community Centre",
            type="community_center",
            address="5851 West Boulevard, Vancouver, BC",
            lat=49.2328,
            lng=-123.1582,
            rating=4.4
        ),
        Amenity(
            place_id="ChIJ9_Park_Dunbar",
            name="Musqueam Park",
            type="park",
            address="4546 West 8th Ave, Vancouver, BC",
            lat=49.2645,
            lng=-123.2095,
            rating=4.3
        ),
        Amenity(
            place_id="ChIJ10_Park_West_Van",
            name="Ambleside Park",
            type="park",
            address="1200 Argyle Ave, West Vancouver, BC",
            lat=49.3236,
            lng=-123.1523,
            rating=4.7
        ),
    ]
    
    db.add_all(amenities)
    db.commit()
    print(f"✅ Added {len(amenities)} amenities")


def main():
    """Main seeding function"""
    print("=" * 60)
    print("🌱 STARTING MOCK DATA SEEDING")
    print("=" * 60)
    
    # Create tables if they don't exist
    print("\n📋 Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables ready")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Clear existing data (optional - comment out if you want to keep existing data)
        clear_all_data(db)
        
        # Seed all data
        properties = seed_properties(db)
        seed_assessments(db, properties)
        zones = seed_zoning(db)
        seed_property_zoning(db, properties)
        seed_listings(db, properties)
        seed_demographics(db)
        schools = seed_schools(db)
        seed_school_catchments(db, schools)
        seed_transit_stops(db)
        seed_amenities(db)
        
        print("\n" + "=" * 60)
        print("✅ MOCK DATA SEEDING COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\n📊 Summary:")
        print(f"   • {len(properties)} Properties (Vancouver-focused)")
        print(f"   • {len(properties)} Assessments")
        print(f"   • {len(zones)} Zoning Designations")
        print(f"   • {len(properties)} Property-Zoning Links")
        print(f"   • {len(properties)} Listings")
        print(f"   • 10 Demographic Profiles (Vancouver neighborhoods)")
        print(f"   • {len(schools)} Schools")
        print(f"   • 3 School Catchments")
        print(f"   • 8 Transit Stops (SkyTrain & Bus)")
        print(f"   • 10 Amenities (Parks & Community Centers)")
        print("\n🎉 Your Vancouver-focused database is ready for testing!")
        print("\n💡 Test addresses to try:")
        print("   - 2150 Balsam St, Vancouver (Kitsilano)")
        print("   - 1288 Marinaside Crescent, Vancouver (Yaletown)")
        print("   - 4500 Oak St, Vancouver (Fairview)")
        print("   - 2088 West 41st Ave, Vancouver (Kerrisdale)")
        print("   - 2458 Ottawa Ave, West Vancouver")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

