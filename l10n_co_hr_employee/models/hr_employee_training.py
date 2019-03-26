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


class HrOrientationTraining(models.Model):
    _name = 'hr.employee.training'
    _rec_name = 'program_name'
    _description = "Employee Training"
    _inherit = ['mail.thread']

    program_name = fields.Char(string='Training Program', required=True)
    program_department = fields.Many2one('hr.department',
                                         string='Department', required=True)
    program_convener = fields.Many2one('res.users',
                                       string='Responsible User',
                                       size=32, required=True)
    training_id = fields.One2many('hr.employee',
                                  string='Employee Details',
                                  compute="employee_details")
    note_id = fields.Text('Description')
    company_id = fields.Many2one('res.company',
                                 string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    user_id = fields.Many2one('res.users',
                              string='users',
                              default=lambda self: self.env.user)
    state = fields.Selection([
        ('new', 'New'),
        ('confirm', 'Confirmed'),
        ('complete', 'Completed'),
    ], string='Status', readonly=True,
       copy=False, index=True, track_visibility='onchange', default='new')

    @api.onchange('program_department')
    def employee_details(self):
        data = self.env['hr.employee'].search(
            [('department_id', '=', self.program_department.id)])
        self.training_id = data

    @api.multi
    def complete_event(self):
        user_obj = self.env.user
        if user_obj == self.program_convener.user_id:
            self.write({'state': 'complete'})

    @api.multi
    def confirm_event(self):
        self.write({'state': 'confirm'})

    @api.multi
    def confirm_send_mail(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference(
                'hr_employee_orientation', 'orientation_training_mailer')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(
                'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'employee.training',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        })

        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }