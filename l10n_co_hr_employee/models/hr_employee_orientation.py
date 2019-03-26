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


class HrOrientationEmployee(models.Model):
    _name = 'hr.employee.orientation'
    _description = "Employee Orientation"
    _inherit = ['mail.thread']

    name = fields.Char(string='Employee Orientation',
                       readonly=True, default=lambda self: _('New'))
    employee_name = fields.Many2one('hr.employee',
                                    string='Employee', size=32, required=True)
    department = fields.Many2one('hr.department',
                                 string='Department', required=True)
    date = fields.Date(string="Date", default=fields.Datetime.now)
    responsible_user = fields.Many2one('res.users', string='Responsible User')
    employee_company = fields.Many2one('res.company',
                                       string='Company', required=True,
                                       default=
                                       lambda self: self.env.user.company_id)
    parent_id = fields.Many2one('hr.employee', string='Manager')
    job_id = fields.Many2one('hr.job', string='Job Title')
    orientation_id = fields.Many2one('hr.orientation.checklist',
                                     string='Orientation Checklist',
                                     required=True)
    note_id = fields.Text('Description')
    orientation_line_id = fields.Many2many('hr.orientation.check',
                                           string='Orientation Line')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('complete', 'Completed'),
    ], string='Status', readonly=True, copy=False, index=True,
       track_visibility='onchange', default='draft')

    @api.multi
    def confirm_orientation(self):
        self.write({'state': 'confirm'})
        data = self.env[
            'hr.orientation.check'].search(
                [('relative_field.employee_name.name', '=',
                  self.employee_name.name)])
        for values in self.orientation_line_id:
            self.env['hr.orientation.request'].create({
                'request_name': values.checklist_line_name.line_name,
                'request_orientation': self.id,
                'partner_id': values.checklist_line_user.id,
                'request_date': self.date,
                'request_expected_date': values.expected_date,
                'employee_id': self.employee_name.id,
            })

    @api.multi
    def complete_orientation(self):
        self.write({'state': 'complete'})

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'hr.employee.orientation') or 'New'
            result = super(HrOrientationEmployee, self).create(vals)
            return result

    @api.onchange('orientation_id')
    def orientation_details(self):
        data = self.env[
            'hr.orientation.check'].search(
                [('checklist.checklist_name', '=',
                    self.orientation_id.checklist_name),
                 ('checklist.checklist_department.name', '=',
                    self.department.name)])
        self.orientation_line_id = [(6, 0, [x.id for x in data])]

    @api.onchange('employee_name')
    def get_value(self):
        self.department = self.employee_name.department_id
        self.parent_id = self.employee_name.parent_id
        self.job_id = self.employee_name.job_id