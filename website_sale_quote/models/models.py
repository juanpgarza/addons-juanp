# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class website_sale_quote(models.Model):
#     _name = 'website_sale_quote.website_sale_quote'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100