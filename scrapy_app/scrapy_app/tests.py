import os

from scrapy.http import Response, Request

def fake_response_from_file(file_name, url=None):
    """
    Create a Scrapy fake HTTP response from a HTML file
    @param file_name: The relative filename from the responses directory,
                      but absolute paths are also accepted.
    @param url: The URL of the response.
    returns: A scrapy HTTP response which can be used for unittesting.
    """
    if not url:
        url = 'https://www.apartments.com/222-e-39th-st-new-york-ny-unit-15d/ssv2975/'

    request = Request(url=url)
    if not file_name[0] == '/':
        responses_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(responses_dir, file_name)
    else:
        file_path = file_name

    file_content = open(file_path, 'r').read()

    response = Response(url=url,
        request=request,
        body=file_content)
    response.encoding = 'utf-8'
    return response


from unittest import TestCase
from scrapy_app.scrapy_app.spiders import icrawler

class SpiderTest(TestCase):

    def setUp(self):
        self.spider = icrawler

    def _test_item_results(self, results, expected_length):
        count = 0
        permalinks = set()
        for item in results:
            self.assertIsNotNone(item['content'])
            self.assertIsNotNone(item['title'])
        self.assertEqual(count, expected_length)

    def test_parse(self):
        results = self.spider.parse(fake_response_from_file('./sample.html'))
        self._test_item_results(results, 10)