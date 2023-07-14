from odoo import models, fields, api


class pos_session(models.Model):
    _inherit = 'pos.session'

    def _loader_params_res_company(self):
        result = super()._loader_params_res_company()
        result['search_params']['fields'].append('sh_customer_discount')
        return result

    def _loader_params_res_partner(self):
        result = super()._loader_params_res_partner()
        result['search_params']['fields'].append('sh_customer_discount')
        return result

