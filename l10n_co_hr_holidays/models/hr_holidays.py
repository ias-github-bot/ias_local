# -*- coding: utf-8 -*-

from odoo import models, fields


class HrLeave(models.Model):
    _inherit = "hr.leave"

    upload_file = fields.Binary(string="Upload File")
    file_name = fields.Char(string="File Name")
