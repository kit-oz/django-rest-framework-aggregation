from django.db import connection
from parameterized import parameterized
from rest_framework.test import APITestCase

from .fixtures import RECORDS
from .models import TestCaseModel
from .test_data import (
    ANNOTATIONS_TESTING,
    SORTED_GROUPS_TESTING,
    UNSORTED_GROUPS_TESTING,
)


class AggregationTests(APITestCase):
    URL = "/test/aggregation"

    def setUp(self):
        for record in RECORDS:
            record = TestCaseModel(**record)
            record.save()

    @parameterized.expand(ANNOTATIONS_TESTING)
    def test_annotations(self, query, expected_response):
        if connection.vendor != "postgresql" and query["aggregation"] == "percentile":
            self.skipTest("Percentile only works with PostgreSQL")
        response = self.client.post(self.URL, query, format="json")
        self.assertEqual(
            response.status_code,
            200,
            msg=f"Failed on: {query}" f"\nResponse: {response.data}",
        )
        self.assertEqual(
            response.data,
            expected_response,
            msg=f"Failed on: {query}"
            f"\nResponse: {response.data}"
            f"\nExpected: {expected_response}",
        )

    @parameterized.expand(UNSORTED_GROUPS_TESTING)
    def test_group_by(self, query, expected_response):
        response = self.client.post(self.URL, query, format="json")
        self.assertEqual(
            response.status_code,
            200,
            msg=f"Failed on: {query}" f"\nResponse: {response.data}",
        )
        self.assertEqual(
            len(response.data),
            len(expected_response),
            msg=f"Failed on: {query}"
            f"\nResponse: {response.data}"
            f"\nExpected: {expected_response}",
        )
        for result in response.data:
            self.assertIn(
                result,
                expected_response,
                msg=f"Failed on: {query}"
                f"\nResponse: {response.data}"
                f"\nExpected: {expected_response}",
            )

    @parameterized.expand(SORTED_GROUPS_TESTING)
    def test_group_by_fields(self, query, expected_response, query_params=None):
        response = self.client.post(
            self.URL, query, format="json", query_params=query_params
        )
        self.assertEqual(
            response.status_code,
            200,
            msg=f"Failed on: {query}" f"\nResponse: {response.data}",
        )
        self.assertEqual(
            len(response.data),
            len(expected_response),
            msg=f"Failed on: {query}"
            f"\nResponse: {response.data}"
            f"\nExpected: {expected_response}",
        )
        for n in range(len(expected_response)):
            self.assertDictEqual(
                response.data[n],
                expected_response[n],
                msg=f"Failed on: {query}"
                f"Difference in elements at index: {n}"
                f"\nResponse element: {response.data[n]}"
                f"\nExpected element: {expected_response[n]}",
            )
