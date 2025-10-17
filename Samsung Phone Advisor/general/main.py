from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import uvicorn
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from agent_orchestrator import AgentOrchestrator
from rag_module import RAGModule
from scraper import GSMArenaScraper
from data_processor import DataProcessor
from database import DatabaseManager
from config import API_CONFIG, DB_CONFIG, OLLAMA_CONFIG

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Samsung Phone Assistant API",
    description="Multi-agent system for Samsung phone queries and recommendations",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    status: str
    question: str = None
    answer: str = None
    query_type: str = None
    phones_involved: List[str] = None
    focus_area: str = None
    confidence_score: float = None
    processing_time_ms: float = None

class ErrorResponse(BaseModel):
    status: str
    error_code: str
    error_message: str
    suggestion: str = None
    available_phones: List[str] = None

class PhonesListResponse(BaseModel):
    status: str
    total_phones: int
    returned_count: int
    phones: List[Dict[str, Any]]

class PhoneDetailResponse(BaseModel):
    status: str
    phone: Dict[str, Any]

class HealthResponse(BaseModel):
    status: str
    database_connection: str
    ollama_connection: str
    timestamp: str
    total_phones_in_db: int

class RefreshDataRequest(BaseModel):
    admin_key: Optional[str] = None

class RefreshDataResponse(BaseModel):
    status: str
    message: str
    estimated_duration_seconds: int
    estimated_completion_time: str

# Initialize components
orchestrator = AgentOrchestrator()
rag = RAGModule()
db_manager = DatabaseManager()

# Global variable for scraping status
scraping_in_progress = False

@app.get("/")
async def root():
    return {
        "message": "Samsung Phone Assistant API",
        "version": "1.0.0",
        "endpoints": {
            "POST /ask": "Submit phone queries",
            "GET /phones": "List all phones",
            "GET /phones/{model_name}": "Get phone details",
            "GET /health": "Health check",
            "POST /refresh-data": "Refresh phone data"
        }
    }

@app.post("/ask", response_model=AskResponse, responses={
    200: {"model": AskResponse},
    404: {"model": ErrorResponse},
    400: {"model": ErrorResponse}
})
async def ask_question(request: AskRequest):
    """
    Main endpoint for phone queries
    """
    if not request.question or not request.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "error_code": "INVALID_REQUEST",
                "error_message": "Request must contain 'question' field"
            }
        )
    
    logger.info(f"Received question: {request.question}")
    
    try:
        # Process query through orchestrator
        result = orchestrator.process_user_query(request.question)
        
        if result['status'] == 'success':
            return AskResponse(
                status="success",
                question=request.question,
                answer=result['response'],
                query_type=result['metadata']['intent'],
                phones_involved=result['metadata'].get('phones_analyzed_names', []),
                focus_area=result['metadata']['focus_area'],
                confidence_score=result['metadata']['confidence'],
                processing_time_ms=result['metadata']['processing_times']['total_ms']
            )
        else:
            # Handle no match error
            if result.get('error_details', {}).get('error_type') == 'NO_MATCH':
                # Get available phones for suggestion
                available_phones = get_available_phone_names(limit=10)
                
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "status": "error",
                        "error_code": "NO_MATCH",
                        "error_message": f"No Samsung phones found matching '{request.question}'",
                        "suggestion": f"Try '{available_phones[0]}' or '{available_phones[1]}'" if len(available_phones) >= 2 else "No phones available",
                        "available_phones": available_phones
                    }
                )
            else:
                # Other errors
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "status": "error",
                        "error_code": "PROCESSING_ERROR",
                        "error_message": result.get('error_details', {}).get('message', 'Unknown error')
                    }
                )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API error in /ask: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "error_code": "INTERNAL_ERROR",
                "error_message": f"Internal server error: {str(e)}"
            }
        )

@app.get("/phones", response_model=PhonesListResponse)
async def list_phones(
    limit: int = Query(50, ge=1, le=1000, description="Number of results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    sort_by: str = Query("model_name", description="Field to sort by"),
    sort_order: str = Query("asc", description="Sort order: asc or desc")
):
    """
    List all phones in database with pagination and sorting
    """
    try:
        # Validate sort_by field
        valid_sort_fields = ['model_name', 'battery_mah', 'price_usd', 'main_camera_mp', 'release_date', 'display_size_inches']
        if sort_by not in valid_sort_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sort_by field. Must be one of: {', '.join(valid_sort_fields)}"
            )
        
        # Validate sort_order
        if sort_order not in ['asc', 'desc']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="sort_order must be 'asc' or 'desc'"
            )
        
        # Build query
        order_clause = f"ORDER BY {sort_by} {sort_order.upper()}"
        query = f"""
            SELECT 
                model_name, display_size_inches, battery_mah, main_camera_mp, 
                price_usd, processor, release_date, display_type
            FROM phones 
            {order_clause}
            LIMIT %s OFFSET %s
        """
        
        # Execute query
        results = rag.execute_query(query, [limit, offset])
        
        # Get total count
        count_result = rag.execute_query("SELECT COUNT(*) as total FROM phones", [])
        total_phones = count_result[0]['total'] if count_result else 0
        
        return PhonesListResponse(
            status="success",
            total_phones=total_phones,
            returned_count=len(results),
            phones=results
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /phones: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching phones: {str(e)}"
        )

