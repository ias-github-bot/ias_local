# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    bank_account_id = fields.Many2one('res.partner.bank',
                                      string="Bank Account")
