#!/usr/bin/env python
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.

import sys
import os
DIR = os.path.abspath(os.path.normpath(os.path.join(__file__,
    '..', '..', '..', '..', '..', 'trytond')))
if os.path.isdir(DIR):
    sys.path.insert(0, os.path.dirname(DIR))

import unittest
from decimal import Decimal
import trytond.tests.test_tryton
from trytond.tests.test_tryton import POOL, DB_NAME, USER, CONTEXT, test_view,\
    test_depends
from trytond.exceptions import UserError
from trytond.transaction import Transaction


class TestProductVariantCase(unittest.TestCase):
    'Test Product Variant module'

    def setUp(self):
        trytond.tests.test_tryton.install_module('product_variant_unique')
        self.template = POOL.get('product.template')
        self.product = POOL.get('product.product')
        self.category = POOL.get('product.category')
        self.uom = POOL.get('product.uom')

    def test0005views(self):
        'Test views'
        test_view('product_variant_unique')

    def test0006depends(self):
        'Test depends'
        test_depends()

    def test0010_unique_variant(self):
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            category, = self.category.create([{
                        'name': 'Test unique variant',
                        }])
            kg, = self.uom.search([('name', '=', 'Kilogram')])
            template, uniq_template = self.template.create([{
                        'name': 'Test variant',
                        'type': 'goods',
                        'list_price': Decimal(1),
                        'cost_price': Decimal(0),
                        'category': category.id,
                        'cost_price_method': 'fixed',
                        'default_uom': kg.id,
                        'products': [],
                        }, {
                        'name': 'Test unique variant',
                        'type': 'goods',
                        'list_price': Decimal(1),
                        'cost_price': Decimal(0),
                        'category': category.id,
                        'cost_price_method': 'fixed',
                        'default_uom': kg.id,
                        'products': [],
                        'unique_variant': True,
                        }])

            products = self.product.create([{
                        'code': '1',
                        'template': template.id,
                        }, {
                        'code': '2',
                        'template': template.id,
                        }])
            self.assertEqual(len(products), 2)
            self.assertEqual(len(template.products), 2)
            self.assertIsNone(template.code)
            self.template.write([template], {'code': '1'})
            self.assertIsNone(template.code)
            self.assertEqual(sorted(p.code for p in products), ['1', '2'])

            with self.assertRaises(UserError) as cm:
                self.product.create([{
                            'code': '1',
                            'template': uniq_template.id,
                            }, {
                            'code': '2',
                            'template': uniq_template.id,
                            }])
            self.assertEqual(cm.exception.message,
                'The Template of the Product Variant must be unique.')

            self.product.delete(uniq_template.products)
            self.product.create([{
                        'code': '1',
                        'template': uniq_template.id,
                        }])
            self.assertEqual(uniq_template.code, '1')

            self.assertEqual(self.template.search([
                        ('code', '=', '1'),
                        ]), [uniq_template])
            self.assertEqual(self.template.search([
                        ('rec_name', '=', '1'),
                        ]), [uniq_template])
            self.template.write([uniq_template], {'code': '2'})
            self.assertEqual(uniq_template.code, '2')
            self.assertEqual(uniq_template.products[0].code, '2')
            with self.assertRaises(UserError) as cm:
                self.product.create([{
                            'code': '3',
                            'template': uniq_template.id,
                            }])
            self.assertEqual(cm.exception.message,
                'The Template of the Product Variant must be unique.')


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
            TestProductVariantCase))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
