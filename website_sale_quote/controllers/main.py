# Copyright 2019 Juan Pablo Garza
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import http
from odoo.http import request
#from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale_checkout_skip_payment.controllers.main import CheckoutSkipPayment


class CheckoutSkipPaymentJPG(CheckoutSkipPayment):

    @http.route()
    def payment(self, **post):
        if not request.website.checkout_skip_payment:
            return super(CheckoutSkipPayment, self).payment(**post)
        order = request.website.sale_get_order()
        request.website.sale_reset()
        return request.redirect('/shop/confirmation')
        # if order.force_quotation_send():
        #     # Clean session, then redirect to the confirmation page
        #     request.website.sale_reset()
        #     return request.redirect('/shop/confirmation')
        # else:
        #     return request.render(
        #         'website_sale_skip_payment.confirmation_order_error')