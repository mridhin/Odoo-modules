from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    taxpayer_is_vat_registered = fields.Boolean()
    taxpayer_remarks = fields.Char(compute='_get_tin_info', readonly=True)
    taxpayer_identification_number = fields.Char()
    taxpayer_info = fields.Char(compute='_get_tin_info', readonly=True)

    #check if tin is present else taxpayer_info is blank
    @api.depends('taxpayer_is_vat_registered', 'taxpayer_identification_number')
    def _get_tin_info(self):
        for record in self:
            if record.taxpayer_is_vat_registered:
                if record.taxpayer_identification_number:
                    record.taxpayer_info = 'VAT Registered TIN: ' + \
                        record.taxpayer_identification_number
                    record.taxpayer_remarks = ''
                else:
                    record.taxpayer_info = ''
                    record.taxpayer_remarks = ''
            else:
                if record.taxpayer_identification_number:
                    record.taxpayer_info = 'NON-VAT Registered TIN: ' + \
                        record.taxpayer_identification_number
                    record.taxpayer_remarks = 'THIS DOCUMENT IS NOT VALID FOR CLAIM OF INPUT TAX'
                else:
                    record.taxpayer_info = ''
                    record.taxpayer_remarks = ''
