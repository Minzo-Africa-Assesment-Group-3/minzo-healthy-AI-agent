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
    search: str | None = None,
    county: str | None = None,
    city: str | None = None,
    service: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    radius_km: float | None = None,
    sort: str | None = None,
    page_number: int | None = None,
    page_size: int | None = None,
    
):
    """Search the Minzo directory for business."""
    params = {}
    
    if search:
        params["search"] = search
    if county:
            params["county"] = county
    if city:
        params["city"] = city
    if service:
        params["service"] = service
    if latitude is not None and longitude is not None:
        params["latitude"] = latitude
        params["longitude"] = longitude

        if radius_km is not None:
            params["radiusKM"] = radius_km

    if sort:
        params["sort"] = sort
    if page_number is not None:
        params["pageNumber"] = page_number
    if page_size is not None:
        params["pageSize"] = page_size

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{MINZO_API_URL}/api/v1/businesses",
            params=params,
            timeout=10.0,
        )
        
    response.raise_for_status()
    
    return response.json()


@tool
async def get_business_profile(slug: str):
    """Get Public profile of a specific healthcare business using its slug."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{MINZO_API_URL}/api/v1/businesses/{slug}",
            timeout=10.0,
        )
        
    response.raise_for_status()
    
    return response.json()


@tool
async def get_business_ratings(business_id: str):
    """Get rating and review count for a (healthcare) business."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{MINZO_API_URL}/api/v1/businesses/{business_id}/rating",
            timeout=10.0,
        )
        
    response.raise_for_status()
    
    return response.json()


@tool
async def get_business_reviews(
    business_id: str,
    page_number: int | None = None,
    page_size: int |None = None
):
    """Get customer reviews for a (healthcare) business."""
    params = {}
    
    if page_number is not None:
        params["pageNumber"] = page_number
    if page_size is not None:
            params["pageSize"] = page_size
            
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{MINZO_API_URL}/api/v1/businesses/{business_id}/reviews",
            params=params
            timeout=10.0,
        )
        
    response.raise_for_status()
    
    return response.json()


@tool
async def find_services(
    search: str,
    limit: int | None = None,
):
    """Find healthcare services."""
    params =  {"search": search},
    
    if limit is not None:
        params["limit"] = limit
        
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{MINZO_API_URL}/api/v1/services",
            paramas=params,
            timeout=10.0,
        )
        
    response.raise_for_status()
    
    return response.json()


@tool
async def find_counties(
    search: str,
    limit: int | None = None
):
    """Find healthcare service within a county, matching a search term."""
    params = {
        "search": search,
        }
    
    if limit is not None:
        params["limit"] = limit
        
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{MINZO_API_URL}/api/v1/services",
            params=params,
            timeout=10.0,
        )
        
    response.raise_for_status()
    
    return response.json()


@tool
async def find_cities(search: str, county_id: str | None = None, limit: int | None = None):
    """Find  available cities or towns matching a search term."""
    params = {
        "search": search,
    }
    if county_id is not None:
        params["countyId"] = county_id
    if limit is not None:
        params["limit"] = limit
        
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{MINZO_API_URL}/api/v1/cities",
            params=params,
            timeout=10.0,
        )
        
    response.raise_for_status()
    
    return response.json()


DIRECTORY_TOOLS = [
    search_businesses,
    get_business_profile,
    get_business_ratings,
    get_business_reviews,
    find_counties,
    find_cities,
    find_services,
]
