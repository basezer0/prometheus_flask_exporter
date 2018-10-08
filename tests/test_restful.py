import unittest
from unittest_helper import BaseTestCase
from flask import request, abort
from flask_restful import Resource, Api


import time

class RestfulTest(BaseTestCase):
    def test_exception(self):
        metrics = self.metrics()
        api = Api(self.app)

        class FailingEndpoint(Resource):
            @metrics.summary('http_with_exception',
                             'Tracks the method raising an exception',
                             labels={'status': lambda r: r.status_code})
            def get(self):
                raise NotImplementedError('On purpose')

        api.add_resource(FailingEndpoint, '/exception')

        self.client.get('/exception')

        self.assertMetric('http_with_exception_count', 1.0, ('status', 500))
        self.assertMetric('http_with_exception_sum', '.', ('status', 500))

if __name__ == '__main__':
    unittest.main()
