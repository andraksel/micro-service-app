import os
import uuid

import httpx


gateway_url = os.getenv("GATEWAY_URL", "http://localhost:8080").rstrip("/")


def main() -> None:
    with httpx.Client(timeout=10) as client:
        user_response = client.post(
            f"{gateway_url}/api/users",
            json={"email": f"seed-{uuid.uuid4().hex[:8]}@example.com", "full_name": "Seed User"},
        )
        user_response.raise_for_status()

        product_response = client.post(
            f"{gateway_url}/api/products",
            json={
                "name": "Seed Product",
                "description": "Product created by scripts/seed-data.py",
                "price": "19.99",
                "currency": "USD",
                "stock": 25,
            },
        )
        product_response.raise_for_status()

        print({"user": user_response.json(), "product": product_response.json()})


if __name__ == "__main__":
    main()
