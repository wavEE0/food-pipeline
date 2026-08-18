"""
tests for transformer.py
written alongside the implementation to catch regressions
"""
import pytest
from transformer import transform_batch, _clean_category


def _make_product(barcode='1234567890', name='Test Product', calories=100.0,
                  protein=5.0, carbs=20.0, fat=3.0, category_tags=None):
    """helper to build a minimal valid product dict"""
    return {
        'code': barcode,
        'product_name': name,
        'nutriments': {
            'energy-kcal_100g': calories,
            'proteins_100g': protein,
            'carbohydrates_100g': carbs,
            'fat_100g': fat,
            'fiber_100g': None,
            'sodium_100g': None,
        },
        'categories_tags': category_tags or [],
    }


class TestTransformBatch:
    def test_valid_product_transforms_correctly(self):
        products = [_make_product()]
        records, rejected = transform_batch(products)
        assert len(records) == 1
        assert rejected == 0
        r = records[0]
        assert r['barcode'] == '1234567890'
        assert r['product_name'] == 'Test Product'
        assert r['calories'] == 100.0

    def test_missing_barcode_rejected(self):
        products = [_make_product(barcode='')]
        records, rejected = transform_batch(products)
        assert len(records) == 0
        assert rejected == 1

    def test_missing_name_rejected(self):
        products = [_make_product(name='')]
        records, rejected = transform_batch(products)
        assert len(records) == 0
        assert rejected == 1

    def test_calories_over_limit_rejected(self):
        products = [_make_product(calories=1500.0)]
        records, rejected = transform_batch(products)
        assert len(records) == 0
        assert rejected == 1

    def test_negative_calories_rejected(self):
        products = [_make_product(calories=-5.0)]
        records, rejected = transform_batch(products)
        assert len(records) == 0
        assert rejected == 1

    def test_non_numeric_nutriment_stored_as_none(self):
        product = _make_product()
        product['nutriments']['proteins_100g'] = 'n/a'
        records, _ = transform_batch([product])
        assert records[0]['protein'] is None

    def test_category_cleaned_correctly(self):
        products = [_make_product(category_tags=['en:soft-drinks', 'en:beverages'])]
        records, _ = transform_batch(products)
        assert records[0]['category'] == 'soft drinks'

    def test_duplicate_barcodes_in_batch_deduped(self):
        products = [_make_product(barcode='AAA'), _make_product(barcode='AAA')]
        records, rejected = transform_batch(products)
        assert len(records) == 1
        assert rejected == 1

    def test_empty_batch_returns_empty(self):
        records, rejected = transform_batch([])
        assert records == []
        assert rejected == 0


class TestCleanCategory:
    def test_strips_language_prefix(self):
        assert _clean_category(['en:beverages']) == 'beverages'

    def test_replaces_dashes_with_spaces(self):
        assert _clean_category(['en:soft-drinks']) == 'soft drinks'

    def test_none_on_empty_tags(self):
        assert _clean_category([]) is None

    def test_none_on_none_input(self):
        assert _clean_category(None) is None
