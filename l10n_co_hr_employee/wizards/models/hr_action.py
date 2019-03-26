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
from datetime import datetime


class ActionWizard(models.TransientModel):
    _name = 'hr.infraction.action.wizard'
    _description = 'Choice of Actions for Infraction'

    action_type = fields.Selection([('warning_verbal', 'Verbal Warning'),
                                    ('warning_letter', 'Written Warning'),
                                    ('transfer', 'Transfer'),
                                    ('suspension', 'Suspension'),
                                    ('dismissal', 'Dismissal')], 'Action',
                                   required=True,)
    memo = fields.Text('Notes',)
    new_job_id = fields.Many2one('hr.job', 'New Job')
    xfer_effective_date = fields.Date('Effective Date',)
    effective_date = fields.Date('Effective Date')

    @api.multi
    def create_action(self):
        infraction_id = self._context.get('active_id', False)
        if not infraction_id:
            return False
        vals = {
            'infraction_id': infraction_id,
            'type': self.action_type,
            'memo': self.memo or False,
        }
        action_id = self.env['hr.infraction.action'].create(vals)
        infraction_obj = self.env['hr.infraction']
        imd_obj = self.env['ir.model.data']
        iaa_obj = self.env['ir.actions.act_window']
        infraction_data = infraction_obj.search([('id', '=', infraction_id)])
        if infraction_data['state'] == 'confirm':
            infraction_data.write({'state': 'action'})
        # If the action is a warning create the appropriate record, reference
        # it from the action, and pull it up in the view (in case the user
        # needs to make any changes.
        #
        if self.action_type in ['warning_verbal', 'warning_letter']:
            vals = {
                'name': (self.action_type == 'warning_verbal' and
                         'Verbal' or 'Written') + ' Warning',
                'type': (self.action_type == 'warning_verbal' and
                         'verbal' or 'written'),
                'action_id': action_id.id,
                'date': infraction_data.date,
            }
            warning_id = self.env['hr.infraction.warning'].create(vals)
            action_id.write({'warning_id': warning_id.id})
            return True
        # If the action is a departmental transfer create the appropriate
        # record, reference it from the action, and pull it up in the view
        # (in case the user needs to make any changes.
        #
        elif self.action_type == 'transfer':
            xfer_obj = self.env['hr.department.transfer']

            vals = {'employee_id': infraction_data.employee_id.id,
                    'src_id':
                        infraction_data.employee_id.contract_id.job_id.id,
                    'dst_id': self.new_job_id.id,
                    'src_contract_id':
                        infraction_data.employee_id.contract_id.id,
                    'date': self.xfer_effective_date}
            xfer_id = xfer_obj.create(vals)
            action_id.write({'transfer_id': xfer_id.id})
            return True
        # The action is dismissal. Begin the termination process.
        #
        elif self.action_type == 'dismissal':
            action_id.write({'dismissal': True})
            # End any open contracts
            for contract in infraction_data.employee_id.contract_ids:
                if contract.state not in ['close']:
                    contract.write({'state': 'close',
                                    'date_end': self.effective_date})
            # Set employee state to pending deactivation
            infraction_data.employee_id.toggle_active()
            return True
        return True
