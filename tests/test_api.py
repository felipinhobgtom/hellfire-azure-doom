import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app as api


class ScoreApiTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.db_patch = patch.object(api, "DB_PATH", Path(self.tempdir.name) / "scores.db")
        self.db_patch.start()
        api.app.config["TESTING"] = True
        self.client = api.app.test_client()

    def tearDown(self):
        self.db_patch.stop()
        self.tempdir.cleanup()

    def test_create_score_persists_and_appears_in_sorted_listing(self):
        response = self.client.post("/api/scores", json={"player": "marine", "kills": 8})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["player"], "marine")
        self.assertTrue(response.json["created_at"].endswith("+00:00"))
        listing = self.client.get("/api/scores")
        self.assertEqual(listing.status_code, 200)
        self.assertEqual(listing.json[0]["id"], response.json["id"])

    def test_rejects_invalid_payload_and_out_of_range_score(self):
        for payload in (None, {"player": "", "kills": 1}, {"player": "a" * 25, "kills": 1}, {"player": "x", "kills": True}, {"player": "x", "kills": -1}, {"player": "x", "kills": 1.5}):
            with self.subTest(payload=payload):
                response = self.client.post("/api/scores", data=json.dumps(payload), content_type="application/json")
                self.assertEqual(response.status_code, 400)

    def test_health_reports_sqlite(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["database"], "sqlite")


if __name__ == "__main__":
    unittest.main()
