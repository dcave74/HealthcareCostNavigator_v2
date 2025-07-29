
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..schemas import ProviderSearchResponse, QuestionRequest, QuestionResponse
from ..services.database_service import DatabaseService
from ..services.openai_service import OpenAIService
from ..models import Provider, ProviderPricing

router = APIRouter()

@router.get("/providers", response_model=List[ProviderSearchResponse])
async def search_providers(
    # See below business case question for these two parameters
    # provider_id: Optional[int] = Query(None),
    # provider_name: Optional[str] = Query(None),
    drg_description: Optional[str] = Query(None),
    zip_code: Optional[str] = Query(None),
    zip_code_radius_km: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):
    """Search providers by various criteria"""

    # Validate required parameters
    #if not (provider_id or provider_name):
    #    raise HTTPException(status_code=400, detail="Either provider_id or provider_name is required")

    # See below zip code business case question
    # if not (drg_description or zip_code):
    #     raise HTTPException(status_code=400, detail="Either drg_description or zip_code is required")

    if not (drg_description and zip_code and zip_code_radius_km):
        raise HTTPException(status_code=400, detail="All of drg_description, zip_code, and radius_km are required")

    try:
        db_service = DatabaseService(db)

        # Build query based on parameters
        if drg_description:
            # Search with DRG description
            query = """
            SELECT p.provider_id, p.provider_name, pp.averaged_covered_charges
            FROM provider p
            JOIN provider_pricing pp ON p.provider_id = pp.provider_id
            WHERE pp.ms_drg_definition ILIKE :drg_description 
            and p.provider_zip_code = :zip_code
            """
            params = {
                "drg_description": f"%{drg_description}%",
                "zip_code": zip_code
            }

            # See business question about provider querying
            # if provider_id:
            #     query += " AND p.provider_id = :provider_id"
            #     params["provider_id"] = provider_id
            # elif provider_name:
            #     query += " AND p.provider_name ILIKE :provider_name"
            #     params["provider_name"] = f"%{provider_name}%"

            query += " ORDER BY pp.averaged_covered_charges, p.provider_id"

        # else:
            # Search by zip code
            # Business case question:  shouldn't the customer be able to find local providers?
            # query = """
            # SELECT p.provider_id, p.provider_name
            # FROM provider p
            # WHERE p.provider_zip_code = :zip_code
            # """
            # params = {"zip_code": zip_code}

            # if provider_id:
            #    query += " AND p.provider_id = :provider_id"
            #    params["provider_id"] = provider_id
            # elif provider_name:
            #     query += " AND p.provider_name ILIKE :provider_name"
            #     params["provider_name"] = f"%{provider_name}%"

            # query += " ORDER BY p.provider_id"

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
                answer="I couldn't understand your question. Please try rephrasing it.",
                query_used=None
            )

        # Execute the query
        results = db_service.execute_safe_query(sql_query)

        if results is None:
            return QuestionResponse(
                answer="There was an error executing the query. Please try again.",
                query_used=sql_query
            )

        if not results:
            return QuestionResponse(
                answer="No results found for your query.",
                query_used=sql_query
            )

        # Format results for response
        answer = f"Found {len(results)} result(s):\n"
        for i, result in enumerate(results[:10]):  # Limit to 10 results
            answer += f"{i+1}. {result}\n"

        if len(results) > 10:
            answer += f"... and {len(results) - 10} more results."

        return QuestionResponse(
            answer=answer,
            query_used=sql_query
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Service error: {str(e)}")