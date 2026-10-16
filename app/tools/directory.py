import os
import httpx
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

MINZO_API_URL = os.getenv(
    "MINZO_API_URL",
    "http://localhost:3000",
)


@tool
async def search_businesses(
    query: str | None = None,
    county: str | None = None,
    city: str | None = None,
    service: str | None = None
):
    """Search the Minzo directory for business."""
    params = {}
    
    if query:
        params["query"] = query
    if city:
        params["city"] = city
    if service:
        params["service"] = service
        
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{MINZO_API_URL}/businesses",
            params=params,
            timeout=10.0,
        )
        
    response.raise_for_status()
    
    return response.json()


@tool
async def get_business_reviews(business_id: str):
    """Get review for a specific business."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{MINZO_API_URL}/businesses/{business_id}/reviews",
            timeout=10.0,
        )
        
    response.raise_for_status()
    
    return response.json()


@tool
async def get_business_ratings(business_id: str):
    """Get rating infomation for a business."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{MINZO_API_URL}/businesses/{business_id}/ratings",
            timeout=10.0,
        )
        
    response.raise_for_status()
    
    return response.json()


@tool
async def get_business_service(business_id: str):
    """Get services offered by a business."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{MINZO_API_URL}/businesses/{business_id}/services",
            timeout=10.0,
        )
        
    response.raise_for_status()
    
    return response.json()

@tool
async def list_counties(business_id: str):
    """Get avaliable counties."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{MINZO_API_URL}/counties",
            timeout=10.0,
        )
        
    response.raise_for_status()
    
    return response.json()


@tool
async def list_cities(business_id: str):
    """Get available cities."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{MINZO_API_URL}/cities",
            timeout=10.0,
        )
        
    response.raise_for_status()
    
    return response.json()


DIRECTORY_TOOLS = [
    search_businesses,
    get_business_service,
    get_business_ratings,
    get_business_reviews,
    list_counties,
    list_cities
]
