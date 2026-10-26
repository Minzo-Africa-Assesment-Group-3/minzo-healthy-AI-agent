
import json
from typing import Annotated, Any

from langchain_core.tools import BaseTool, tool
from pydantic import Field

from app.clients.express_api import ExpressApiClient, ExpressApiError


def _format_result(result: Any) -> str:
    """Convert backend data into text the assistant can understand."""
    return json.dumps(result, ensure_ascii=False, default=str)


def build_directory_tools(api: ExpressApiClient) -> list[BaseTool]:
    """Build read-only tools for the healthcare directory."""

    @tool
    async def search_healthcare_businesses(
        search: Annotated[
            str, Field(description="Name or keyword to search for")
        ] = "",
        county: Annotated[str, Field(description="County to search in")] = "",
        city: Annotated[str, Field(description="City to search in")] = "",
        service_id: Annotated[
            str, Field(description="Healthcare service ID")
        ] = "",
        page: Annotated[int, Field(ge=1, description="Page number")] = 1,
    ) -> str:
        """Find healthcare professionals and institutions in the directory."""
        try:
            result = await api.search_businesses(
                search=search.strip() or None,
                county=county.strip() or None,
                city=city.strip() or None,
                service_id=service_id.strip() or None,
                page=page,
                page_size=10,
            )
            return _format_result(result)
        except ExpressApiError:
            return "The directory search is temporarily unavailable."

    @tool
    async def get_healthcare_business(
        business_slug: Annotated[
            str, Field(description="The exact business slug from directory results")
        ],
    ) -> str:
        """Retrieve details about one healthcare business."""
        try:
            return _format_result(await api.get_business(business_slug.strip()))
        except ExpressApiError:
            return "Business details are temporarily unavailable."

    @tool
    async def get_healthcare_business_reviews(
        business_id: Annotated[
            str, Field(description="The business ID from directory results")
        ],
        page: Annotated[int, Field(ge=1, description="Page number")] = 1,
    ) -> str:
        """Retrieve reviews for a healthcare business."""
        try:
            result = await api.get_business_reviews(
                business_id=business_id.strip(),
                page=page,
                page_size=10,
            )
            return _format_result(result)
        except ExpressApiError:
            return "Business reviews are temporarily unavailable."

    @tool
    async def get_healthcare_business_rating(
        business_id: Annotated[
            str, Field(description="The business ID from directory results")
        ],
    ) -> str:
        """Retrieve the rating summary for a healthcare business."""
        try:
            return _format_result(
                await api.get_business_rating(business_id.strip())
            )
        except ExpressApiError:
            return "The business rating is temporarily unavailable."

    @tool
    async def search_healthcare_services(
        search: Annotated[
            str,
            Field(description="Healthcare service name; enter at least two characters"),
        ] = "",
    ) -> str:
        """Find healthcare services by name. Search terms must contain at least two characters."""
        search = search.strip()

        if len(search) < 2:
            return "Please provide at least two characters to search for a service."

        try:
            return _format_result(
                await api.search_services(search=search)
            )
        except ExpressApiError:
            return "Healthcare services are temporarily unavailable."

    @tool
    async def search_counties(
        search: Annotated[
            str,
            Field(description="County name; enter at least two characters"),
        ] = "",
    ) -> str:
        """Find counties by name. Search terms must contain at least two characters."""
        search = search.strip()

        if len(search) < 2:
            return "Please provide at least two characters to search for a county."

        try:
            return _format_result(
                await api.search_counties(search=search)
            )
        except ExpressApiError:
            return "County information is temporarily unavailable."

    @tool
    async def search_cities(
        county_id: Annotated[
            str, Field(description="County ID returned by the county search")
        ],
        search: Annotated[
            str,
            Field(description="City name; enter at least two characters"),
        ] = "",
    ) -> str:
        """Find cities within a selected county. Use a real county ID from directory results."""
        county_id = county_id.strip()
        search = search.strip()

        if not county_id:
            return "Please select a valid county from the directory results first."

        if len(search) < 2:
            return "Please provide at least two characters to search for a city."

        try:
            return _format_result(
                await api.search_cities(
                    county_id=county_id,
                    search=search,
                )
            )
        except ExpressApiError:
            return "City information is temporarily unavailable."

    return [
        search_healthcare_businesses,
        get_healthcare_business,
        get_healthcare_business_reviews,
        get_healthcare_business_rating,
        search_healthcare_services,
        search_counties,
        search_cities,
    ]