@app.get("/phones/{model_name}", response_model=PhoneDetailResponse, responses={
    200: {"model": PhoneDetailResponse},
    404: {"model": ErrorResponse}
})
async def get_phone_details(model_name: str):
    """
    Get detailed specifications of a specific phone
    """
    try:
        # Use fuzzy matching to find the closest model
        fuzzy_matches = rag.fuzzy_match_phone(model_name, threshold=85)
        if not fuzzy_matches:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "status": "error",
                    "error_code": "NOT_FOUND",
                    "error_message": f"Phone '{model_name}' not found"
                }
            )
        
        # Get the best match
        best_match = fuzzy_matches[0][0]
        
        # Query for the specific phone
        query = "SELECT * FROM phones WHERE model_name = %s"
        results = rag.execute_query(query, [best_match])
        
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "status": "error",
                    "error_code": "NOT_FOUND", 
                    "error_message": f"Phone '{model_name}' not found"
                }
            )
        
        return PhoneDetailResponse(
            status="success",
            phone=results[0]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /phones/{model_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching phone details: {str(e)}"
        )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    """
    try:
        # Check database connection
        db_connection = "connected" if rag.connect() else "disconnected"
        
        # Check Ollama connection
        ollama_connection = "disconnected"
        try:
            import requests
            response = requests.get(f"{OLLAMA_CONFIG['base_url']}/api/tags", timeout=5)
            if response.status_code == 200:
                ollama_connection = "connected"
        except:
            ollama_connection = "disconnected"
        
        # Get total phones count
        count_result = rag.execute_query("SELECT COUNT(*) as total FROM phones", [])
        total_phones = count_result[0]['total'] if count_result else 0
        
        return HealthResponse(
            status="healthy",
            database_connection=db_connection,
            ollama_connection=ollama_connection,
            timestamp=datetime.now(timezone.utc).isoformat(),
            total_phones_in_db=total_phones
        )
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return HealthResponse(
            status="unhealthy",
            database_connection="error",
            ollama_connection="error",
            timestamp=datetime.now(timezone.utc).isoformat(),
            total_phones_in_db=0
        )

@app.post("/refresh-data", response_model=RefreshDataResponse, responses={
    202: {"model": RefreshDataResponse},
    401: {"model": ErrorResponse}
})
async def refresh_data(request: RefreshDataRequest = None):
    """
    Scrape and update phone data from GSMArena
    """
    global scraping_in_progress
    
    # Simple admin key check (in production, use proper authentication)
    ADMIN_KEY = "your_admin_password"  # Change this in production
    
    if request and request.admin_key != ADMIN_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "status": "error",
                "error_code": "UNAUTHORIZED",
                "error_message": "Invalid or missing admin key"
            }
        )
    
    if scraping_in_progress:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "status": "error", 
                "error_code": "ALREADY_RUNNING",
                "error_message": "Data refresh is already in progress"
            }
        )
    
    # Start scraping in background
    scraping_in_progress = True
    
    # Calculate estimated completion time (2 minutes from now)
    estimated_duration = 120  # 2 minutes
    completion_time = datetime.now(timezone.utc).timestamp() + estimated_duration
    completion_time_iso = datetime.fromtimestamp(completion_time, timezone.utc).isoformat()
    
    # Run scraping in background
    asyncio.create_task(run_data_refresh())
    
    return RefreshDataResponse(
        status="scraping_initiated",
        message="Samsung phone data scraping started",
        estimated_duration_seconds=estimated_duration,
        estimated_completion_time=completion_time_iso
    )

async def run_data_refresh():
    """
    Background task to refresh phone data
    """
    global scraping_in_progress
    
    try:
        logger.info("Starting background data refresh...")
        
        # Run the scraper
        scraper = GSMArenaScraper()
        raw_data = scraper.scrape_phones()
        
        if raw_data:
            # Process data
            processor = DataProcessor()
            processed_data = processor.process_data(raw_data)
            
            # Save to database
            successful_inserts = 0
            for phone_data in processed_data:
                if db_manager.insert_phone_data(phone_data):
                    successful_inserts += 1
            
            logger.info(f"Data refresh completed. Inserted/updated {successful_inserts} phones.")
        else:
            logger.error("No data scraped during refresh.")
            
    except Exception as e:
        logger.error(f"Error during data refresh: {e}")
    finally:
        scraping_in_progress = False

def get_available_phone_names(limit: int = 10) -> List[str]:
    """
    Get list of available phone names for suggestions
    """
    try:
        results = rag.execute_query(
            "SELECT model_name FROM phones ORDER BY model_name LIMIT %s", 
            [limit]
        )
        return [row['model_name'] for row in results]
    except:
        return ["Galaxy S23 Ultra", "Galaxy S22 Ultra", "Galaxy A54"]

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=API_CONFIG["host"],
        port=API_CONFIG["port"],
        reload=API_CONFIG["debug"]
    )