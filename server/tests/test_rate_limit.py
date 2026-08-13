import unittest

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.core.rate_limit import rate_limit, reset_rate_limits


class RateLimitTest(unittest.TestCase):
    def setUp(self):
        reset_rate_limits()

    def tearDown(self):
        reset_rate_limits()

    def test_returns_429_after_limit_is_exhausted(self):
        app = FastAPI()

        @app.get("/limited", dependencies=[Depends(rate_limit(2, 60, "unit-test"))])
        def limited_endpoint():
            return {"ok": True}

        client = TestClient(app)

        self.assertEqual(client.get("/limited").status_code, 200)
        self.assertEqual(client.get("/limited").status_code, 200)

        limited = client.get("/limited")

        self.assertEqual(limited.status_code, 429)
        self.assertEqual(limited.json()["detail"]["code"], "rate_limited")
        self.assertEqual(limited.headers["X-RateLimit-Remaining"], "0")
        self.assertIn("Retry-After", limited.headers)

    def test_limit_scope_is_separate(self):
        app = FastAPI()

        @app.get("/a", dependencies=[Depends(rate_limit(1, 60, "scope-a"))])
        def scope_a():
            return {"scope": "a"}

        @app.get("/b", dependencies=[Depends(rate_limit(1, 60, "scope-b"))])
        def scope_b():
            return {"scope": "b"}

        client = TestClient(app)

        self.assertEqual(client.get("/a").status_code, 200)
        self.assertEqual(client.get("/a").status_code, 429)
        self.assertEqual(client.get("/b").status_code, 200)


if __name__ == "__main__":
    unittest.main()
