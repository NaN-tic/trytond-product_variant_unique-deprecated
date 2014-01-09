# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import logging
from sql import Literal
from sql.aggregate import Count

from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from trytond.modules.product.product import STATES, DEPENDS

__all__ = ['Template', 'Product', 'ProductByLocation',
    'OpenProductQuantitiesByWarehouse']
__metaclass__ = PoolMeta


class Template:
    __name__ = 'product.template'

    code = fields.Function(fields.Char("Code", states=STATES, depends=DEPENDS),
        'get_code', setter='set_code', searcher='search_code')

    @classmethod
    def __setup__(cls):
        super(Template, cls).__setup__()
        cls.products.size = 1

    @classmethod
    def search_rec_name(cls, name, clause):
        res = super(Template, cls).search_rec_name(name, clause)
        ids = map(int, cls.search([('products.code',) + tuple(clause[1:])],
                order=[]))
        if ids:
            res = ['OR', res, [('id', 'in', ids)]]
        return res

    def get_code(self, name):
        return self.products and self.products[0].code or None

    @classmethod
    def set_code(cls, templates, name, value):
        Product = Pool().get('product.product')

        products = []
        for template in templates:
            if template.products:
                products.append(template.products[0])
            else:
                new_product = Product(template=template, code=value)
                new_product.save()
        if products:
            Product.write(products, {
                    'code': value,
                    })

    @classmethod
    def search_code(cls, name, clause):
        return [('products.code',) + tuple(clause[1:])]


class Product:
    __name__ = 'product.product'

    @classmethod
    def __setup__(cls):
        super(Product, cls).__setup__()

        cursor = Transaction().cursor
        sql_table = cls.__table__()
        cursor.execute(*sql_table.select(sql_table.template, Count(Literal(1)),
                group_by=sql_table.template, having=Count(Literal(1)) > 1))
        if cursor.fetchone():
            logging.getLogger('product_variant_unique').warning(
                "There are templates with more than one variant. Please, "
                "remove these variants or split in different templates and "
                "update this module.")
        else:
            cls._sql_constraints += [
                ('template_uniq', 'UNIQUE (template)',
                    'The Template of the Product Variant must be unique.'),
                ]


class ProductByLocation:
    __name__ = 'product.by_location'

    def do_open(self, action):
        Template = Pool().get('product.template')

        context = Transaction().context
        if context['active_model'] == 'product.template':
            template = Template(context['active_id'])
            if not template.products:
                return None, {}
            product_id = template.products[0].id
            new_context = {
                'active_model': 'product.template',
                'active_id': product_id,
                'active_ids': [product_id],
                }
            with Transaction().set_context(new_context):
                return super(ProductByLocation, self).do_open(action)
        return super(ProductByLocation, self).do_open(action)


class OpenProductQuantitiesByWarehouse:
    __name__ = 'stock.product_quantities_warehouse'

    def do_open_(self, action):
        Template = Pool().get('product.template')

        context = Transaction().context
        if context['active_model'] == 'product.template':
            template = Template(context['active_id'])
            if not template.products:
                return None, {}
            product_id = template.products[0].id
            new_context = {
                'active_model': 'product.template',
                'active_id': product_id,
                'active_ids': [product_id],
                }
            with Transaction().set_context(new_context):
                return super(OpenProductQuantitiesByWarehouse,
                    self).do_open_(action)
        return super(OpenProductQuantitiesByWarehouse, self).do_open_(action)
