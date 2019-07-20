# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('request', 'Presupuesto Solicitado'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    @api.multi
    def quote_request(self):
        return self.write({'state': 'request'})

    @api.multi
    def print_quotation(self):
        self.filtered(lambda s: s.state in ['draft', 'request']).write({'state': 'sent'})
        return self.env.ref('sale.action_report_saleorder').report_action(self)