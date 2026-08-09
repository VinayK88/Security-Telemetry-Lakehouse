import unittest
from datetime import datetime, timezone

from app.detection import score_features
from app.features import build_hourly_features


class FeatureTests(unittest.TestCase):
    def test_feature_aggregation_and_finding(self):
        ts = datetime(2026, 8, 10, 10, 20, tzinfo=timezone.utc).isoformat()
        rows = []
        for i in range(8):
            rows.append(
                {
                    "event_time": ts,
                    "principal": "finance@example.com",
                    "src_ip": f"198.51.100.{i}",
                    "action": "login" if i < 7 else "role_assignment",
                    "outcome": "failure" if i < 7 else "success",
                    "risk": 0.8,
                }
            )

        features = build_hourly_features(rows)
        self.assertEqual(len(features), 1)
        self.assertEqual(features[0].failed_logins, 7)
        self.assertEqual(features[0].distinct_ips, 8)
        self.assertEqual(features[0].sensitive_actions, 1)

        findings = score_features(features)
        self.assertEqual(len(findings), 1)
        self.assertGreater(findings[0].score, 0.35)


if __name__ == "__main__":
    unittest.main()
