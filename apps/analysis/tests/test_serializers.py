from django.test import TestCase

from apps.analysis.serializers import AnalysisSerializer


class TestAnalysisSerializer(TestCase):
    def setUp(self):
        self.data = {
            "about": "INCOME",
            "period_type": "weekly",
            "period_start": "2026-04-05",
            "period_end": "2026-04-11",
        }

    def test_serializer(self):
        self.analysis = AnalysisSerializer(data=self.data)
        self.analysis.is_valid()

        self.assertTrue(self.analysis.is_valid())
        self.assertEqual(self.analysis.data["about"], self.data["about"])
        self.assertEqual(self.analysis.data["period_type"], self.data["period_type"])
        self.assertEqual(self.analysis.data["period_start"], self.data["period_start"])
        self.assertEqual(self.analysis.data["period_end"], self.data["period_end"])

    def test_invalid_date_range(self):
        # period_start > period_end 이면 에러
        invalid_data = {
            **self.data,
            "period_start": "2026-04-11",
            "period_end": "2026-04-05",
        }
        serializer = AnalysisSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
