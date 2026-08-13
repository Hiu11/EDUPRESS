import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


class ObservabilityTest(unittest.TestCase):
    def test_request_id_is_returned(self):
        client = TestClient(app)

        response = client.get("/health", headers={"X-Request-ID": "test-request-id"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["X-Request-ID"], "test-request-id")

    def test_frontend_errors_are_accepted(self):
        client = TestClient(app)

        response = client.post(
            "/api/monitoring/frontend-error",
            json={"message": "Client crashed", "route": "#quiz", "source": "unit-test"},
        )

        self.assertEqual(response.status_code, 202)
        self.assertTrue(response.json()["accepted"])

    def test_deployment_health_reports_degraded_when_required_check_fails(self):
        client = TestClient(app)

        with (
            patch("app.api.health._check_postgres", return_value={"ok": False, "detail": "db down"}),
            patch("app.api.health._check_mongo", return_value={"ok": True, "detail": "mongo ok"}),
            patch("app.api.health._check_redis", return_value={"ok": True, "detail": "redis ok"}),
            patch("app.api.health._check_ai_engine", return_value={"ok": True, "detail": "ai optional"}),
        ):
            response = client.get("/health/deployment")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["status"], "degraded")
        self.assertFalse(response.json()["checks"]["postgres"]["ok"])


if __name__ == "__main__":
    unittest.main()
