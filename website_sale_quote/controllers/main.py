# Copyright 2019 Juan Pablo Garza
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import http, _, fields
from odoo.http import request
from odoo.exceptions import AccessError
from odoo.tools import consteq
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import pager as portal_pager, get_records_pager
from odoo.addons.sale.controllers.portal import CustomerPortal
from odoo.addons.website_quote.controllers.main import sale_quote
from odoo.addons.website_sale_checkout_skip_payment.controllers.main import CheckoutSkipPayment

class sale_quote(sale_quote):

    @http.route("/quote/<int:order_id>/<token>", type='http', auth="public", website=True)
    def view(self, order_id, pdf=None, token=None, message=False, **post):
        # use sudo to allow accessing/viewing orders for public user
        # only if he knows the private token
        now = fields.Date.today()
        if token:
            Order = request.env['sale.order'].sudo().search([('id', '=', order_id), ('access_token', '=', token)])
        else:
            Order = request.env['sale.order'].sudo().search([('id', '=', order_id)])
        # Log only once a day
        if Order and request.session.get('view_quote_%s' % Order.id) != now and request.env.user.share:
            request.session['view_quote_%s' % Order.id] = now
            body = _('Quotation viewed by customer')
            _message_post_helper(res_model='sale.order', res_id=Order.id, message=body, token=Order.access_token, message_type='notification', subtype="mail.mt_note", partner_ids=Order.user_id.sudo().partner_id.ids)
        # import pdb; pdb.set_trace()
        # if Order.state == 'request':
        #     values = {
        #     'quotation': Order}
        #     return request.render('website_sale_quote.request_quote_1', values)
        if not Order:
            # import pdb; pdb.set_trace()
            return request.render('website.404')

        # Token or not, sudo the order, since portal user has not access on
        # taxes, required to compute the total_amout of SO.
        order_sudo = Order.sudo()

        days = 0
        if order_sudo.validity_date:
            days = (fields.Date.from_string(order_sudo.validity_date) - fields.Date.from_string(fields.Date.today())).days + 1
        if pdf:
            pdf = request.env.ref('website_quote.report_web_quote').sudo().with_context(set_viewport_size=True).render_qweb_pdf([order_sudo.id])[0]
            pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
            return request.make_response(pdf, headers=pdfhttpheaders)
        transaction_id = request.session.get('quote_%s_transaction_id' % order_sudo.id)
        if not transaction_id:
            Transaction = request.env['payment.transaction'].sudo().search([('reference', '=', order_sudo.name)])
        else:
            Transaction = request.env['payment.transaction'].sudo().browse(transaction_id)
        values = {
            'quotation': order_sudo,
            'message': message and int(message) or False,
            'option': any(not x.line_id for x in order_sudo.options),
            'order_valid': (not order_sudo.validity_date) or (now <= order_sudo.validity_date),
            'days_valid': days,
            'action': request.env.ref('sale.action_quotations').id,
            # 'no_breadcrumbs': request.env.user.partner_id.commercial_partner_id not in order_sudo.message_partner_ids,
            'no_breadcrumbs': False,
            'tx_id': Transaction.id if Transaction else False,
            'tx_state': Transaction.state if Transaction else False,
            'tx_post_msg': Transaction.acquirer_id.post_msg if Transaction else False,
            'payment_tx': Transaction,
            'need_payment': order_sudo.invoice_status == 'to invoice' and Transaction.state in ['draft', 'cancel', 'error'],
            'token': token,
            'return_url': '/shop/payment/validate',
            'bootstrap_formatting': True,
            'partner_id': order_sudo.partner_id.id,
        }

        if order_sudo.require_payment or values['need_payment']:
            domain = expression.AND([
                ['&', ('website_published', '=', True), ('company_id', '=', order_sudo.company_id.id)],
                ['|', ('specific_countries', '=', False), ('country_ids', 'in', [order_sudo.partner_id.country_id.id])]
            ])
            acquirers = request.env['payment.acquirer'].sudo().search(domain)

            values['form_acquirers'] = [acq for acq in acquirers if acq.payment_flow == 'form' and acq.view_template_id]
            values['s2s_acquirers'] = [acq for acq in acquirers if acq.payment_flow == 's2s' and acq.registration_view_template_id]
            values['pms'] = request.env['payment.token'].search(
                [('partner_id', '=', order_sudo.partner_id.id),
                ('acquirer_id', 'in', [acq.id for acq in values['s2s_acquirers']])])

            for acq in values['form_acquirers']:
                acq.form = acq.render('/', order_sudo.amount_total, order_sudo.pricelist_id.currency_id.id,
                    values={
                        'return_url': '/quote/%s/%s' % (order_id, token) if token else '/quote/%s' % order_id,
                        'type': 'form',
                        'alias_usage': _('If we store your payment information on our server, subscription payments will be made automatically.'),
                        'partner_id': order_sudo.partner_id.id,
                    })
        history = request.session.get('my_quotes_history', [])
        values.update(get_records_pager(history, order_sudo))

        # import pdb; pdb.set_trace()
        # 
        if order_sudo.state == 'request':
            return request.render('website_sale_quote.request_quote_1', values)
        else:
            return request.render('website_quote.so_quotation', values)

class CheckoutSkipPaymentJPG(CheckoutSkipPayment):

    @http.route()
    def payment(self, **post):
        if not request.website.checkout_skip_payment:
            return super(CheckoutSkipPayment, self).payment(**post)
        order = request.website.sale_get_order()
        order.quote_request()
        request.website.sale_reset()
        return request.redirect('/shop/confirmation')

        # if order.force_quotation_send():
        #     # Clean session, then redirect to the confirmation page
        #     request.website.sale_reset()
        #     return request.redirect('/shop/confirmation')
        # else:
        #     return request.render(
        #         'website_sale_skip_payment.confirmation_order_error')


class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        SaleOrder = request.env['sale.order']
        quotation_count = SaleOrder.sudo().search_count([
            # ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['sent', 'cancel', 'request'])
        ])
        order_count = SaleOrder.sudo().search_count([
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['sale', 'done'])
        ])
        # import pdb; pdb.set_trace()
        values.update({
            'quotation_count': quotation_count,
            'order_count': order_count,
        })
        return values

    @http.route(['/my/quotes', '/my/quotes/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_quotes(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order']
        # import pdb; pdb.set_trace()
        domain = [
            # ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['sent', 'cancel', 'request'])
        ]

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'date_order desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('sale.order', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        quotation_count = SaleOrder.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/quotes",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=quotation_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        quotations = SaleOrder.sudo().search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        #import pdb; pdb.set_trace()
        request.session['my_quotes_history'] = quotations.ids[:100]

        values.update({
            'date': date_begin,
            'quotations': quotations.sudo(),
            'page_name': 'quote',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/quotes',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("sale.portal_my_quotations", values)