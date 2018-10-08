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

    def test_handled_exception(self):
        metrics = self.metrics()
        api = Api(self.app)

        class CustomError(Exception):
            def __init__(self, message, status_code=500, payload=None):
                Exception.__init__(self)
                self.message = message
                self.status_code = status_code
                self.payload = payload

            def to_dict(self):
                rv = dict(self.payload or ())
                rv['message'] = self.message
                return rv

        @self.app.errorhandler(CustomError)
        def handle_error(exception):
            response = jsonify(exception.to_dict())
            response.status_code = 501
            return response

        class FailingEndpoint(Resource):
            @metrics.summary('http_with_exception',
                             'Tracks the method raising an exception',
                             labels={'status': lambda r: r.status_code})
            def get(self):
                raise CustomError('On purpose')

        api.add_resource(FailingEndpoint, '/exception')

        self.client.get('/exception')

        self.assertMetric('http_with_exception_count', 1.0, ('status', 500))
        self.assertMetric('http_with_exception_sum', '.', ('status', 500))

if __name__ == '__main__':
    unittest.main()
