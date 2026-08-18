"""
tests for extractor.py - uses mocks so we dont actually hit the api
"""
import pytest
from unittest.mock import patch, MagicMock
from extractor import _fetch_page_with_retry, fetch_products
import config


def _make_response(status_code, products):
    """build a fake requests.Response"""
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = {'products': products}
    return mock


@pytest.fixture(autouse=True)
def reset_config():
    """ensure test config is sensible"""
    original_retries = config.MAX_RETRIES
    config.MAX_RETRIES = 2
    yield
    config.MAX_RETRIES = original_retries


class TestFetchPageWithRetry:
    @patch('extractor.requests.get')
    def test_returns_data_on_200(self, mock_get):
        products = [{'code': '123', 'product_name': 'Bread'}]
        mock_get.return_value = _make_response(200, products)
        result = _fetch_page_with_retry(1)
        assert result['products'] == products

    @patch('extractor.time.sleep')
    @patch('extractor.requests.get')
    def test_retries_on_429(self, mock_get, mock_sleep):
        # fail with 429 twice then succeed
        mock_get.side_effect = [
            _make_response(429, []),
            _make_response(200, [{'code': '999', 'product_name': 'Milk'}]),
        ]
        result = _fetch_page_with_retry(1)
        assert result is not None
        assert mock_sleep.called

    @patch('extractor.time.sleep')
    @patch('extractor.requests.get')
    def test_returns_none_after_all_retries_fail(self, mock_get, mock_sleep):
        mock_get.return_value = _make_response(429, [])
        result = _fetch_page_with_retry(1)
        assert result is None


class TestFetchProducts:
    @patch('extractor._fetch_page_with_retry')
    def test_yields_products_then_stops_on_empty(self, mock_fetch):
        mock_fetch.side_effect = [
            {'products': [{'code': '1'}] * 100},
            {'products': []},
        ]
        pages = list(fetch_products())
        assert len(pages) == 1
        assert len(pages[0]) == 100

    @patch('extractor._fetch_page_with_retry')
    def test_stops_on_partial_page(self, mock_fetch):
        mock_fetch.side_effect = [
            {'products': [{'code': str(i)} for i in range(50)]},
        ]
        pages = list(fetch_products())
        assert len(pages) == 1
