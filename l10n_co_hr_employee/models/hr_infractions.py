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
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrInfractionCategory(models.Model):
    _name = 'hr.infraction.category'
    _description = 'Infraction Type'

    name = fields.Char('Name', required=True,)
    code = fields.Char('Code', required=True,)


class HrInfraction(models.Model):
    _name = 'hr.infraction'
    _description = 'Infraction'
    _inherit = ['mail.thread']

    name = fields.Char('Subject', size=256, required=True, readonly=True,
                       states={'draft': [('readonly', False)]},)
    date = fields.Date('Date', required=True, readonly=True,
                       states={'draft': [('readonly', False)]},)
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True,
                                  readonly=True,
                                  states={'draft': [('readonly', False)]},)
    category_id = fields.Many2one('hr.infraction.category', 'Category',
                                  required=True, readonly=True,
                                  states={'draft': [('readonly', False)]},)
    action_ids = fields.One2many('hr.infraction.action', 'infraction_id',
                                 'Actions', readonly=True,)
    memo = fields.Text('Description', readonly=True,
                       states={'draft': [('readonly', False)]},)
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'),
                              ('action', 'Actioned'),
                              ('noaction', 'No Action')],
                             default='draft', string='State', readonly=True,)

    @api.model
    def _needaction_domain_get(self):
        users_obj = self.env['res.users']
        domain = []
        if users_obj.has_group('hr.group_hr_manager'):
            domain = [('state', '=', 'confirm')]
        if len(domain) == 0:
            return False
        return domain

    @api.multi
    def unlink(self):
        for infraction in self:
            if infraction.state not in ['draft']:
                raise UserError(_('Error '
                                  'Infractions that have progressed '
                                  'beyond "Draft" state may not be removed.'))

        return super(HrInfraction, self).unlink()

    @api.onchange('category_id')
    def _onchange_company_id(self):
        res = {'value': {'name': False}}
        if self.category_id:
            res['value']['name'] = self.category_id.name
        return res

    @api.multi
    def confirm(self):
        self.state = 'confirm'

    @api.multi
    def noaction(self):
        self.state = 'noaction'


class HrInfractionAction(models.Model):
    _name = 'hr.infraction.action'
    _description = 'Action Based on Infraction'
    _rec_name = 'type'

    infraction_id = fields.Many2one('hr.infraction', 'Infraction',
                                    ondelete='cascade', required=True,
                                    readonly=True,)
    type = fields.Selection([('warning_verbal', 'Verbal Warning'),
                             ('warning_letter', 'Written Warning'),
                             ('transfer', 'Transfer'),
                             ('suspension', 'Suspension'),
                             ('dismissal', 'Dismissal')], 'Type',
                            required=True,)
    memo = fields.Text('Notes')
    employee_id = fields.Many2one('hr.employee',
                                  related='infraction_id.employee_id',
                                  string='Employee', store=True)
    warning_id = fields.Many2one('hr.infraction.warning', 'Warning',
                                 readonly=True,)
    transfer_id = fields.Many2one('hr.department.transfer', 'Transfer',
                                  readonly=True,)

    @api.multi
    def unlink(self):
        for action in self:
            if action.infraction_id.state not in ['draft']:
                raise UserError(_('Error'
                                  'Actions belonging to Infractions not in '
                                  '"Draft" state may not be removed.'))
        return super(HrInfractionAction, self).unlink()


class HrInfractionWarning(models.Model):
    _name = 'hr.infraction.warning'
    _description = 'Employee Warning'

    name = fields.Char('Subject', required=True)
    date = fields.Date('Date Issued')
    type = fields.Selection([('verbal', 'Verbal'),
                             ('written', 'Written')],
                            string='Type', required=True,  default='written')
    action_id = fields.Many2one('hr.infraction.action', 'Action',
                                ondelete='cascade')
    infraction_id = fields.Many2one('hr.infraction',
                                    related='action_id.infraction_id',
                                    readonly=True, string='Infraction')
    employee_id = fields.Many2one('hr.employee',
                                  related='infraction_id.employee_id',
                                  readonly=True, string='Employee')

    @api.multi
    def unlink(self):
        for warning in self:
            if (warning.action_id.infraction_id.state != 'draft' and
                    warning.action_id):
                raise UserError(_('Error'
                                  'Warnings attached to Infractions not'
                                  ' in "Draft" state may not be removed.'))
        return super(HrInfractionWarning, self).unlink()
