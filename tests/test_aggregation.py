from rest_framework.test import APITestCase
from parameterized import parameterized
from .models import TestCaseModel
from .fixtures import RECORDS
from .test_data import TEST_ANNOTATIONS


class AggregationTests(APITestCase):
    URL = "/test/aggregation"

    def setUp(self):
        for record in RECORDS:
            record = TestCaseModel(**record)
            record.save()

    @parameterized.expand(TEST_ANNOTATIONS)
    def test_annotations(self, query, expected_response):
        response = self.client.get(self.URL, query, format="json")
        self.assertEqual(response.status_code, 200,
                         msg=f"Failed on: {query}\n"
                             f"response: {response.data}")
        self.assertEqual(response.data, expected_response,
                         msg=f"Failed on: {query}\n"
                             f"response: {response.data}\n"
                             f"expected: {expected_response}")

    def test_group_by_field(self):
        query = {"aggregation": "count", "groupByFields": "group1"}
        expected_response = [{"group1": "1", "value": 2},
                             {"group1": "2", "value": 1},
                             {"group1": "3", "value": 3}]

        response = self.client.get(self.URL, query, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)
        for result in response.data:
            self.assertIn(result, expected_response)

    def test_limit_sort_desc(self):
        query = {"aggregation": "count", "groupByFields": "group1",
                 "limit": 1, "limitByField": "group1", "order": "desc"}
        expected_response = [{"group1": "3", "value": 3}]

        response = self.client.get(self.URL, query, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_response)

    def test_limit_sort_asc(self):
        query = {"aggregation": "count", "groupByFields": "group1",
                 "limit": 1, "limitByField": "group1", "order": "asc"}
        expected_response = [{"group1": "2", "value": 1}]

        response = self.client.get(self.URL, query, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_response)

    def test_limit_show_other(self):
        query = {"aggregation": "count", "groupByFields": "group1",
                 "limit": 1, "limitByField": "group1", "order": "desc",
                 "showOther": 1}
        expected_response = [{"group1": "3", "value": 3},
                             {"group1": "Other", "value": 3}]

        response = self.client.get(self.URL, query, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_response)

    def test_limit_show_empty_other(self):
        query = {"aggregation": "count", "groupByFields": "group1",
                 "limit": 3, "limitByField": "group1", "order": "desc",
                 "showOther": 1}
        expected_response = [{"group1": "3", "value": 3},
                             {"group1": "1", "value": 2},
                             {"group1": "2", "value": 1}]

        response = self.client.get(self.URL, query, format="json")
        self.assertEqual(response.status_code, 200)
        for result in response.data:
            self.assertIn(result, expected_response)

    def test_group_by_multiple_field(self):
        query = {"aggregation": "count", "groupByFields": "group1,group2"}
        expected_response = [{"group1": "1", "group2": "1", "value": 1},
                             {"group1": "1", "group2": "2", "value": 1},
                             {"group1": "2", "group2": "1", "value": 1},
                             {"group1": "3", "group2": "1", "value": 1},
                             {"group1": "3", "group2": "2", "value": 1},
                             {"group1": "3", "group2": "3", "value": 1}]

        response = self.client.get(self.URL, query, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 6)
        for result in response.data:
            self.assertIn(result, expected_response)

    def test_limit_with_group_by_multiple_field(self):
        query = {"aggregation": "count", "groupByFields": "group1,group2",
                 "limit": 1, "limitByField": "group1", "order": "desc"}
        expected_response = [{"group1": "3", "group2": "1", "value": 1},
                             {"group1": "3", "group2": "2", "value": 1},
                             {"group1": "3", "group2": "3", "value": 1}]

        response = self.client.get(self.URL, query, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)
        for result in response.data:
            self.assertIn(result, expected_response)