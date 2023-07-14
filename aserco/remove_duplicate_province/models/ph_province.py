import re
from odoo import api, fields, models


class CountryState(models.Model):
    _inherit = 'res.country.state'

    def remove_dup_records(self):
        states = self.sudo().search([('country_id.name','=','Philippines')])
        dup_states = states.filtered(lambda s: len(s.code) <= 4)
        for state in dup_states:
            ori_state = states.filtered(lambda s:len(s.code) > 4 and s.name == state.name)
            if not ori_state:
                dup_states -= state
                continue
            partners = self.env['res.partner'].sudo().search([('state_id','=',state.id)])
            if partners:
                partners.state_id = ori_state
        dup_states.sudo().unlink()

        provinces = self.sudo().search([('country_id.code', '=', 'PH')])
        for province in provinces:
            partner = self.env['res.partner'].search([('state_id','=',province.id)])
            partner.state_id = False
            if not province.city_ids:
                try:
                    province.unlink()
                except():
                    pass


class StateCity(models.Model):
    _inherit = 'res.state.city'

    def remove_number_special_character(self):
        city_code_list = ['101301000','023106000','043403000','042106000','137601000','034917000','043411000','042114000','140117000',
                '097209000','051731000','175324000']

        for city_code in city_code_list:
            city = self.search([('city_code','=',city_code)])
            if city:
                new_name = re.sub('[^A-Za-z()]+ ', '', city.name)
                new_name = new_name.replace("�","")
                new_name = new_name.replace("?", "")
                city.name = new_name

