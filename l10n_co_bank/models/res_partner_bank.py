# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    @api.onchange('bank_id')
    def bank_code(self):
        if self.bank_id:
            self.entity_code = self.bank_id.bic
        else:
            self.entity_code = ''

    entity_code = fields.Char('Entity Code', size=4)
    account_type = fields.Selection([
        ('corriente', 'Corriente'),
        ('ahorro', 'Ahorros')
        ], string="Tipo de cuenta", required=True)
