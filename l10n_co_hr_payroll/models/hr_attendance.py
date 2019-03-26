from odoo import models, fields, api


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    @api.model
    def create(self, values):
        res = super(HrAttendance, self).create(values)
        employee_id = values['employee_id']
        check_in = values['check_in']
        check_out = values['check_out']
        overtime_ids = self.env[
            'hr.overtime'].search([
                ('employee_id', '=', employee_id),
                ('to_date', '>=', check_in),
                ('from_date', '<=', check_out)])
        if values.get('action') == 'sign_out':
            for ov in overtime_ids:
                actual_leave_time = check_out - check_in
                ov.write({'actual_leave_time': actual_leave_time})
        return res
