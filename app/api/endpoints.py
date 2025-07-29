
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..schemas import ProviderSearchResponse, QuestionRequest, QuestionResponse
from ..services.database_service import DatabaseService
from ..services.openai_service import OpenAIService

router = APIRouter()

@router.get("/providers", response_model=List[ProviderSearchResponse])
async def search_providers(
    drg_description: Optional[str] = Query(None),
    zip_code: Optional[str] = Query(None),
    zip_code_radius_km: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):
    """Search providers by various criteria"""
    if not (drg_description and zip_code and zip_code_radius_km):
        raise HTTPException(status_code=400, detail="All of drg_description, zip_code, and radius_km are required")

    try:
        db_service = DatabaseService(db)

        # Build query based on parameters
        # Zipcode radius searching is mocked.  Need geocode table or call to GoogleMaps for real
        query = """
        SELECT p.provider_id, p.provider_name, pp.averaged_covered_charges
        FROM provider p
        JOIN provider_pricing pp ON p.provider_id = pp.provider_id
        WHERE pp.ms_drg_definition ILIKE :drg_description
        and calculate_zip_distance(p.provider_zip_code, :zip_code) < :zip_code_radius_km
        """
        params = {
            "drg_description": f"%{drg_description}%",
            "zip_code": zip_code,
            "zip_code_radius_km": zip_code_radius_km
        }

        query += " ORDER BY pp.averaged_covered_charges, p.provider_id"

        results = db_service.execute_safe_query(query, params)

        if not results:
            return []

        # Convert results to response model
        response = []
        for result in results:
            response.append(ProviderSearchResponse(
                provider_id=result["provider_id"],
                provider_name=result["provider_name"],
                average_covered_charges=result.get("averaged_covered_charges")
            ))

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/ask", response_model=QuestionResponse)
async def ask_question(
    request: QuestionRequest,
    db: Session = Depends(get_db)
):
    """Convert natural language question to SQL and execute"""

    try:
        # Initialize services
        openai_service = OpenAIService()
        db_service = DatabaseService(db)

        # Define table schemas for OpenAI
        table_schemas = {
            "provider": [
                "provider_id INT PRIMARY KEY",
                "provider_name VARCHAR(255)",
                "provider_city VARCHAR(255)",
                "provider_state VARCHAR(2)",
                "provider_zip_code VARCHAR(20)",
                "provider_status VARCHAR(20)"
            ],
            "provider_pricing": [
                "provider_id INT",
                "ms_drg_definition VARCHAR(1000)",
                "total_discharges INT",
                "averaged_covered_charges INT",
                "average_total_payments INT",
                "average_medicare_payments INT",
                "provider_pricing_year INT"
            ],
            "provider_rating": [
                "provider_id INT",
                "provider_overall_rating INT",
                "provider_star_rating INT",
                "provider_rating_year INT"
            ]
        }

        # Convert natural language to SQL
        sql_query = await openai_service.convert_to_sql(request.question, table_schemas)

        if not sql_query:
            return QuestionResponse(
                answer=" I can only help with hospital pricing and quality information. Please ask about medical procedures, costs, or hospital ratings.",
            )

        # Execute the query
        results = db_service.execute_safe_query(sql_query)

        if results is None:
            return QuestionResponse(
                answer="I had a problem finding an answer for you. Please try again.",
            )

        if not results:
            return QuestionResponse(
                answer="I didn't find any hospital pricing or quality information for your question.  Please ask another question"
            )

        # Format results for response
        # answer = f"Found {len(results)} result(s):\n"
        answer = ""
        for i, result in enumerate(results[:10]):  # Limit to 10 results
            answer += f"{i+1}. {result}\n"

        if len(results) > 10:
            answer += f"... and {len(results) - 10} more results."

        return QuestionResponse(
           answer=answer
        )
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Service error: {str(e)}")