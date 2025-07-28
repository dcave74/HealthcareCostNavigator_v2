
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.services.data_import_service import DataImportService
from app.services.database_service import DatabaseService

async def seed_data():
    """Seed the database with initial data"""

    urls_to_process = [
        {
            "url": "https://data.cms.gov/sites/default/files/2024-05/7d1f4bcd-7dd9-4fd1-aa7f-91cd69e452d3/MUP_INP_RY24_P03_V10_DY22_PrvSvc.CSV",
            "filename": "MUP_INP_RY24_P03_V10_DY22_PrvSvc.CSV",
            "file_extension": "CSV",
            "file_type": "CSV",
            "subfiles": []
        }#,
        #{
        #    "url": "https://data.cms.gov/provider-data/sites/default/files/archive/Hospitals/current/hospitals_current_data.zip",
        #    "filename": "hospitals_current_data.zip",
        #    "file_extension": "zip",
        #    "file_type": "ZIP",
        #    "subfiles": ["Hospital_General_Information.csv"]  # Assuming this is in the ZIP
        #}
    ]

    db = SessionLocal()
    try:
        import_service = DataImportService()
        db_service = DatabaseService(db)

        for url_config in urls_to_process:
            print(f"Processing {url_config['url']}...")

            json_data = import_service.fetch_and_process_file(
                url=url_config["url"],
                filename=url_config["filename"],
                file_extension=url_config["file_extension"],
                file_type=url_config["file_type"],
                subfiles=url_config["subfiles"]
            )
            if json_data:
                print(f"Importing {len(json_data)} datasets...")
                success = db_service.import_json_data(json_data)
                if success:
                    print("Data imported successfully!")
                else:
                    print("Failed to import data.")
            else:
                print("No data retrieved from URL.")

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(seed_data())