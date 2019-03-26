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
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import UserError


class Transfer(models.Model):
    _name = 'hr.department.transfer'
    _description = 'Departmental Transfer'
    _inherit = ['mail.thread']

    employee_id = fields.Many2one(
        'hr.employee', 'Employee', required=True)
    src_id = fields.Many2one('hr.job', 'From', required=True)
    dst_id = fields.Many2one('hr.job', 'Destination', required=True)
    src_department_id = fields.Many2one(
        'hr.department', related='src_id.department_id',
        string='From Department', store=True)
    dst_department_id = fields.Many2one(
        'hr.department', related='dst_id.department_id',
        store=True, string='Destination Department')
    src_contract_id = fields.Many2one(
        'hr.contract', 'From Contract')
    dst_contract_id = fields.Many2one(
        'hr.contract', 'Destination Contract')
    date = fields.Date('Effective Date', required=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirmed'),
         ('pending', 'Pending'), ('done', 'Done'),
         ('cancel', 'Cancelled')], 'State', default="draft")

    @api.multi
    def _needaction_domain_get(self):
        users_obj = self.env['res.users']
        if users_obj.has_group('hr.group_hr_manager'):
            domain = [('state', '=', 'confirm')]
            return domain
        return False

    @api.multi
    def unlink(self):
        for d_transfer in self:
            if d_transfer.state not in ['draft']:
                raise UserError(
                    _('Unable to Delete Transfer!'
                      'Transfer has been initiated. Either cancel the '
                      'transfer or create another transfer to undo it.'))
        return super(Transfer, self).unlink()

    @api.onchange('employee_id')
    def onchange_employee(self):
        res = {'value': {'src_id': False, 'src_contract_id': False}}
        if self.employee_id:
            self.src_id = self.employee_id.contract_id.job_id.id
            self.src_contract_id = self.employee_id.contract_id.id
            res['domain'] = {
                'src_contract_id': [
                    ('employee_id', '=', self.employee_id.id)]
            }
            return res

    @api.multi
    def effective_date_in_future(self):
        today = datetime.now().date()
        for d_transfer in self:
            effective_date = datetime.strptime(
                d_transfer.date, DEFAULT_SERVER_DATE_FORMAT).date()
            if effective_date <= today:
                return False
        return True

    @api.multi
    def _check_state(self, contract_id, effective_date):
        contract_obj = self.env['hr.contract']
        contract = contract_obj.search([('id', '=', contract_id)])
        if contract.state not in ['draft', 'pending', 'open']:
            raise UserError(_(
                'Warning! '
                'The current state of the contract does '
                'not permit changes.'))
        if contract.date_end:
            date_contract_end = datetime.strptime(
                contract.date_end, DEFAULT_SERVER_DATE_FORMAT)
            date_effective = datetime.strptime(
                effective_date, DEFAULT_SERVER_DATE_FORMAT)
            if date_effective >= date_contract_end:
                raise UserError(_(
                    'Warning! '
                    'The contract end date is on or before the '
                    'effective date of the transfer.'))
        return True

    @api.multi
    def transfer_contract(self, contract_id, job_id, xfer_id, effective_date):
        contract_obj = self.env['hr.contract']
        d_transfer = self.env['hr.department.transfer']
        contract = contract_obj.search([('id', '=', contract_id)])
        transfer = d_transfer.search([('id', '=', xfer_id)])
        data = contract.copy({'job_id': job_id,
                              'date_start': effective_date,
                              'state': 'draft',
                              'message_ids': False,
                              'trial_date_start': False,
                              'trial_date_end': False})
        if data:
            # Set the new contract to the appropriate state
            data.write({'state': 'open'})
            # Terminate the current contract (and trigger appropriate state
            # change)
            date_end = datetime.strptime(
                effective_date, '%Y-%m-%d').date() + relativedelta(days=-1)
            contract.write({'date_end': date_end, 'state': 'pending'})
            # Link to the new contract
            transfer.write({'dst_contract_id': data.id})
        return

    @api.multi
    def confirm(self):
        self.write({'state': 'draft'})
        self.state_confirm()

    @api.multi
    def pending(self):
        if self.effective_date_in_future() and self.state_confirm():
            self.write({'state': 'pending'})

    @api.multi
    def cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def state_confirm(self):
        for d_transfer in self:
            if self._check_state(d_transfer.src_contract_id.id,
                                 d_transfer.date):
                self.write({'state': 'confirm'})
        return True

    @api.multi
    def state_done(self):
        today = datetime.now().date()
        for d_transfer in self:
            if datetime.strptime(d_transfer.date,
                                 DEFAULT_SERVER_DATE_FORMAT).date() <= today:
                if self._check_state(d_transfer.src_contract_id.id,
                                     d_transfer.date):
                    d_transfer.employee_id.write(
                        {'department_id': d_transfer.dst_department_id.id})
                    self.transfer_contract(d_transfer.src_contract_id.id,
                                           d_transfer.dst_id.id, d_transfer.id,
                                           d_transfer.date)
                    d_transfer.write({'state': 'done'})
            else:
                return False
        return True

    @api.model
    def try_pending_department_transfers(self):
        """Completes pending departmental transfers. Called from
        the scheduler."""
        today = datetime.now().date()
        transfers_ids = self.search(
            [('state', '=', 'pending'),
             ('date', '<=', today.strftime(
                 DEFAULT_SERVER_DATE_FORMAT))])
        for transfer in transfers_ids:
            if not transfer.effective_date_in_future():
                transfer.write({'state': 'pending'})
                transfer.state_done()
            return True
