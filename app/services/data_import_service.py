
import requests
import zipfile
import io
import csv
import json
from typing import List, Dict, Any, Optional

class DataImportService:

    def fetch_and_process_file(self, url: str, filename: str, file_extension: str,
                              file_type: str, subfiles: List[str] = None) -> List[str]:
        """Fetch file from URL and process it"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            if file_type.upper() == "ZIP" and subfiles:
                return self._process_zip_file(response.content, subfiles)
            elif file_extension.lower() == "csv":
                return [self._csv_to_json(response.text)]
            else:
                raise ValueError("Unsupported file type")

        except Exception as e:
            print(f"Error fetching file from {url}: {e}")
            return []

    def _process_zip_file(self, zip_content: bytes, subfiles: List[str]) -> List[str]:
        """Process ZIP file and extract specified subfiles"""
        try:
            json_results = []

            with zipfile.ZipFile(io.BytesIO(zip_content)) as zip_file:
                for subfile in subfiles:
                    if subfile in zip_file.namelist():
                        with zip_file.open(subfile) as file:
                            if subfile.lower().endswith('.csv'):
                                content = file.read().decode('utf-8')
                                json_results.append(self._csv_to_json(content))
                            else:
                                print(f"Skipping non-CSV file: {subfile}")

            return json_results

        except Exception as e:
            print(f"Error processing ZIP file: {e}")
            return []

    def _csv_to_json(self, csv_content: str) -> str:
        """Convert CSV content to JSON with field mappings"""
        try:
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            json_objects = []

            field_mappings = {
                "facility id": "provider_id",
                "rndrng_prvdr_ccn": "provider_id",
                "facility name": "provider_name",
                "rndrng_prvdr_org_name": "provider_name",
                "address": "provider_address",
                "rndrng_prvdr_st": "provider_address",
                "city/town": "provider_city",
                "rndrng_prvdr_city": "provider_city",
                "state": "provider_state",
                "rndrng_prvdr_state_abrvtn": "provider_state",
                "zip code": "provider_zip_code",
                "rndrng_prvdr_zip5": "provider_zip_code",
                "drg_cd": "ms_drg_code",
                "drg_desc": "ms_drg_definition",
                "tot_dschrgs": "total_discharges",
                "avg_submtd_cvrd_chrg": "averaged_covered_charges",
                "avg_tot_pymt_amt": "average_total_payments",
                "avg_mdcr_pymt_amt": "average_medicare_payments",
                "hospital overall rating": "provider_overall_rating",
                "patient survey star rating": "provider_star_rating"
            }

            for row in csv_reader:
                # Skip rows based on specified criteria
                if self._should_skip_row(row):
                    continue

                # Map field names
                mapped_row = {}
                for original_key, value in row.items():
                    mapped_key = field_mappings.get(original_key.lower(), original_key)
                    mapped_row[mapped_key] = value

                json_objects.append(mapped_row)

            return json.dumps(json_objects)

        except Exception as e:
            print(f"Error converting CSV to JSON: {e}")
            return "[]"

    def _should_skip_row(self, row: Dict[str, Any]) -> bool:
        """Check if row should be skipped based on criteria"""
        # Check hospital overall rating
        if row.get("Hospital overall rating") and not str(row.get("Hospital overall rating")).isdigit():
            return True

        # Check patient survey star rating
        if row.get("Patient Survey Star Rating") and not str(row.get("Patient Survey Star Rating")).isdigit():
            return True

        # Check HCAHPS answer description
        if row.get("HCAHPS Answer Description") and not str(row.get("HCAHPS Answer Description")).isdigit():
            if str(row.get("HCAHPS Answer Description")).lower() != "summary star rating":
                return True

        return False