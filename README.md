
    # Healthcare Provider Analysis API
    
    A FastAPI application for analyzing healthcare provider data using natural language queries powered by OpenAI GPT-4.1 nano.
    
    ## Features
    
    - **Natural Language Queries**: Convert plain English questions to SQL queries using OpenAI
    - **Provider Search**: Search providers by DRG descriptions, zip codes, and other criteria
    - **PostGIS Integration**: Calculate distances between zip codes
    - **Data Import**: Automated data seeding from CMS datasets
    - **Docker Support**: Complete containerization with PostgreSQL and PostGIS
    - **PostGIS**:  PostGIS is usually preinstalled on cloud PostgreSQL instances.  If it is not or you are building locally, make sure it is installed on your machine where PostgreSQL is installed.
    
    ## Quick Start
    
    1. **Clone and Setup**
       ```bash
       git clone <repository>
       cd healthcare-api
       cp .env.example .env
       # Edit .env with your OpenAI API key
       ```
    
    2. **Run with Docker Compose**
       ```bash
       docker-compose up --build
       ```
    
    3. **Seed Data** (optional)
       ```bash
       docker-compose exec app python scripts/seed_data.py
       ```
    
    4. **Access API**
       - API: http://localhost:8000
       - Swagger Docs: http://localhost:8000/docs
    
    ## API Endpoints
    
    ### GET /api/v1/providers
    Search providers by various criteria.
    
    **Parameters:**
    - `provider_id` or `provider_name` (required)
    - `drg_description` or `zip_code` (required)
    - `zip_code_radius_km` (optional)
    
    ### POST /api/v1/ask
    Submit natural language questions about the data.
    
    **Body:**

json
{
"question": "How many providers are in New York?"
}

    ## Development
    
    ### Running Tests

bash
docker-compose exec app pytest

    ### Database Access

bash

Main database

docker-compose exec db psql -U hcs_user -d hcs

Test database

docker-compose exec db_test psql -U hcs_user_test -d hcs_test

    ### Manual Data Import

python
from app.services.data_import_service import DataImportService
service = DataImportService()

Use service methods to import custom data
    ## Security Notes
    
    - **FOR LOCAL DEVELOPMENT ONLY**: The included passwords are for development only
    - Change all passwords for production use
    - Ensure OpenAI API key is kept secure
    - SQL injection protection is implemented via parameterized queries
    
    ## Architecture
    
    - **FastAPI**: Modern Python web framework
    - **SQLAlchemy 2.0**: Database ORM
    - **PostgreSQL 16**: Primary database
    - **PostGIS 3.5**: Geospatial extensions
    - **OpenAI GPT-4.1 nano**: Natural language processing
    - **Docker**: Containerization
    - **Pytest**: Testing framework
    
    ## Data Sources
    
    The application can automatically import data from:
    - CMS Provider Pricing Data
    - CMS Hospital Information Data
    
    Both datasets are processed and normalized during import.

This completes the comprehensive FastAPI project structure. The project includes:

1. Complete Docker setup with PostgreSQL 16 and PostGIS 3.5
2. FastAPI application with proper structure and endpoints
3. SQLAlchemy models with relationships and constraints
4. OpenAI integration for natural language to SQL conversion
5. Data import services for processing CMS datasets
6. Comprehensive tests with pytest
7. Production-ready configuration with proper error handling

Key features implemented:

- ✅ Provider search API with DRG and zip code filtering
- ✅ Natural language question processing via OpenAI
- ✅ PostGIS distance calculations
- ✅ Automated data seeding from CMS URLs
- ✅ SQL injection protection via parameterized queries
- ✅ Comprehensive test suite
- ✅ Docker containerization

To get started, you'll need to:

1. Set up your OpenAI API key in the `.env` file
2. Run `docker-compose up --build`
3. Optionally run the data seeding script to populate with real CMS data