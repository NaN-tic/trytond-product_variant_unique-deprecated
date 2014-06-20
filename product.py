# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import If, Eval
from trytond.transaction import Transaction
from trytond.modules.product.product import STATES, DEPENDS

__all__ = ['Template', 'Product', 'ProductByLocation',
    'OpenProductQuantitiesByWarehouse']
__metaclass__ = PoolMeta

UNIQUE_STATES = STATES.copy()
UNIQUE_STATES.update({
        'invisible': ~Eval('unique_variant', False)
        })


class Template:
    __name__ = 'product.template'

    unique_variant = fields.Boolean('Unique variant')
    code = fields.Function(fields.Char("Code", states=UNIQUE_STATES,
            depends=DEPENDS + ['unique_variant']),
        'get_code', setter='set_code', searcher='search_code')

    @classmethod
    def __setup__(cls):
        super(Template, cls).__setup__()
        cls.products.size = If(Eval('unique_variant', False), 1, 999999999999)

    @staticmethod
    def default_unique_variant():
        pool = Pool()
        Config = pool.get('product.configuration')
        config = Config.get_singleton()
        if config:
            return config.unique_variant

    @classmethod
    def search_rec_name(cls, name, clause):
        return ['OR', super(Template, cls).search_rec_name(name, clause),
            [('code',) + tuple(clause[1:])]]

    def get_code(self, name):
        if self.unique_variant:
            return self.products and self.products[0].code or None

    @classmethod
    def set_code(cls, templates, name, value):
        Product = Pool().get('product.product')

        products = set()
        for template in templates:
            if not template.unique_variant:
                continue
            if template.products:
                products.add(template.products[0])
            elif value:
                new_product = Product(template=template)
                new_product.save()
                products.add(new_product)
        if products:
            Product.write(list(products), {
                    'code': value,
                    })

    @classmethod
    def search_code(cls, name, clause):
        return [
            ('unique_variant', '=', True),
            ('products.code',) + tuple(clause[1:])]

    @classmethod
    def validate(cls, templates):
        pool = Pool()
        Product = pool.get('product.product')
        products = []
        for template in templates:
            if template.unique_variant and template.products:
                products.append(template.products[0])
        if products:
            Product.validate_unique_template(products)
        super(Template, cls).validate(templates)


class Product:
    __name__ = 'product.product'

    @classmethod
    def __setup__(cls):
        super(Product, cls).__setup__()
        cls._error_messages.update({
                'template_uniq': ('The Template of the Product Variant must '
                    'be unique.'),
                })

    @classmethod
    def validate(cls, products):
        cls.validate_unique_template(products)
        super(Product, cls).validate(products)

    @classmethod
    def validate_unique_template(cls, products):
        unique_products = [p for p in products if p.unique_variant]
        templates = [p.template.id for p in unique_products]
        if len(set(templates)) != len(templates):
            cls.raise_user_error('template_uniq')
        if cls.search([
                    ('id', 'not in', [p.id for p in unique_products]),
                    ('template', 'in', templates),
                    ], limit=1):
            cls.raise_user_error('template_uniq')


class ProductByLocation:
    __name__ = 'product.by_location'

    @classmethod
    def __setup__(cls):
        super(ProductByLocation, cls).__setup__()
        cls._error_messages.update({
                'not_unique_variant': ('The template "%s" must be marked as '
                    'unique variant in order to be able to see it\'s stock'),
                })

    def default_start(self, fields):
        Template = Pool().get('product.template')
        try:
            res = super(ProductByLocation, self).default_start(fields)
        except AttributeError:
            res = {}
        context = Transaction().context
        if context['active_model'] == 'product.template':
            template = Template(context['active_id'])
            if not template.unique_variant:
                self.raise_user_error('not_unique_variant', template.rec_name)
        return res

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

    @classmethod
    def __setup__(cls):
        super(OpenProductQuantitiesByWarehouse, cls).__setup__()
        cls._error_messages.update({
                'not_unique_variant': ('The template "%s" must be marked as '
                    'unique variant in order to be able to see it\'s stock'),
                })

    def default_start(self, fields):
        Template = Pool().get('product.template')
        try:
            res = super(OpenProductQuantitiesByWarehouse, self).default_start(
                fields)
        except AttributeError:
            res = {}
        context = Transaction().context
        if context['active_model'] == 'product.template':
            template = Template(context['active_id'])
            if not template.unique_variant:
                self.raise_user_error('not_unique_variant', template.rec_name)
        return res

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
