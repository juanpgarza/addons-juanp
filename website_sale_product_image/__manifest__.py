# -*- coding: utf-8 -*-
{
    'name': "website_sale_product_image",

    'summary': """
        mejora en la función de subir múltiples imagenes a los productos""",

    'description': """
        Long description of module's purpose
    """,

    'author': "juanpgarza",
    'website': "http://www.juanpgarza.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Website',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','website_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/product_views.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}