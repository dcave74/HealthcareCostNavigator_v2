
import openai
from typing import Optional
from ..config import settings

class OpenAIService:
    def __init__(self):
        openai.api_key = settings.openai_api_key

    async def convert_to_sql(self, natural_language: str, table_schemas: dict) -> Optional[str]:
        """Convert natural language to PostgreSQL query using OpenAI GPT-4.1 nano"""
        try:
            schema_text = self._format_schemas(table_schemas)

            prompt = f"""
            Convert the following natural language question to a PostgreSQL query.

            Database Schema:
            {schema_text}

            Guidelines:
            - Use ILIKE for ms_drg_definition matching
            - Use PostGIS for provider_zip_code distance calculations
            - Only return the SQL query, no explanations

            Question: {natural_language}
            """

            response = await openai.ChatCompletion.acreate(
                model="gpt-4.1-nano",
                messages=[
                    {"role": "system", "content": "You are a SQL expert. Convert natural language to PostgreSQL queries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.1
            )

            sql_query = response.choices[0].message.content.strip()

            if self._validate_sql_response(sql_query):
                return sql_query
            else:
                return None

        except Exception as e:
            print(f"OpenAI API error: {e}")
            return None

    def _format_schemas(self, schemas: dict) -> str:
        """Format table schemas for OpenAI prompt"""
        schema_text = ""
        for table_name, columns in schemas.items():
            schema_text += f"\nTable: {table_name}\n"
            for column in columns:
                schema_text += f"  - {column}\n"
        return schema_text

    def _validate_sql_response(self, sql_query: str) -> bool:
        """Validate that the response is a valid SQL query"""
        if not sql_query:
            return False

        # Basic validation - starts with SELECT, INSERT, UPDATE, or DELETE
        sql_query = sql_query.upper().strip()
        valid_starts = ['SELECT', 'INSERT', 'UPDATE', 'DELETE']

        return any(sql_query.startswith(start) for start in valid_starts)