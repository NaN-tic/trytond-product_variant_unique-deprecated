# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from .product import *


def register():
    Pool.register(
        Template,
        Product,
        module='product_variant_unique', type_='model')
    Pool.register(
        ProductByLocation,
        OpenProductQuantitiesByWarehouse,
        module='product_variant_unique', type_='wizard')
