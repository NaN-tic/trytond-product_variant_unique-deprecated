# This file is part of the product_variant_unique module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class ProductVariantUniqueTestCase(ModuleTestCase):
    'Test Product Variant Unique module'
    module = 'product_variant_unique'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        ProductVariantUniqueTestCase))
    return suite