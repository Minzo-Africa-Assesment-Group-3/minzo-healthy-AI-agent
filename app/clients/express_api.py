from pydantic import SecretStr
from typing import Any
from urllib.parse import quote

import httpx

from app.core.config import EXPRESS_SERVICE_TOKEN


class ExpressApiError(RuntimeError):
    def __init__(
        self,
        operation: str,
        status_code: int | None = None,
    ):
        super().__init__(operation)
        self.operation = operation
        self.status_code = status_code


class ExpressApiClient:
    """Client for reading directory data from Express."""

    def __init__(self, client: httpx.AsyncClient):
        self._client = client
        self._service_token = EXPRESS_SERVICE_TOKEN

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}

        if self._service_token:
            headers["Authorization"] = (
                f"Bearer {self._service_token.get_secret_value()}"
            )

        return headers

    async def _get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        try:
            response = await self._client.get(
                path,
                params=params,
                headers=self._headers(),
                follow_redirects=False,
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as exc:
            raise ExpressApiError(
                f"GET {path}",
                exc.response.status_code,
            ) from None

        except (httpx.HTTPError, ValueError) as exc:
            raise ExpressApiError(f"GET {path}") from exc

    async def get_business(self, business_slug: str) -> Any:
        slug = quote(business_slug, safe="")
        return await self._get(f"/api/v1/businesses/{slug}")

    async def search_businesses(
        self,
        search: str | None = None,
        county: str | None = None,
        city: str | None = None,
        service_id: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        radius_km: float | None = None,
        sort: str | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> Any:
        params: dict[str, Any] = {
            "pageNumber": page,
            "pageSize": min(max(page_size, 1), 20),
        }

        optional_params = {
            "search": search,
            "county": county,
            "city": city,
            "serviceId": service_id,
            "latitude": latitude,
            "longitude": longitude,
            "radiusKm": radius_km,
            "sort": sort,
        }

        params.update({
            key: value
            for key, value in optional_params.items()
            if value is not None
        })

        return await self._get("/api/v1/businesses", params)

    async def get_business_reviews(
        self,
        business_id: str,
        page: int = 1,
        page_size: int = 10,
    ) -> Any:
        business_id = quote(business_id, safe="")

        return await self._get(
            f"/api/v1/businesses/{business_id}/reviews",
            {
                "pageNumber": page,
                "pageSize": min(max(page_size, 1), 20),
            },
        )

    async def get_business_rating(self, business_id: str) -> Any:
        business_id = quote(business_id, safe="")
        return await self._get(
            f"/api/v1/businesses/{business_id}/rating"
        )

    async def search_services(
        self,
        search: str | None = None,
        limit: int = 10,
    ) -> Any:
        params: dict[str, Any] = {
            "limit": min(max(limit, 1), 20)
        }

        if search:
            params["search"] = search

        return await self._get("/api/v1/services", params)

    async def search_counties(
        self,
        search: str | None = None,
        limit: int = 10,
    ) -> Any:
        params: dict[str, Any] = {
            "limit": min(max(limit, 1), 20)
        }

        if search:
            params["search"] = search

        return await self._get("/api/v1/counties", params)

    async def search_cities(
        self,
        county_id: str,
        search: str | None = None,
        limit: int = 10,
    ) -> Any:
        params: dict[str, Any] = {
            "limit": min(max(limit, 1), 20)
        }

        if search:
            params["search"] = search

        county_id = quote(county_id, safe="")

        return await self._get(
            f"/api/v1/counties/{county_id}/cities",
            params,
        )
        
    def for_user(self, token: SecretStr):
        """Create a client scoped to the authenticated user."""
        from app.clients.current_user_api import CurrentUserApiClient

        return CurrentUserApiClient(self._client, token)
