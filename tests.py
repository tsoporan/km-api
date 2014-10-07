import os
import unittest
import api

import simplejson as json

class KMAPITest(unittest.TestCase):

    def setUp(self):

        api.app.testing = True

        # Load the test data.
        api.load_data('data/metrics_over_time_test_data.csv')

        self.app = api.app.test_client()

    def tearDown(self):
        api.METRICS = []

    def test_index(self):
        resp = self.app.get('/')

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data, 'KM Demo API!')

    def test_all_metrics(self):
        resp = self.app.get('/metrics')

        js = json.loads(resp.data)
        amount = js['amount']
        pages = js['pages']

        self.assertEqual(amount, 5)
        self.assertEqual(pages, 1)

    def test_metrics_by_id(self):
        resp = self.app.get('/metrics/2')

        js = json.loads(resp.data)

        amount = js['amount']

        self.assertEqual(amount, 1)

    def test_metrics_by_date(self):
        resp = self.app.get('/metrics?start_date=2009-01-02&end_date=2009-01-05')

        js = json.loads(resp.data)

        amount = js['amount']

        self.assertEqual(amount, 2)

    def test_metrics_id_and_date(self):
        resp = self.app.get('/metrics/1?start_date=2009-01-02&end_date=2009-01-02')

        js = json.loads(resp.data)

        amount = js['amount']

        self.assertEqual(amount, 1)

    def test_metric_limit(self):
        resp = self.app.get('/metrics?limit=2')

        js = json.loads(resp.data)

        amount = js['amount']

        self.assertEqual(amount, 2)

    def test_metric_id_and_limit(self):
        resp = self.app.get('/metrics/2?limit=3')

        js = json.loads(resp.data)

        amount = js['amount']

        self.assertEqual(amount, 1)

    def test_metric_offset(self):
        resp = self.app.get('/metrics?offset=1')

        js = json.loads(resp.data)

        metrics = js['metrics']

        self.assertEqual(metrics[0]['metric_id'], '2')

    def test_metric_pages(self):
        resp = self.app.get('/metrics?limit=2')

        js = json.loads(resp.data)

        pages = js['pages']

        self.assertEqual(pages, 3)

if __name__ == '__main__':
    unittest.main()
