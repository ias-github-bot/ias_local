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
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DATEFORMAT
from openerp.exceptions import UserError
from odoo import models, fields, api, _


class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    employee_id = fields.Many2one('hr.employee', string='Employee')


class SurveyComposeMessage(models.TransientModel):

    _inherit = 'survey.mail.compose.message'

    employee_ids = fields.Many2many('hr.employee', 'wizard_id',
                                    'employee_id', string='Employees')

    public = fields.Selection(selection_add=[('internal', _('Internal'))])

    @api.model
    def default_get(self, fields):
        res = super(SurveyComposeMessage, self).default_get(fields)

        if self._context.get('active_model') == 'hr.employee' and self._context.get('active_ids'):
            res.update({'employee_ids': self._context['active_ids']})

        return res

    @api.onchange('employee_ids')
    def onchange_employee_ids(self):

        emails = ''
        for employee in self.employee_ids:
            if employee.work_email:
                emails += employee.work_email + ','
        self.multi_email = emails

    @api.multi
    def send_mail(self, auto_commit=False):

        for employee in self.employee_ids:
            self.survey_id.write({'employee_id': employee.id})
            employee.write({'survey_ids': [(4, self.survey_id.id)]})

        res = super(SurveyComposeMessage, self).send_mail()
        return res
