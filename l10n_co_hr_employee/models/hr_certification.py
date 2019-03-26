# -*- coding: utf-8 -*-
##############################################################################
#
#    Ingeniería, Aplicaciones y Software S.A.S
#    Copyright (C) 2003-2018 Tiny SPRL (<http://www.ias.com.co>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields, api
from datetime import date
from dateutil.relativedelta import relativedelta


class HrCertification(models.Model):
    _name = 'hr.certification'
    _inherit = ['mail.thread', 'hr.curriculum']

    certification = fields.Char(
        string='Certification Number', help='Certification Number')

    state = fields.Selection([
        ('valid', 'Valid'),
        ('to_expire', 'To expire'),
        ('expired', 'Expired')], 'State', track_visibility='onchange',)

    @api.model
    def next_to_expire(self):
        self.search([
            ('expire', '=', '1'),
            ('end_date', '<=', fields.Date.to_string(date.today() + relativedelta(days=60)))]).write(
            {'state': 'to_expire'})

        self.search([
            ('state', 'in', ('valid', 'to_expire')),
            ('end_date', '<=', fields.Date.to_string(date.today() + relativedelta(days=1))),
        ]).write({
            'state': 'expired'
        })

        return True

    @api.multi
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state == 'to_expire':
            return 'l10n_co_hr_employee.mt_certification_to_expire'
        elif 'state' in init_values and self.state == 'expired':
            return 'l10n_co_hr_employee.mt_certification_expired'
        return super(HrCertification, self)._track_subtype(init_values)
