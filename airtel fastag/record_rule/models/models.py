# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, date


class team_leader(models.Model):
    _inherit = "stock.picking"

    rs_teamleader = fields.Char(string="Team leader")
    rs_reassign = fields.Char(string="Reassign To",
                              compute="_onchange_transfer")
    rs_citymanager = fields.Char(string="City Mnager",
                                 compute='_onchange_mngdestination')
    balance_count = fields.Integer(string="Balance Fastags", store=True)
    ft_user_id = fields.Many2one('res.users', string="Select User")
    ft_user_count = fields.Integer(string="Available Fastag", readonly=True)
    current_user = fields.Boolean('is current user ?',
                                  compute='_get_current_user')
    product_circle = fields.Many2many('rs.circle.name',
                                      string="Available Circles")
    em_user = fields.Boolean()
    product_count = fields.Text(string="Product Count", readonly=True)
    product_categ_count = fields.Text(string="Product category Count",
                                      readonly=True)
    avail_category_ids = fields.Many2many('product.category',
                                          string="Available Categories")

    @api.depends('rs_destination_id')
    def _get_current_user(self):
        if self.env.user.id == self.rs_destination_id.id:
            self.current_user = True
        else:
            self.current_user = False

    @api.onchange('rs_user_id')
    def _onchange_cirlename(self):
        user_id = self.env['res.users'].search(
            [('id', '=', self.rs_user_id.id)])
        if user_id.rs_designation == 'em':
            self.em_user = True
            listids = []
            if user_id.rs_circle_ids:
                for each in user_id.rs_circle_ids:
                    listids.append(each.id)
                domain = {'product_circle': [('id', 'in', listids)]}
                return {'domain': domain, 'value': {'product_circle': []}}

    @api.onchange('product_circle')
    def _onchange_product_circle(self):
        print(self.product_circle)
        list = ""
        for rec in self.product_circle:
            count = self.env['product.template'].search_count(
                [('circle_name', '=', rec.name)])
            product_count = "%s-%s," % (rec.name, count)
            list = list + product_count
        self.product_count = list

    @api.onchange('avail_category_ids')
    def _onchange_avail_category_ids(self):
        list = ""
        for rec in self.avail_category_ids:
            print(rec.id)
            count = self.env['product.template'].search_count(
                [('categ_id', '=', rec.name)])
            product_count = "%s-%s," % (rec.name, count)
            list = list + product_count
        self.product_categ_count = list

    # @api.onchange('move_ids_without_package')
    # def _compute_bal_fastag(self):
    #     # for rec in self:
    #     balance_c = 0
    #     records = self.env['product.template'].search([])
    #     # if pic:
    #     balance_c = len(records.ids)
    #     self.balance_count = balance_c

    @api.onchange('move_ids_without_package')
    def _compute_bal_fastag(self):
        records = self.env['product.template'].search_count([])
        balance_c = len(self.move_ids_without_package)
        records = records - balance_c
        self.balance_count = records
        list = self.move_ids_without_package
        for rec in list:
            user = self.env['res.users'].search(
                [('login', '=', rec.emp_mobile_no)])
            # if user.rs_promoter == True:
            #     records = self.env['product.template'].sudo().search_count(
            #         [('warehouse_emp_no', '=', rec.emp_mobile_no)])
            #     if records > 100:
            #         raise UserError("Promoter fastag count is greaterthan 100")
            #     elif len(self.move_ids_without_package) >100 - records:
            #         raise UserError("you can transfer only fastag")
            #     up_rec = records + balance_c
            #     if up_rec >100:
            #         raise UserError("Promoter fastag count is greaterthan 100")

    # @api.onchange('rs_destination_id')
    # def _onchange_destination(self):
    #     x = self.rs_destination_id
    #     if x.rs_tl.name:
    #       self.rs_teamleader = x.rs_tl.name
    #     else:
    #         self.rs_teamleader = "null"
    # @api.onchange('rs_destination_id')
    # def _onchange_destination(self):
    #     x = self.rs_destination_id
    #     if x.rs_promoter == True:
    #         records = self.env['product.template'].search_count(
    #             [('warehouse_emp_no', '=', x.login)])
    #         if records > 100:
    #             raise UserError("Promoter fastag count is greaterthan 100")

    @api.onchange('rs_destination_id')
    def _onchange_mngdestination(self):
        x = self.rs_destination_id
        if x.rs_cm.name:
            self.rs_citymanager = x.rs_cm.name
        else:
            self.rs_citymanager = "null"

    @api.onchange('state')
    def _onchange_transfer(self):
        if self.state == 'cancel':
            self.rs_reassign = self.rs_user_id.name
        else:
            self.rs_reassign = 'null'

    # def action_cancel(self):
    #     self.rs_state = "cancel"
    #     for move in self.move_ids_without_package:
    #         product_id = move.sudo().product_id
    #         product_id.product_tmpl_id.sudo().update(
    #     {'warehouse_emp_no': self.rs_user_id.rs_employee_id,
    #      'product_assigned_to': self.rs_user_id,
    #      'assigned_to_mob': self.rs_user_id.login})
    #
    #     res = super(team_leader, self).action_cancel()
    #     return res

    # def action_cancel(self):
    #     self.rs_state = "cancel"
    #     for move_id in self.move_ids_without_package:
    #         product_id = move_id.sudo().product_id.product_tmpl_id
    #         query = """UPDATE product_template
    #                                SET warehouse_emp_no = %(number)s,
    #                                    assigned_to_mob = %(mobile)s,
    #                                    product_assigned_to = %(assign)s
    #                                 WHERE id = %(name)s """
    #         self.sudo().env.cr.execute(query, {'name': product_id.id,
    #                                            'number': self.sudo().rs_user_id.rs_employee_id,
    #                                            'mobile': self.sudo().rs_user_id.login,
    #                                            'assign': self.sudo().rs_user_id.id
    #                                            })
    #     res = super(team_leader, self).action_cancel()
    #     return res
    def action_cancel(self):
        self.rs_state = "cancel"
        items = []

        for move_id in self.move_ids_without_package:
            product_id = move_id.sudo().product_id.product_tmpl_id
            values = {'name': product_id.id,
                      'number': self.sudo().rs_user_id.rs_employee_id,
                      'mobile': self.sudo().rs_user_id.login,
                      'assign': self.sudo().rs_user_id.id}
            items.append(values)

        print("=====", items)

        query = """UPDATE product_template
                                   SET warehouse_emp_no = %(number)s,
                                       assigned_to_mob = %(mobile)s,
                                       product_assigned_to = %(assign)s
                                    WHERE id = %(name)s """
        self.sudo().env.cr.executemany(query, items)

        delete_unacknowledged_sql = """DELETE FROM unacknowledged_report WHERE rs_barcode IN (SELECT fatag_bracode FROM stock_move WHERE picking_id = %(id)s)"""

        self.sudo().env.cr.execute(delete_unacknowledged_sql, {'id': self.id}
                                   )

        res = super(team_leader, self).action_cancel()
        return res

    def action_updtate_report(self):
        today = date.today()
        lst_date = str(today).split("-")
        today = lst_date[2] + "/" + lst_date[1] + "/" + lst_date[0]
        insert_transfer_report_records = []
        ids = []
        first_move_id = 0
        last_move_id = 0
        for move_id in self.move_ids_without_package:
            if move_id.sudo().product_id.product_tmpl_id.barcode == "607569-005-4846509":
                first_move_id = move_id.id
            if move_id.sudo().product_id.product_tmpl_id.barcode == "607569-005-4846538":
                last_move_id = move_id.id
        for move_id in range(first_move_id, last_move_id + 1):
            ids.append(move_id)
        move_obj = self.env['stock.move'].search([('id','in',ids)])
        for move_id in move_obj:
            product_id = move_id.sudo().product_id.product_tmpl_id
            insert_transfer_report_values = {'name': product_id.barcode,
                                                 'rs_date_dispatch': today,
                                                 'assigned_id': self.sudo().rs_destination_id.id,
                                                 'rs_date_transfer': today,
                                                 'rs_from_emp_no': self.rs_user_id.rs_employee_id,
                                                 'rs_to_emp_no': self.sudo().rs_destination_id.rs_employee_id
                                                 }
            insert_transfer_report_records.append(insert_transfer_report_values)
        insert_transfer_report_sql = """INSERT INTO transfer_report(name, rs_date_dispatch, assigned_id, 
        rs_date_transfer, rs_from_emp_no, rs_to_emp_no) VALUES (%(name)s, %(rs_date_dispatch)s, %(assigned_id)s, 
        %(rs_date_transfer)s, %(rs_from_emp_no)s, %(rs_to_emp_no)s)"""

        self.env.cr.executemany(insert_transfer_report_sql,
                                insert_transfer_report_records)
    def action_confirm(self):
        self.rs_state = "ackw"
        today = date.today()
        lst_date = str(today).split("-")
        today = lst_date[2] + "/" + lst_date[1] + "/" + lst_date[0]

        update_product_template_records = []
        delete_all_transfer_records = []
        insert_all_transfer_records = []
        insert_transfer_report_records = []

        # for move_id in self.move_ids_without_package:
        #     product_id = move_id.sudo().product_id.product_tmpl_id
        #
        #     product_update_values = {'name': product_id.id,
        #                              'number': self.sudo().rs_destination_id.rs_employee_id,
        #                              'mobile': self.sudo().rs_destination_id.login,
        #                              'assign': self.sudo().rs_destination_id.id,
        #                              'internal': self.sudo().name,
        #                              'circle': move_id.circle_name.id}
        #
        #     update_product_template_records.append(product_update_values)
        #
        #     delete_all_transfer_values = {'name': product_id.barcode}
        #     delete_all_transfer_records.append(delete_all_transfer_values)
        #
            # insert_all_transfer_values = {'name': product_id.barcode,
            #                               'rs_assigned_id': self.sudo().rs_destination_id.id,
            #                               'rs_designation': self.rs_destination_id.rs_designation,
            #                               'rs_assi_date': today,
            #                               'rs_emp_no': self.rs_user_id.rs_employee_id,
            #                               'rs_to_emp_no': self.sudo().rs_destination_id.rs_employee_id,
            #                               'rs_circle': move_id.circle_name.id,
            #                               'rs_tag_sold': move_id.fastag_sold,
            #                               'rs_fault_tags': move_id.rs_faulty_stag,
            #                               'rs_unlinked': move_id.unlink_fastag,
            #                               'rs_balance_stock': 0,
            #                               'rs_name': self.name}
            # insert_all_transfer_records.append(insert_all_transfer_values)
        #
            # insert_transfer_report_values = {'name': product_id.barcode,
            #                                  'rs_date_dispatch': today,
            #                                  'assigned_id': self.sudo().rs_destination_id.id,
            #                                  'rs_date_transfer': today,
            #                                  'rs_from_emp_no': self.rs_user_id.rs_employee_id,
            #                                  'rs_to_emp_no': self.sudo().rs_destination_id.rs_employee_id
            #                                  }
            # insert_transfer_report_records.append(insert_transfer_report_values)


        # product_template_sql = """UPDATE product_template SET warehouse_emp_no = %(number)s, assigned_to_mob = %(mobile)s, product_assigned_to = %(assign)s,internal_ref = %(internal)s,
        #                                circle_name = %(circle)s  WHERE id = %(name)s """
        # self.sudo().env.cr.executemany(product_template_sql,
        #                                update_product_template_records)
        # delete_all_transfer_sql = """DELETE FROM all_transfer_report WHERE name = %(name)s"""
        #
        # self.sudo().env.cr.executemany(delete_all_transfer_sql,
        #                                delete_all_transfer_records)
        #
        # insert_transfer_report_sql = """INSERT INTO all_transfer_report ( name, rs_assigned_id, rs_designation, rs_assi_date, rs_emp_no, rs_to_emp_no, rs_circle, rs_tag_sold,
        #             rs_fault_tags,rs_unlinked,rs_balance_stock,rs_name) VALUES (%(name)s, %(rs_assigned_id)s, %(rs_designation)s, %(rs_assi_date)s, %(rs_emp_no)s, %(rs_to_emp_no)s, %(rs_circle)s, %(rs_tag_sold)s, %(rs_fault_tags)s, %(rs_unlinked)s, %(rs_balance_stock)s, %(rs_name)s)"""
        #
        # self.env.cr.executemany(insert_transfer_report_sql,
        #                         insert_all_transfer_records)
        #
        # insert_transfer_report_sql = """INSERT INTO transfer_report(name, rs_date_dispatch, assigned_id, rs_date_transfer, rs_from_emp_no, rs_to_emp_no) VALUES (%(name)s, %(rs_date_dispatch)s, %(assigned_id)s, %(rs_date_transfer)s, %(rs_from_emp_no)s, %(rs_to_emp_no)s)"""
        #
        # self.env.cr.executemany(insert_transfer_report_sql,
        #                         insert_transfer_report_records)
        # select_product_sql = """SELECT product_id FROM stock_move WHERE picking_id = %(id)s"""
        #
        # self.env.cr.execute(select_product_sql,
        #                     {'id': self.id}
        #                     )
        # product_ids = self.env.cr.fetchall()
        # product_list = []
        # for rec in product_ids:
        #     product_list.append(rec[0])
        # print(product_list[1:-1])
        # select_product_barcode_sql = """SELECT barcode FROM product_product WHERE id IN %(id)s"""
        #
        # self.env.cr.execute(select_product_barcode_sql,
        #                     {'id': (222246,222247)}
        #                     )
        # barcodes = self.env.cr.fetchall()
        #
        # select_product_tmpl_sql = """SELECT fastag_sold,rs_faulty_stag,unlink_fastag,barcode FROM
        # product_template pt LEFT JOIN product_product pp ON pt.id = pp.product_tmple_id
        # WHERE pp.product_tmpl_id IN (SELECT product_tmpl_id FROM product_product WHERE id IN %(id)s )"""
        # self.env.cr.execute(select_product_tmpl_sql,
        #                     {'id': product_ids}
        # #                     )
        # product_tmpl_ids = self.env.cr.fetchall()
        product_template_sql = """UPDATE stock_picking SET rs_assi_date=%(today)s  WHERE id = %(id)s"""

        self.sudo().env.cr.execute(product_template_sql,
                                   {   'today': today,
                                       'id': self.id
                                    })

        product_template_sql = """UPDATE product_template SET warehouse_emp_no = %(number)s, 
        assigned_to_mob = %(mobile)s, product_assigned_to = %(assign)s,internal_ref = %(internal)s,
        circle_name = %(circle)s  WHERE id IN (SELECT product_tmpl_id FROM
        product_product WHERE id IN (SELECT product_id FROM stock_move WHERE picking_id = %(id)s))"""

        self.sudo().env.cr.execute(product_template_sql,
                                       {'id': self.id,
                                        'number': self.sudo().rs_destination_id.rs_employee_id,
                                        'mobile': self.sudo().rs_destination_id.login,
                                        'assign': self.sudo().rs_destination_id.id,
                                        'internal': self.sudo().name,
                                        'circle': self.rs_circle_id.id})

        delete_all_transfer_sql = """DELETE FROM all_transfer_report WHERE name IN (SELECT fatag_bracode FROM stock_move WHERE picking_id = %(id)s)"""

        self.sudo().env.cr.execute(delete_all_transfer_sql,{'id': self.id}
                                       )

        delete_unacknowledged_sql = """DELETE FROM unacknowledged_report WHERE rs_barcode IN (SELECT fatag_bracode FROM stock_move WHERE picking_id = %(id)s)"""

        self.sudo().env.cr.execute(delete_unacknowledged_sql, {'id': self.id}
                                   )

        self.sudo().env.cr.execute("""INSERT INTO all_transfer_report ( name, rs_assigned_id, rs_circle, rs_tag_sold,
            rs_fault_tags,rs_unlinked,rs_name,rs_designation,rs_to_emp_no,rs_emp_no,rs_assi_date,tag_class) 
                                        SELECT sm.fatag_bracode, st.rs_destination_id,
                                         sm.circle_name, sm.fastag_sold,sm.rs_faulty_stag,sm.unlink_fastag,
                                         st.name,rd.rs_designation,rd.rs_employee_id,rs.rs_employee_id,st.rs_assi_date,pt.categ_id
                                        FROM stock_picking st INNER JOIN stock_move sm ON sm.picking_id = st.id 
                                        INNER JOIN res_users rd ON rd.id = st.rs_destination_id
                                        INNER JOIN product_product pp ON pp.barcode = sm.fatag_bracode
                                        INNER JOIN product_template pt ON pp.product_tmpl_id = pt.id
                                        INNER JOIN res_users rs ON rs.id = st.rs_user_id WHERE st.id = %s
                                        
                                        """%(self.id))

        self.sudo().env.cr.execute("""INSERT INTO transfer_report
                                    (name, rs_date_dispatch, assigned_id, rs_date_transfer, rs_from_emp_no, rs_to_emp_no) 
                                                SELECT sm.fatag_bracode,st.rs_assi_date,st.rs_destination_id,st.rs_assi_date,rs.rs_employee_id,rd.rs_employee_id
                                                FROM stock_picking st INNER JOIN stock_move sm ON sm.picking_id = st.id INNER JOIN res_users rd ON rd.id = st.rs_destination_id
                                                INNER JOIN res_users rs ON rs.id = st.rs_user_id WHERE st.id = %s
                                                """ % (self.id))
        # for rec in product_tmpl_ids:
        #     insert_all_transfer_values = {
        #                                   'rs_tag_sold': rec[0],
        #                                   'rs_fault_tags': rec[1],
        #                                   'rs_unlinked': rec[2],
        #                                   'name': rec[3]
        #                                     }
        #     insert_all_transfer_records.append(insert_all_transfer_values)
        # insert_transfer_report_sql = """INSERT INTO all_transfer_report ( name, rs_assigned_id, rs_designation, rs_assi_date,
        #  rs_emp_no, rs_to_emp_no, rs_circle, rs_tag_sold,
        #     rs_fault_tags,rs_unlinked,rs_balance_stock,rs_name) VALUES (%(name)s, %s,
        #      %s, %s, %s, %s, %s,
        #     %(rs_tag_sold)s, %(rs_fault_tags)s, %(rs_unlinked)s, %s, %s)""",(self.sudo().rs_destination_id.id,
        #                                                                                                 self.rs_destination_id.rs_designation,today,
        #                                                                                                 self.rs_user_id.rs_employee_id,
        #                                                                                                 self.sudo().rs_destination_id.rs_employee_id,
        #                                                                                                 self.rs_circle_id.id,0,self.name
        #                                                                                                 )
        #
        # self.env.cr.executemany(insert_transfer_report_sql,
        #                         insert_all_transfer_records)
        #
        # # insert_transfer_report_sql = """INSERT INTO transfer_report(name, rs_date_dispatch, assigned_id, rs_date_transfer, rs_from_emp_no, rs_to_emp_no) VALUES (%(name)s, %(rs_date_dispatch)s, %(assigned_id)s, %(rs_date_transfer)s, %(rs_from_emp_no)s, %(rs_to_emp_no)s)"""
        # #
        # # self.env.cr.executemany(insert_transfer_report_sql,
        # #                         insert_transfer_report_records)

        res = super(team_leader, self).action_confirm()
        return res

    @api.onchange('ft_user_id')
    def _onchange_ft_user_id(self):
        self.ft_user_count = 0

    def action_find_fastag(self):
        records = self.env['product.template'].sudo().search_count(
            [('warehouse_emp_no', '=', self.ft_user_id.login)])
        self.ft_user_count = records

    def action_declined(self):
        self.rs_state = "declined"
        self.state = "cancel"
        items = []
        for move_id in self.move_ids_without_package:
            product_id = move_id.sudo().product_id.product_tmpl_id
            values = {'name': product_id.id,
                      'number': self.sudo().rs_user_id.rs_employee_id,
                      'mobile': self.sudo().rs_user_id.login,
                      'assign': self.sudo().rs_user_id.id}
            items.append(values)

        print("=====", items)
        print('yyyyyyyyyyyyyyyyyyyyyyyy')

        query = """UPDATE product_template
                                   SET warehouse_emp_no = %(number)s,
                                       assigned_to_mob = %(mobile)s,
                                       product_assigned_to = %(assign)s
                                    WHERE id = %(name)s """
        self.sudo().env.cr.executemany(query, items)

        delete_unacknowledged_sql = """DELETE FROM unacknowledged_report WHERE rs_barcode IN (SELECT fatag_bracode FROM stock_move WHERE picking_id = %(id)s)"""

        self.sudo().env.cr.execute(delete_unacknowledged_sql, {'id': self.id}
                                   )
        print('uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu')