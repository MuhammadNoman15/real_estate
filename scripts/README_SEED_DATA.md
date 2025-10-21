# Real Estate Mock Data Seeding

## Overview
This seed script populates your database with Vancouver-focused mock data for testing all 10 real estate queries.

## What's Included

### 📍 Properties (12 total)
Vancouver-focused properties across popular neighborhoods:
- **Kitsilano** (2 properties) - Townhouse & Detached
- **Yaletown** (2 properties) - Condos
- **Mount Pleasant** (1 property) - Townhouse
- **Fairview** (1 property) - Condo
- **West End** (1 property) - Condo
- **Coal Harbour** (1 property) - Luxury Condo
- **Kerrisdale** (1 property) - Detached
- **Dunbar** (1 property) - Detached
- **West Vancouver** (1 property) - Detached
- **North Vancouver** (1 property) - Condo

### 💰 BC Assessments
- Complete assessment data for all properties
- Assessment year: 2024
- Includes: Total assessed value, land value, improvement value

### 🏘️ Zoning (7 types)
- RS-5: One-Family Dwelling (West Vancouver)
- RS-1: One-Family Dwelling (Vancouver)
- RM-4: Residential Multiple Dwelling (Vancouver)
- CD-1: Comprehensive Development (Vancouver)
- R2: Two-Family Dwelling (Burnaby)
- RM1: Residential Multiple Family (Richmond)
- RF: Single Family Residential (Surrey)

### 🏠 Listings
- Active listings for all 12 properties
- Includes: Price, beds, baths, square footage, images, listing URLs

### 👥 Demographics (10 neighborhoods)
Vancouver-focused neighborhoods:
1. Kitsilano
2. Yaletown
3. Mount Pleasant
4. Fairview
5. West End
6. Coal Harbour
7. Kerrisdale
8. Dunbar-Southlands
9. West Vancouver
10. Lower Lonsdale (North Vancouver)

Each includes: Population, median income, median age, education levels

### 🎓 Schools (6 schools)
- Sentinel Secondary School (West Vancouver)
- Hollyburn Elementary (West Vancouver)
- Kitsilano Secondary School (Vancouver)
- General Gordon Elementary (Vancouver)
- Burnaby South Secondary (Burnaby)
- Richmond Secondary School (Richmond)

### 📍 School Catchments (3)
- Catchment boundaries for key schools

### 🚌 Transit Stops (8 stops)
SkyTrain Stations:
- Broadway-City Hall Station
- Waterfront Station
- Yaletown-Roundhouse Station
- Burrard Station

Bus Stops:
- Oak St & 41st Ave
- Broadway & Macdonald
- Marine Dr & 25th St
- Lonsdale Quay

### 🌳 Amenities (10 total)
**Parks:**
- Kitsilano Beach Park
- David Lam Park
- Stanley Park
- Jonathan Rogers Park
- Kerrisdale Centennial Park
- Musqueam Park
- Ambleside Park

**Community Centers:**
- Kitsilano Community Centre
- West End Community Centre
- Kerrisdale Community Centre

## Usage

### Step 1: Run Alembic Migration
```bash
# Activate virtual environment
.\real_env\Scripts\activate

# Generate migration
alembic revision --autogenerate -m "add_real_estate_tables"

# Apply migration
alembic upgrade head
```

### Step 2: Seed Mock Data
```bash
python -m scripts.seed_mock_data
```

## Test Queries

Once seeded, you can test with these addresses:

### Query 1: BC Assessment Value
```
"What is the BC Assessment value of 2150 Balsam St, Vancouver?"
```

### Query 2: Lot Size & Year Built
```
"What is the lot size and year built of 4500 Oak St, Vancouver?"
```

### Query 3: Zoning
```
"What is the zoning designation of 1288 Marinaside Crescent, Vancouver?"
```

### Query 4: Nearby Schools
```
"What schools are within 1 km of 2088 West 41st Ave, Vancouver?"
```

### Query 5: School Catchment
```
"Which school catchment does 2458 Ottawa Ave, West Vancouver belong to?"
```

### Query 6: Nearest Transit (Uses Google API - Real-time)
```
"How far is the nearest bus stop or SkyTrain station from 4500 Oak St, Vancouver?"
```

### Query 7: Demographics
```
"What is the demographic profile of the neighborhood around 2150 Balsam St, Vancouver?"
```

### Query 8: Parks & Community Centers (Uses Google API - Real-time)
```
"What parks or community centers are within walking distance of 1288 Marinaside Crescent, Vancouver?"
```

### Query 9: Average BC Assessment
```
"What is the average BC Assessment value of properties in Kitsilano?"
```

### Query 10: Transit Routes (Uses Google API - Real-time)
```
"Which transit routes connect 1250 Barclay St, Vancouver to downtown Vancouver?"
```

## Data Characteristics

### Price Ranges (Listings)
- **Condos**: $725K - $1.65M
- **Townhouses**: $1.095M - $1.395M
- **Detached Houses**: $2.495M - $3.495M

### Assessment Ranges
- **Condos**: $725K - $1.45M
- **Townhouses**: $980K - $1.25M
- **Detached Houses**: $2.15M - $2.68M

### Median Income by Area
- **Coal Harbour**: $125,000 (highest)
- **West Vancouver**: $150,000 (highest)
- **Mount Pleasant**: $72,000 (lowest in dataset)
- **West End**: $68,000 (most affordable Vancouver area)

## Notes

⚠️ **Warning**: Running the seed script will **clear all existing mock data** before seeding. Comment out `clear_all_data(db)` in the script if you want to keep existing data.

✅ **Safe to re-run**: You can run the seed script multiple times. It will clear and reseed.

🔄 **Real-time APIs**: Transit stops, parks, and amenities can also be fetched in real-time via Google Places API in your endpoints.

