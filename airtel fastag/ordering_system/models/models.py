from odoo import models, fields, api, _
from datetime import datetime, date
from odoo.exceptions import UserError


class OrderingSystem(models.Model):
    _name = 'ordering.system'  # MODEL NAME
    _description = 'Here You Can Create Yur OrderId For Product Barcode Request'
    _rec_name = 'name'

    # Fields of the tree view in ordering system

    name = fields.Char(string='Ref No:', copy=False, readonly=True,
                       index=True, default=lambda self: _('New'))  # FIELD OF THE SEQUENCE
    requester_name = fields.Many2one('res.users', string='Requester Name:',
                                     domain=[('rs_designation', '=', 'em')], default=lambda self: self.env.user)
    requester_circle = fields.Many2one('rs.circle.name', string='Requester Circle:')
    requested_date = fields.Date(string='Requested Date:', default=datetime.today(), readonly=True)
    employee_id = fields.Char(string='Employee ID:', related='requester_name.rs_employee_id')
    employee_name = fields.Many2one('res.users', string='Employee Name:',
                                    domain=['|', ('rs_designation', '=', 'fastag_promoter'),
                                            ('rs_designation', '=', 'fastag_tl')])
    # product_name = fields.Char(string='Product Name')
    tag_class = fields.Many2one('product.category', string='Tag Class:')
    tag_count = fields.Char(string='Tag Count:', size=5)
    tag_fulfillment_status = fields.Selection([('requested', 'Requested'), ('transferred', 'Transferred')],
                                              default='requested', string='Tag Fulfillment Status:')
    source_profile = fields.Selection(related='requester_name.rs_designation', string='Source Profile:')
    product_type = fields.Selection([('consu', 'Consumable'), ('service', 'Service'),
                                     ('product', 'Storable Product')], string='Product Type', default='product')
    mobile_no = fields.Char(string='Mobile No:', related='requester_name.login')
    email_id = fields.Char(string='Email ID:', related='requester_name.rs_email')
    address = fields.Char(string='Address To Deliver:', related='requester_name.rs_office_addres')
    state = fields.Char(string="State")
    pin_code = fields.Char(string="Pincode")
    city = fields.Char(string="City")
    reset_button = fields.Boolean()
    reset_button2 = fields.Boolean(default=True)



    @api.model  # SEQUENCE GENERATOR OF THE ORDER ID
    def create(self, vals):
        category_id = self.env['product.category'].search(
            [('id', '=', vals['tag_class'])])
        if category_id.id == 22:
            if int(vals['tag_count']) > 10000:
                raise UserError(
                    _('You can not request more than 10000 barcode for this Tag Class'))
        else:
            if int(vals['tag_count']) > 500:
                raise UserError(
                    _('You can not request more than 500 barcode for this Tag Class'))
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('order.sequence')

        result = super(OrderingSystem, self).create(vals)
        # for rec in result:
        #     category_id = self.env['product.category'].search(
        #         [('id', '=', rec.tag_class.id)])
        #     if category_id.id == 22:
        #         if int(rec.tag_count) > 10000:
        #             raise UserError(
        #                 _('You can not request more than 10000 barcode for this Tag Class'))
        #     else:
        #         if int(rec.tag_count) > 500:
        #             rec.tag_count = ''
        #             raise UserError(
        #                 _('You can not request more than 500 barcode for this Tag Class'))
        return result

    @api.onchange('requester_name')
    def fill_circle(self):
        for rec in self:
            if rec.requester_name.rs_designation == 'em':
                listids = []
                if rec.requester_name.rs_circle_ids:
                    for each in rec.requester_name.rs_circle_ids:
                        listids.append(each.id)
                    domain = {'requester_circle': [('id', 'in', listids)]}
                    return {'domain': domain, 'value': {'requester_circle': []}}

    def action_order_submit(self):  # ACTION FOR SUBMIT BUTTON (will submit the detail, show the message with Order ID)
        # category_id = self.env['product.category'].search(
        #     [('id', '=', self.tag_class.id)])
        # if category_id.id == 22:
        #     if int(self.tag_count) > 10000:
        #         raise Warning(
        #             _('You can not request more than 10000 barcode for this Tag Class'))
        # else:
        #     if int(self.tag_count) > 500:
        #         raise Warning(
        #             _('You can not request more than 500 barcode for this Tag Class'))

        message_id = self.env['message_order.wizard'].create(
            {'message': _(" Your Order Reference Has Been Created! The Order ID is %s", self.name)})
        return {  # return will open wizard window
            'name': _('Thanks For The Barcode Order'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'message_order.wizard',
            'res_id': message_id.id,
            'target': 'new'
        }

    @api.onchange('reset_button')
    def onchange_reset_button(self):
        for rec in self:
            rec.tag_class = False
            rec.tag_count = ''
            rec.requester_circle = False
            rec.reset_button2 = False

    @api.onchange('reset_button2')
    def onchange_reset_button2(self):
        for rec in self:
            rec.reset_button = False
            rec.tag_class = False
            rec.tag_count = ''
            rec.requester_circle = False

    # whatever my_button does

    def action_order_reset(self):  # ACTION FOR RESET BUTTON (it will clear the fields)

        self.tag_class = False
        self.tag_count = ''
        self.requester_circle = False

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, '%s - %s/%s' % (rec.name, rec.requester_circle.name, rec.tag_count)))
        return result


class MessageWizard(models.TransientModel):  # MODEL FOR THE POPUP THROUGH WIZARD
    _name = 'message_order.wizard'

    message = fields.Char('Message', readonly=True, required=True)

    def action_create_order(self):  # ACTION FOR OK BUTTON ON WIZARD
        print('success')
        # return {  # will open the ist view of Order ID
        #     'name': " ",
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'ordering.system',
        #     'view_mode': 'tree',
        #     'target': 'self',
        # }
