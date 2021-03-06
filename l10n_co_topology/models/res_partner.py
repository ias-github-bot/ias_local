# -*- coding: utf-8 -*-
##############################################################################
#
#    Ingeniería, Aplicaciones y Software S.A.S
#    Copyright (C) 2003-2017 Tiny SPRL (<http://www.ias.com.co>).
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
import logging

from odoo import _, api, exceptions, fields, models

_logger = logging.getLogger(__name__)


class ResPartnerCode(models.Model):
    _inherit = "res.partner"

    @api.model
    def _get_default_country(self):
        country = self.env[
            'res.country'].search([('code', '=', 'CO')], limit=1)
        return country

    country_id = fields.Many2one(
        'res.country', string='Country', ondelete='restrict',
        default=_get_default_country, track_visibility='onchange')
    municipality_id = fields.Many2one(
        'res.country.municipality',
        string='Municipality', track_visibility='onchange')
    sector_id = fields.Many2one(
        comodel_name='res.country.sector',
        string='Main Sector',
        track_visibility='onchange')
    secondary_sector_ids = fields.Many2one(
        comodel_name='res.country.sector',
        string="Secondary Sectors",
        domain="[('parent_id', '=', sector_id)]",
        track_visibility='onchange')
