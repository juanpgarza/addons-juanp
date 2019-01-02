# -*- coding: utf-8 -*-
from odoo import http

# class WebsiteSaleProductImage(http.Controller):
#     @http.route('/website_sale_product_image/website_sale_product_image/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/website_sale_product_image/website_sale_product_image/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('website_sale_product_image.listing', {
#             'root': '/website_sale_product_image/website_sale_product_image',
#             'objects': http.request.env['website_sale_product_image.website_sale_product_image'].search([]),
#         })

#     @http.route('/website_sale_product_image/website_sale_product_image/objects/<model("website_sale_product_image.website_sale_product_image"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('website_sale_product_image.object', {
#             'object': obj
#         })