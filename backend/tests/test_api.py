import os
import sys
import tempfile
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import database
import main


class ApiTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_fd, cls.db_path = tempfile.mkstemp(suffix=".db")
        os.close(cls.db_fd)
        cls.engine = create_engine(
            f"sqlite:///{cls.db_path}",
            connect_args={"check_same_thread": False},
        )
        cls.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=cls.engine,
        )
        database.Base.metadata.create_all(bind=cls.engine)

        def override_get_db():
            db = cls.SessionLocal()
            try:
                yield db
            finally:
                db.close()

        main.app.dependency_overrides[main.get_db] = override_get_db
        cls.client = TestClient(main.app)

    @classmethod
    def tearDownClass(cls):
        main.app.dependency_overrides.clear()
        cls.engine.dispose()
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)

    def test_openapi_docs_is_available(self):
        response = self.client.get("/docs")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])

    def test_categories_starts_empty(self):
        response = self.client.get("/api/categories")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_product_crud_flow(self):
        create_payload = {
            "sku": "TEST-001",
            "description": "Cong tac thong minh",
            "category": "Cong tac",
            "brand": "JayHome",
            "image_url": "",
            "details": "2 nut",
            "list_price": 100000,
            "input_price": 80000,
            "sell_price": 120000,
        }
        create_response = self.client.post("/api/products", json=create_payload)
        self.assertEqual(create_response.status_code, 200)
        product = create_response.json()
        self.assertEqual(product["sku"], create_payload["sku"])

        categories_response = self.client.get("/api/categories")
        self.assertEqual(categories_response.status_code, 200)
        self.assertEqual(categories_response.json(), ["Cong tac"])

        list_response = self.client.get("/api/products")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.json()), 1)

        product_id = product["id"]
        update_response = self.client.put(
            f"/api/products/{product_id}",
            json={"description": "Cong tac da cap nhat", "sell_price": 130000},
        )
        self.assertEqual(update_response.status_code, 200)
        updated = update_response.json()
        self.assertEqual(updated["description"], "Cong tac da cap nhat")
        self.assertEqual(updated["sell_price"], 130000)

        search_response = self.client.get("/api/search", params={"q": "cap nhat"})
        self.assertEqual(search_response.status_code, 200)
        self.assertEqual(len(search_response.json()), 1)
        self.assertEqual(search_response.json()[0]["id"], product_id)

        delete_response = self.client.delete(f"/api/products/{product_id}")
        self.assertEqual(delete_response.status_code, 200)
        self.assertEqual(delete_response.json()["status"], "success")

        final_list_response = self.client.get("/api/products")
        self.assertEqual(final_list_response.status_code, 200)
        self.assertEqual(final_list_response.json(), [])

    def test_quote_update_and_duplicate_flow(self):
        create_payload = {
            "customer_name": "Khach A",
            "data": '{"html":"<tr></tr>","outsideData":[],"outsideInputs":[]}',
        }
        create_response = self.client.post("/api/quotes", json=create_payload)
        self.assertEqual(create_response.status_code, 200)
        quote = create_response.json()
        self.assertEqual(quote["customer_name"], "Khach A")

        quote_id = quote["id"]
        get_response = self.client.get(f"/api/quotes/{quote_id}")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json()["id"], quote_id)

        update_payload = {
            "customer_name": "Khach A Updated",
            "data": '{"html":"<tr><td>updated</td></tr>","outsideData":["x"],"outsideInputs":["0"]}',
        }
        update_response = self.client.put(f"/api/quotes/{quote_id}", json=update_payload)
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.json()["customer_name"], "Khach A Updated")
        self.assertEqual(update_response.json()["data"], update_payload["data"])

        duplicate_response = self.client.post(f"/api/quotes/{quote_id}/duplicate")
        self.assertEqual(duplicate_response.status_code, 200)
        duplicate = duplicate_response.json()
        self.assertNotEqual(duplicate["id"], quote_id)
        self.assertEqual(duplicate["customer_name"], "Khach A Updated - Copy")
        self.assertEqual(duplicate["data"], update_payload["data"])

    def test_uploaded_price_normalization(self):
        one_price = main._normalize_uploaded_prices(
            {"list_price": "1.234.000", "input_price": "", "sell_price": 0}
        )
        self.assertEqual(one_price["list_price"], 1234000)
        self.assertEqual(one_price["input_price"], 1234000)
        self.assertEqual(one_price["sell_price"], 1234000)

        two_prices = main._normalize_uploaded_prices(
            {"list_price": "2.500.000", "input_price": "1.700.000", "sell_price": 0}
        )
        self.assertEqual(two_prices["list_price"], 2500000)
        self.assertEqual(two_prices["input_price"], 1700000)
        self.assertEqual(two_prices["sell_price"], 2500000)

        three_prices = main._normalize_uploaded_prices(
            {"list_price": 3200000, "input_price": 2100000, "sell_price": 2800000}
        )
        self.assertEqual(three_prices["list_price"], 3200000)
        self.assertEqual(three_prices["input_price"], 2100000)
        self.assertEqual(three_prices["sell_price"], 2800000)

        existing = type(
            "ExistingProduct",
            (),
            {"list_price": 1000, "input_price": 700, "sell_price": 900},
        )()
        no_price = main._normalize_uploaded_prices({}, existing)
        self.assertEqual(no_price["list_price"], 1000)
        self.assertEqual(no_price["input_price"], 700)
        self.assertEqual(no_price["sell_price"], 900)


if __name__ == "__main__":
    unittest.main()
