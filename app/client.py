from typing import Any

import httpx

BASE_URL = "https://lsapp-prod.bonus.is/CommerceService/UCJson.svc"


class BonusClient:
    def __init__(self, token: str = "", card_id: str = "", store_id: str = "") -> None:
        self.token = token
        self.card_id = card_id
        self.store_id = store_id
        self._client = httpx.Client(timeout=30.0)

    def _post(self, method: str, data: dict[str, Any] | None = None) -> Any:
        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.token:
            headers["LSRETAIL-TOKEN"] = self.token
        response = self._client.post(f"{BASE_URL}/{method}", json=data or {}, headers=headers)
        response.raise_for_status()
        return response.json()

    def _get_image_url(self, image_id: str, width: int = 400, height: int = 400) -> str:
        return f"{BASE_URL}/ImageStreamGetById?id={image_id}&width={width}&height={height}"

    # === System ===

    def ping(self) -> str:
        result = self._post("Ping")
        return result.get("PingResult", "")  # type: ignore[no-any-return]

    # === Products ===

    def search_items(self, query: str, max_items: int = 20, include_details: bool = True) -> list[dict[str, Any]]:
        result = self._post("ItemsSearch", {
            "search": query,
            "maxNumberOfItems": max_items,
            "includeDetails": include_details,
            "storeId": self.store_id,
            "cardId": self.card_id,
        })
        return result.get("ItemsSearchResult", [])  # type: ignore[no-any-return]

    def get_item(self, item_id: str) -> dict[str, Any]:
        result = self._post("ItemGetById", {"itemId": item_id, "storeId": self.store_id})
        return result.get("ItemGetByIdResult", {})  # type: ignore[no-any-return]

    # === Stores ===

    def get_stores(self) -> list[dict[str, Any]]:
        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.token:
            headers["LSRETAIL-TOKEN"] = self.token
        response = self._client.post(f"{BASE_URL}/StoresGetAll", json={}, headers=headers)
        response.raise_for_status()
        result: dict[str, Any] = response.json()
        return result.get("StoresGetAllResult", [])  # type: ignore[no-any-return]

    # === Offers ===

    def get_published_offers(self, card_id: str = "", item_id: str = "") -> list[dict[str, Any]]:
        result = self._post("PublishedOffersGetByCardId", {
            "cardId": card_id or self.card_id,
            "itemId": item_id,
        })
        return result.get("PublishedOffersGetByCardIdResult", [])  # type: ignore[no-any-return]

    # === Loyalty ===

    def get_point_rate(self) -> float:
        result = self._post("GetPointRate")
        return result.get("GetPointRateResult", 0)  # type: ignore[no-any-return]

    def contact_get_by_card_id(self, card_id: str = "") -> dict[str, Any]:
        result = self._post("MemberContactGetByCardId", {
            "cardId": card_id or self.card_id,
        })
        return result.get("MemberContactGetByCardIdResult", {})  # type: ignore[no-any-return]

    def contact_search(self, search: str, search_type: int = 0) -> list[dict[str, Any]]:
        result = self._post("ContactSearch", {
            "search": search,
            "searchType": search_type,
        })
        return result.get("ContactSearchResult", [])  # type: ignore[no-any-return]

    # === Auth ===

    def login(self, username: str, password: str) -> dict[str, Any]:
        result = self._post("MemberContactLogon", {
            "userName": username,
            "password": password,
        })
        return result.get("MemberContactLogonResult", {})  # type: ignore[no-any-return]

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "BonusClient":
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()
