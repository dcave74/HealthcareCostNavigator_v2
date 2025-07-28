import math

from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Optional
import json
from ..models import Provider, ProviderPricing, ProviderRating

class DatabaseService:
    def __init__(self, db: Session):
        self.db = db

    def execute_safe_query(self, query: str, params: Dict[str, Any] = None) -> Optional[List[Dict]]:
        """Execute a parameterized query safely"""
        try:
            if params is None:
                params = {}

            result = self.db.execute(text(query), params)

            if result.returns_rows:
                columns = result.keys()
                rows = result.fetchall()
                return [dict(zip(columns, row)) for row in rows]
            else:
                return []

        except Exception as e:
            print(f"Database query error: {e}")
            return None

    def calculate_zip_distance(self, zip1: str, zip2: str) -> Optional[float]:
        """Calculate distance between two zip codes using PostGIS"""
        try:
            query = "SELECT calculate_zip_distance(:zip1, :zip2) as distance"
            result = self.execute_safe_query(query, {"zip1": zip1, "zip2": zip2})

            if result and len(result) > 0:
                return result[0].get('distance')
            return None

        except Exception as e:
            print(f"Distance calculation error: {e}")
            return None

    def import_json_data(self, json_strings: List[str]) -> bool:
        """Import data from JSON strings into database tables"""
        try:
            for json_str in json_strings:
                try:
                    data = json.loads(json_str)

                    for json_date in data:
                        if 'provider_id' not in json_date:
                            print(f"Skipping record without provider_id: {json_str[:100]}...")
                            continue

                        self._import_provider_data(json_date)
                        self._import_pricing_data(json_date)
                        self._import_rating_data(json_date)
                        self.db.commit()

                except json.JSONDecodeError as e:
                    print(f"Invalid JSON: {e}")
                    continue

            self.db.commit()
            return True

        except Exception as e:
            print(f"Data import error: {e}")
            self.db.rollback()
            return False

    def _import_provider_data(self, data: Dict[str, Any]):
        """Import provider data"""
        provider_fields = {
            'provider_id', 'provider_name', 'provider_city',
            'provider_state', 'provider_zip_code', 'provider_status'
        }

        provider_data = {k: v for k, v in data.items() if k in provider_fields}

        if len(provider_data) > 1:  # More than just provider_id
            existing = self.db.query(Provider).filter(
                Provider.provider_id == provider_data['provider_id']
            ).first()

            if not existing:
                provider = Provider(**provider_data)
                self.db.add(provider)

    def _import_pricing_data(self, data: Dict[str, Any]):
        """Import pricing data"""
        pricing_fields = {
            'provider_id', 'ms_drg_definition', 'total_discharges',
            'averaged_covered_charges', 'average_total_payments',
            'average_medicare_payments', 'provider_pricing_year'
        }

        pricing_data = {k: v for k, v in data.items() if k in pricing_fields}

        if 'ms_drg_definition' in pricing_data:
            if 'averaged_covered_charges' in pricing_data:
                averaged_covered_charges = math.trunc(float(pricing_data['averaged_covered_charges']))
                pricing_data['averaged_covered_charges'] = averaged_covered_charges
            if 'average_total_payments' in pricing_data:
                average_total_payments = math.trunc(float(pricing_data['average_total_payments']))
                pricing_data['average_total_payments'] = average_total_payments
            if 'average_medicare_payments' in pricing_data:
                average_medicare_payments = math.trunc(float(pricing_data['average_medicare_payments']))
                pricing_data['average_medicare_payments'] = average_medicare_payments
            pricing = ProviderPricing(**pricing_data)
            self.db.add(pricing)

    def _import_rating_data(self, data: Dict[str, Any]):
        """Import rating data"""
        rating_fields = {
            'provider_id', 'provider_overall_rating',
            'provider_star_rating', 'provider_rating_year'
        }

        rating_data = {k: v for k, v in data.items() if k in rating_fields}

        if len(rating_data) > 1:  # More than just provider_id
            rating = ProviderRating(**rating_data)
            self.db.add(rating)