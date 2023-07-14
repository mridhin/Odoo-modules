from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    company_display_address = fields.Char(
        compute='_compute_company_display_address', string='Company Address')
    
#    taxpayer_is_vat_registered = fields.Boolean()
    #taxpayer_remarks = fields.Char(compute='_get_tin_info', readonly=True)
    #taxpayer_identification_number = fields.Char()
    #taxpayer_info = fields.Char(compute='_get_tin_info', readonly=True)

    awb_pos_provider_id = fields.Many2one('res.partner', string='POS Provider')
    awb_pos_provider_street = fields.Char('POS Provider Street')
    awb_pos_provider_street2 = fields.Char('POS Provider Street 2')
    awb_pos_provider_state_id = fields.Many2one(
        'res.country.state', string='POS Provider State')
    awb_pos_provider_country_id = fields.Many2one(
        'res.country', string='POS Provider Country')
    awb_pos_provider_tin = fields.Char('POS Provider TIN')
    awb_pos_provider_accreditation_no = fields.Char(
        'POS Provider Accreditation No.')
    awb_pos_provider_date = fields.Date('POS Provider Date')
    awb_pos_provider_valid_until = fields.Date('POS Provider Valid Until')
    awb_pos_provider_display_address = fields.Char(
        compute='_compute_awb_pos_provider_display_address', string='POS Provider Address')
    awb_pos_provider_display_date = fields.Char(
        compute='_compute_awb_pos_provider_display_date', string='Provider Display Date')
    awb_pos_provider_display_valid_until = fields.Char(
        compute='_compute_awb_pos_provider_display_date', string='Provider Display Date')

    @api.depends('city', 'state_id', 'zip')
    def _compute_company_display_address(self):
        for record in self:
            _temp_display_address = ''
            _temp_display_address += record.city if record.city else ''
            _temp_display_address += f', {record.state_id.name}' if (_temp_display_address and record.state_id.name) else (record.state_id.name or '')
            _temp_display_address += f', {record.zip}' if (_temp_display_address and record.zip) else (record.zip or '')
            record.company_display_address = _temp_display_address

    @api.depends('awb_pos_provider_date', 'awb_pos_provider_valid_until')
    def _compute_awb_pos_provider_display_date(self):
        """
            We need this to reformat the default date format 'YYYY-MM-DD' displayed in the POS Order Receipt
            The display format generated in this compute functions is 'MM-DD-YYYY'
        """
        for record in self:
            record.awb_pos_provider_display_date = record.awb_pos_provider_date.strftime(
                '%m/%d/%Y') if record.awb_pos_provider_date else ''
            record.awb_pos_provider_display_valid_until = record.awb_pos_provider_valid_until.strftime(
                '%m/%d/%Y') if record.awb_pos_provider_valid_until else ''

    @api.depends('awb_pos_provider_street', 'awb_pos_provider_street2', 'awb_pos_provider_state_id', 'awb_pos_provider_country_id')
    def _compute_awb_pos_provider_display_address(self):
        for record in self:
            record.awb_pos_provider_display_address = ''
            _display_address = ''
            _display_address += self.awb_pos_provider_street if self.awb_pos_provider_street else ''
            _display_address += f', {self.awb_pos_provider_street2}' if (
                _display_address and self.awb_pos_provider_street2) else (self.awb_pos_provider_street2 or '')
            _display_address += f', {self.awb_pos_provider_state_id.name}' if (
                _display_address and self.awb_pos_provider_state_id.name) else (self.awb_pos_provider_state_id.name or '')
            _display_address += f', {self.awb_pos_provider_country_id.name}' if (
                _display_address and self.awb_pos_provider_country_id.name) else (self.awb_pos_provider_country_id.name or '')
            record.awb_pos_provider_display_address = _display_address


    #check if tin is present else taxpayer_info is blank
#    @api.depends('taxpayer_is_vat_registered', 'taxpayer_identification_number')
    #def _get_tin_info(self):
        #for record in self:
            #if record.taxpayer_is_vat_registered:
                #if record.taxpayer_identification_number:
                    #record.taxpayer_info = 'VAT Registered TIN: ' + \
                        #record.taxpayer_identification_number
                    #record.taxpayer_remarks = ''
                #else:
                    #record.taxpayer_info = ''
                    #record.taxpayer_remarks = ''
            #else:
                #if record.taxpayer_identification_number:
                    #record.taxpayer_info = 'NON-VAT Registered TIN: ' + \
                        #record.taxpayer_identification_number
                    #record.taxpayer_remarks = 'THIS DOCUMENT IS NOT VALID FOR CLAIM OF INPUT TAX'
                #else:
                    #record.taxpayer_info = ''
                    #record.taxpayer_remarks = ''
class ResPartner(models.Model):
    _inherit= "res.partner"

    bus_style = fields.Char(string= "Bus Style")