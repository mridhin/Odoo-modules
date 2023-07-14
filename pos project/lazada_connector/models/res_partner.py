from odoo import fields, models, api


class LazadaConnectorPartner(models.Model):
    _inherit = 'lazada.connector'
    def get_partner_details(self, address_data,name,partner_type, parent_id = False):
        street = address_data.get('address1', '')
        street2 = address_data.get('address2', '')
        city = address_data.get('city', '')
        zip = address_data.get('post_code', '')
        phone = address_data.get('phone', '')
        mobile = address_data.get('phone2', '')
        country_id = self.env['res.country'].search([('name', '=', address_data.get('country'))])
        if not country_id:
            country_id = self.env['res.country'].create({'name': address_data.get('country')})
        state_id = self.env['res.country.state'].search([('name', '=', address_data.get('address3'))])
        if not state_id:
            state_id = self.env['res.country.state'].create({
                'name': address_data.get('address3'),
                'code': address_data.get('address3'),
                'country_id': country_id.id})
        if partner_type == 'delivery' and parent_id:
            name = address_data.get('first_name', '')
            if address_data.get('last_name'):
                name += ' ' + address_data.get('last_name', '')
            partner_vals = {
                'name': name,
                'type': 'delivery',
                'parent_id':parent_id.id
            }
            delivery_partner_id = self.env['res.partner'].search(
                [('name', '=', name), ('phone', '=', phone), ('mobile', '=', mobile), ('street', '=', street),
                 ('street2', '=', street2), ('city', '=', city), ('state_id', '=', state_id.id), ('zip', '=', zip),
                 ('country_id', '=', country_id.id), ('type', '=', 'delivery'), ('parent_id', '=', parent_id.id)],
                limit=1)
        elif partner_type == 'invoice' and parent_id:
            invoice_partner_id = self.env['res.partner'].search(
                [('name', '=', name), ('phone', '=', phone), ('mobile', '=', mobile), ('street', '=', street),
                 ('street2', '=', street2), ('city', '=', city), ('state_id', '=', state_id.id), ('zip', '=', zip),
                 ('country_id', '=', country_id.id), ('type', '=', 'invoice'), ('parent_id', '=', parent_id.id)],
                limit=1)
            if invoice_partner_id:
                return invoice_partner_id
            name = address_data.get('first_name', '')
            if address_data.get('last_name'):
                name += ' ' + address_data.get('last_name', '')
            partner_vals = {
                'name': name,
                'type': 'invoice',
                'parent_id': parent_id.id
            }
        else:
            partner_id = self.env['res.partner'].search([('phone', '=', str(address_data.get('phone', False)))],
                                                        limit=1)
            if partner_id:
                return partner_id

            partner_vals = {
                'name': name,
                'customer_rank': 1,
            }



        partner_vals.update({
            'phone': address_data.get('phone', ''),
            'mobile': address_data.get('phone2', ''),
            'street': address_data.get('address1'),
            'street2': address_data.get('address2'),
            'city': address_data.get('city'),
            'zip': address_data.get('post_code'),
            'country_id': country_id.id,
            'state_id': state_id.id,
        })
        partner_id = self.env['res.partner'].create(partner_vals)
        return partner_id



