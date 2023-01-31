from odoo import api, fields, models


class HotelOrder(models.Model):
    _name = 'hotel.order'
    _description = 'Product order food'

    name = fields.Many2one('hotel.room', string='Room')
    guest_name = fields.Many2one(related='name.guest_name', string='Guest')
    time = fields.Datetime(default=fields.Datetime.now(), string='Time')
    category_ids = fields.Many2many('hotel.food.category', string='Category')
    food_ids = fields.Many2many('hotel.food', string='Available Items')
    food_id = fields.One2many('hotel.food', 'order_id',  string='Orders')
    state = fields.Selection([('order','order'),('draft','draft')],default='draft')
    c = fields.Integer()
    food = fields.Char()
    booking_id = fields.Many2one('hotel.booking', string='Order Person')
    name1 = fields.Char(string="Sequence Number", readonly=True, required=True,
                       copy=False, default='NEW')

    @api.onchange('food_ids')
    def _onchange_food_ids(self):
            list = [(5, 0, 0)]
            food = self.env['hotel.food'].search([('id1', '=', self.name.id),
                                                  ('id2', '=', self.guest_name.id),
                                                 ('state', '=', 'order')])
            for x in food:
                val = {
                    'name': x.name,
                    'price': x.price,
                    'description': x.description,
                    'quantity': x.quantity,
                    'sub_total_price': x.sub_total_price
                       }
                list.append((0, 0, val))
            self.update({'food_id': list})
            booking = self.env['hotel.booking'].search([('partner_id', '=', self.guest_name.id)])
            for rec in booking:
                rec.update({'food_id': list})
                rec.order_ref = self.name1



    @api.onchange('category_ids')
    def _onchange_category_ids(self):
      for x in self:
        list = [(5, 0, 0)]
        for record in self.category_ids:
         foods = self.env['hotel.food'].search(
                     [('category_ids', '=', record.name)])
         for rec in foods:

            val = {
                    'id1': x.name,
                    'id2': x.guest_name,
                    'name': rec.name,
                    'price': rec.price,
                    'description': rec.description,
                    'order_id': self.name.id,

                  }
            list.append((0, 0, val))
        x.update({'food_ids': list})

    @api.model
    def create(self, vals):
        vals['name1'] = self.env['ir.sequence'].next_by_code('hotel.order')
        result = super(HotelOrder, self).create(vals)
        return result





class HotelFood(models.Model):
    _name = 'hotel.food'
    _description = 'hotel Product'

    name = fields.Char(string='Name')
    image = fields.Binary(string='Image', attachment=True, readonly=False)
    description = fields.Text(string='Description')
    category_ids = fields.Many2many('hotel.food.category')
    price = fields.Integer(string='Unit price')
    notes = fields.Text(string='Notes')
    quantity = fields.Integer(string='Quantity')
    order_id = fields.Many2one('hotel.order', string='Orders')
    sub_total_price = fields.Integer(string='Subtotal price')
    booking_id = fields.Many2one('hotel.booking', string='Order Person')
    id1 = fields.Integer()
    id2 = fields.Integer()
    state = fields.Selection([('unorder', 'Unorder'), ('order', 'Order')],
                             default='unorder', string='State')

    @api.onchange('quantity', 'price')
    def _onchange_sub_total_price(self):
        for record in self:
            record.sub_total_price = record.price * record.quantity

    def action_add_to_list(self):
        self.state = 'order'

class HotelFoodCategory(models.Model):
    _name = 'hotel.food.category'
    _description = 'hotel Product'

    name = fields.Char(string='Category')













    #extras = fields.Char(string='Extras')




#@api.onchange('category')
 #   def _compute_category(self):
  #      for record in self:
   #         list = [(5,0,0)]
    #        foods = self.env['hotel.food'].search(
     ##      for rec in foods:
       #        val={
        #           'food_id':rec.id,
         #          'quantity':1,
          #         'price': rec.price,
           #        'image': rec.image
            #   }
             #  list.append((0,0,val))
            #record.update({'food_order_id':list})

 #@api.onchange('category_ids')
    #def _onchange_category(self):
        # for record in self.category_ids:
            #return {'domain': {
                     #   'food_id': [('category_ids', '=', record.name)]}}

#return {'domain': {'food_id': [('category', '=', record.category)]}}