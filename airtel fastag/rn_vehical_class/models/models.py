# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.osv import expression
from odoo.exceptions import ValidationError, Warning, UserError,RedirectWarning
from datetime import datetime, date
import pytz


class VehicalClass(models.Model):
    _name = 'vehical.class'
    _inherit = ['mail.thread']
    _description = 'Vehicle Class'

    name = fields.Char(string="Vendor ID")
    tag_id = fields.Char(string="Tag ID")
    partner_id = fields.Many2one('res.partner', string='Vendor Name',
                                 domain="[('supplier_rank','=',1)]")
    barcode = fields.Char(string='Barcode')
    inword_data = fields.Date(string='Inward Date')
    vehical_type = fields.Char(string='Vehicle Type')
    v_type_id = fields.Char(string='Vehicle Type ID')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm')],
                             default='draft')
    category_id = fields.Many2many('res.partner.category', string="Tag Color")
    rn_category_id = fields.Many2one('product.category',
                                     string="Product Category")

    def action_confirm(self):
        self.state = 'confirm'

    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm')],
                             default='draft')
    category_id = fields.Many2many('res.partner.category', string="Tag Color")
    rn_category_id = fields.Many2one('product.category',
                                     string="Product Category")


class ResPartner(models.Model):
    _inherit = 'res.partner'

    vendor_id = fields.Char(string='Vendor ID')
    partner_id = fields.Char(string="Partner ID")


class StockPicking(models.Model):
    _inherit = "stock.picking"
    _order = "id desc"

    rs_user_id = fields.Many2one('res.users', copy=False, tracking=True,
                                 string='Source Location',
                                 default=lambda self: self.env.user)
    rs_destination_id = fields.Many2one('res.users', copy=False, tracking=True,
                                        string='Assign To')
    rs_office_addres = fields.Text(string="Office Address")
    rs_emp_no = fields.Char(string="Employee No")
    rs_state = fields.Selection(
        [('draft', 'Assign'), ('assign', 'Assign'),
         ('not_ackw', 'Not Acknowledged'),
         ('ackw', 'Acknowledged'), ('declined', 'Declined'),
         ('cancel', 'Cancelled')], string="State", default='draft',
            readonly=True)
    fastag_count = fields.Integer(string="Fastags Count",
                                  compute='get_pro_count')
    fastag_count1 = fields.Integer()
    fastag_sold = fields.Integer(string="Fastags Sold", compute='get_pro_count')
    fastag_faulty = fields.Integer(string="Fastags Faulty",
                                   compute='get_pro_count')
    fastag_trnsfr_date = fields.Char(string="Transfer Date")
    no_fastags = fields.Char(string="No Of Fastag")
    rs_circle = fields.Many2one('rs.circle.name', string="Circle Name")
    rs_circle_id = fields.Many2one('rs.circle.name', string="Circle Name", )
    rs_emp_mob_no = fields.Char(string="Employee No")
    rs_filter_fastag = fields.Boolean(string="Filter Transfer")
    category_id = fields.Many2one('product.category', string="Tag Class")
    circle_list = fields.Many2one('rs.circle.name')
    from_fastags = fields.Char(string='From Fastag')
    to_fastags = fields.Char(string="To Fastag")
    sequence_fastag = fields.Boolean(string="Sequence Transfer")
    product_id_count = fields.Char(string="Product Count")
    select_order_id = fields.Many2one('ordering.system', domain=[
        ('tag_fulfillment_status', '=', 'requested')], string='Select Order ID')
    user_order_id = fields.Many2one('res.users',string="Requester Name")
    user_order_designation = fields.Selection(string="Designation"
                                         , related="user_order_id.rs_designation")
    rs_assi_date = fields.Char(string="Assigned Date")
    order_id_bool = fields.Boolean(compute='order_count')
    @api.depends('select_order_id')
    def order_count(self):
        if self.select_order_id:
            self.order_id_bool = True
            self.no_fastags = self.select_order_id.tag_count
            self.rs_circle = self.select_order_id.requester_circle
            self.rs_emp_mob_no = self.select_order_id.mobile_no
            self.category_id = self.select_order_id.tag_class
        else:
            self.order_id_bool = False

    @api.onchange('user_order_id')
    def _onchange_select_order_id(self):
        order_id = self.env['ordering.system'].search(
            [('requester_name', '=', self.user_order_id.id)])
        listids = []
        for rec in order_id:
            listids.append(rec.id)
        domain = {'select_order_id': [('id', 'in', listids)]}
        return {'domain': domain, 'value': {'select_order_id': []}}

    # @api.onchange('select_order_id')
    # def filter_field_fill(self):
    #     if self.select_order_id:
    #         self.no_fastags = self.select_order_id.tag_count
    #         self.rs_circle = self.select_order_id.requester_circle
    #         self.rs_emp_mob_no = self.select_order_id.mobile_no
    #         self.category_id = self.select_order_id.tag_class
    def product_user_circle(self):

        # delete_all_transfer_sql = """DELETE FROM all_transfer_report WHERE name IN
        # (SELECT barcode FROM product_product pp INNER JOIN product_template pt ON pt.id = pp.product_tmpl_id
        #  WHERE pp.id IN (SELECT product_id FROM stock_move WHERE picking_id = %(id)s ) AND
        #  pt.internal_ref < %(name)s)"""
        # self.sudo().env.cr.execute(delete_all_transfer_sql, {'id': self.id,'name': self.name}
        #                            )

        self.sudo().env.cr.execute("""
        DO $$
        declare
            i varchar;
        BEGIN
            FOR i IN SELECT barcode FROM product_product  WHERE id IN (SELECT product_id FROM stock_move WHERE picking_id = %s)
         LOOP
         IF EXISTS (SELECT id FROM all_transfer_report WHERE name = i) THEN
                 IF  %s >= (SELECT id FROM stock_picking WHERE name =
                 (SELECT internal_ref FROM product_template WHERE id = (SELECT product_tmpl_id FROM product_product WHERE barcode = i))) THEN
                        DELETE FROM all_transfer_report WHERE name = i;
                        INSERT INTO all_transfer_report ( name, rs_assigned_id, rs_circle, rs_tag_sold,
                                    rs_fault_tags,rs_unlinked,rs_name,rs_designation,rs_to_emp_no,rs_emp_no,rs_assi_date)
                                                                SELECT pp.barcode, st.rs_destination_id,
                                                                 sm.circle_name, sm.fastag_sold,sm.rs_faulty_stag,sm.unlink_fastag,
                                                                 st.name,rd.rs_designation,rd.rs_employee_id,rs.rs_employee_id,st.rs_assi_date
                                                                FROM stock_picking st INNER JOIN stock_move sm ON sm.picking_id = st.id
                                                                INNER JOIN product_product pp ON sm.product_id = pp.id
                                                                INNER JOIN res_users rd ON rd.id = st.rs_destination_id
                                                                INNER JOIN res_users rs ON rs.id = st.rs_user_id WHERE st.id = %s AND pp.barcode = i;

            END IF;
            ELSE
            INSERT INTO all_transfer_report ( name, rs_assigned_id, rs_circle, rs_tag_sold,
                                    rs_fault_tags,rs_unlinked,rs_name,rs_designation,rs_to_emp_no,rs_emp_no,rs_assi_date)
                                                                SELECT pp.barcode, st.rs_destination_id,
                                                                 sm.circle_name, sm.fastag_sold,sm.rs_faulty_stag,sm.unlink_fastag,
                                                                 st.name,rd.rs_designation,rd.rs_employee_id,rs.rs_employee_id,st.rs_assi_date
                                                                FROM stock_picking st INNER JOIN stock_move sm ON sm.picking_id = st.id
                                                                INNER JOIN product_product pp ON sm.product_id = pp.id
                                                                INNER JOIN res_users rd ON rd.id = st.rs_destination_id
                                                                INNER JOIN res_users rs ON rs.id = st.rs_user_id WHERE st.id = %s AND pp.barcode = i;
            END IF;
            END LOOP;
            END $$;
                                                        """ % (self.id,self.id,self.id,self.id))

        # self.sudo().env.cr.execute("""
        #  DO $$
        #  declare
        #      i varchar;
        #      J varchar;
        #
        # BEGIN
        #     FOR i IN SELECT DISTINCT(rs_name) FROM all_transfer_report WHERE name is null
        #     LOOP
        #         FOR J IN SELECT barcode FROM product_product WHERE id IN
        #         (SELECT product_id FROM stock_move WHERE picking_id = (SELECT id FROM stock_picking WHERE name = i))
        #         LOOP
        #          IF EXISTS (SELECT id FROM all_transfer_report WHERE name = J) THEN
        #          IF  (SELECT id FROM stock_picking WHERE name = i) >= (SELECT id FROM stock_picking WHERE name =
        #          (SELECT internal_ref FROM product_template WHERE id = (SELECT product_tmpl_id FROM product_product WHERE barcode = j))) THEN
        #                 DELETE FROM all_transfer_report WHERE name = j;
        #                 INSERT INTO all_transfer_report ( name, rs_assigned_id, rs_circle, rs_tag_sold,
        #                             rs_fault_tags,rs_unlinked,rs_name,rs_designation,rs_to_emp_no,rs_emp_no,rs_assi_date)
        #                                                         SELECT pp.barcode, st.rs_destination_id,
        #                                                          sm.circle_name, sm.fastag_sold,sm.rs_faulty_stag,sm.unlink_fastag,
        #                                                          st.name,rd.rs_designation,rd.rs_employee_id,rs.rs_employee_id,st.rs_assi_date
        #                                                         FROM stock_picking st INNER JOIN stock_move sm ON sm.picking_id = st.id
        #                                                         INNER JOIN product_product pp ON sm.product_id = pp.id
        #                                                         INNER JOIN res_users rd ON rd.id = st.rs_destination_id
        #                                                         INNER JOIN res_users rs ON rs.id = st.rs_user_id WHERE st.name = i AND pp.barcode = j;
        #
        #             END IF;
        #             ELSE
        #     INSERT INTO all_transfer_report ( name, rs_assigned_id, rs_circle, rs_tag_sold,
        #                             rs_fault_tags,rs_unlinked,rs_name,rs_designation,rs_to_emp_no,rs_emp_no,rs_assi_date)
        #                                                         SELECT pp.barcode, st.rs_destination_id,
        #                                                          sm.circle_name, sm.fastag_sold,sm.rs_faulty_stag,sm.unlink_fastag,
        #                                                          st.name,rd.rs_designation,rd.rs_employee_id,rs.rs_employee_id,st.rs_assi_date
        #                                                         FROM stock_picking st INNER JOIN stock_move sm ON sm.picking_id = st.id
        #                                                         INNER JOIN product_product pp ON sm.product_id = pp.id
        #                                                         INNER JOIN res_users rd ON rd.id = st.rs_destination_id
        #                                                         INNER JOIN res_users rs ON rs.id = st.rs_user_id WHERE st.name = i AND pp.barcode = i;
        #             END IF;
        #             END LOOP;
        #             END LOOP;
        #             END $$;
        #                                                         """ )

        # self.sudo().env.cr.execute("""INSERT INTO transfer_report
        #                                     (name, rs_date_dispatch, assigned_id, rs_date_transfer, rs_from_emp_no, rs_to_emp_no)
        #                                     SELECT pp.barcode,st.rs_assi_date,st.rs_destination_id,st.rs_assi_date,rs.rs_employee_id,rd.rs_employee_id
        #                                     FROM stock_picking st INNER JOIN stock_move sm ON sm.picking_id = st.id
        #                                     INNER JOIN product_product pp ON sm.product_id = pp.id
        #                                     INNER JOIN res_users rd ON rd.id = st.rs_destination_id
        #                                     INNER JOIN res_users rs ON rs.id = st.rs_user_id WHERE st.id = %s
        #                                                 """ % (self.id))
    # def count_user_destination(self):
    #     users = self.env['res.users'].search([])
    #     print("===",users)
    #     group_id = self.env.ref('stock.group_stock_user')
    #     for user in users:
    #         group_id.write({'users': [(4, user.id)]})
    # def product_update(self):
    #     update_pro = self.env['all.transfer.report'].search(
    #         [('rs_name', '=', 'WH/OUT/00408')])
    #     print('=============',update_pro)
    #     for rec in update_pro:
    #         product = self.env['product.template'].search(
    #              [('barcode', '=', rec.name)])
    #         query = """UPDATE product_template
    #                     SET warehouse_emp_no = 'A1YHHI90',
    #                         assigned_to_mob = Null,
    #                         product_assigned_to = Null
    #                      WHERE id = %(name)s """
    #         self.env.cr.execute(query, {'name': product.id
    #                                     })

    # def product_user_circle(self):
    #     move_line = self.move_ids_without_package
    #     user_id = self.env['res.users'].search(
    #         [('id', '=', self.rs_destination_id.id)])
    #     if user_id.rs_designation == 'em':
    #         for rec in move_line:
    #             product_id = rec.product_id
    #             product_tem_id = self.env['product.template'].search(
    #                 [('barcode', '=', product_id.barcode)])
    #             product_tem_id.write({'circle_name': rec.circle_name,
    #                                   'categ_id': 7})
    #             product_id.write({'circle_name': rec.circle_name,
    #                               'categ_id': 7})
    #     else:
    #         for rec in move_line:
    #             product_id  = rec.product_id
    #             product_tem_id = self.env['product.template'].search([('barcode','=',product_id.barcode)])
    #             product_tem_id.write({'circle_name': user_id.rs_circle,
    #                               'categ_id': 7})
    #             product_id.write({'circle_name': user_id.rs_circle,
    #                               'categ_id':7})
    #             # query = """DELETE FROM all_transfer_report WHERE id = %(name)s"""
    #             # self.env.cr.execute(query, {'name': list_bar[l]
    #             #                             })

    # @api.onchange('rs_user_id')
    # def stata_ackw(self):
    #     picking_id = self.search([('rs_state','=','assign'),('rs_destination_id','=',self.env.user.id)])
    #     if picking_id:
    #         raise UserError(
    #             _('You cannot create transfer,having assigned transfer'))

    # @api.model
    # def report_update(self):
    #     print('abcddddddddddddddddddddddddddddddddddddddddd')
    #     transfer_id = self.env['transfer.report']
    #     all_transfer_id = self.env['all.transfer.report']
    #     # time = fields.Datetime.now(default=lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'))
    #     now = datetime.strftime(
    #         fields.Datetime.context_timestamp(self, datetime.now()),
    #         "%Y-%m-%d %H:%M:%S")
    #     print('timeeeeeeeeeeeeeeeee',now)
    #     # picking_id = self.search([])
    #     query = """SELECT * FROM stock_picking WHERE scheduled_date > (%(now)s::timestamp - INTERVAL '10 MINUTES')"""
    #     self.env.cr.execute(query,{'now': now
    #                                             })
    #     picking_ids = self.env.cr.fetchall()
    #     print('picking',picking_ids)
    #     trans_list = []
    #     all_transfer_lst = []
    #     today = date.today()
    #     lst_date = str(today).split("-")
    #     today = lst_date[2] + "/" + lst_date[1] + "/" + lst_date[0]
    #     for record in picking_ids:
    #         picking_id = self.search([('id','=',record[0])])
    #         print('pickingggggggggggggggggggggggggggggggg',picking_id)
    #         print('move',self.move_ids_without_package)
    #         for rec in picking_id.move_ids_without_package:
    #             user_id = self.env['res.users'].search(
    #                 [('login', '=', rec.emp_mobile_no)])
    #             if user_id:
    #                 print('scheduled action++++++++++++++++++++++++++++++')
    #                 query = """DELETE FROM all_transfer_report WHERE name = %(name)s"""
    #                 self.env.cr.execute(query, {'name': rec.fatag_bracode
    #                                             })
    #                 trans_list.append({'name': rec.fatag_bracode,
    #                                    'rs_date_dispatch': today,
    #                                    'assigned_id': user_id.id,
    #                                    'rs_date_transfer': today,
    #                                    'rs_from_emp_no': picking_id.rs_user_id.rs_employee_id,
    #                                    'rs_to_emp_no': user_id.rs_employee_id,
    #                                    })
    #                 all_transfer_lst.append({'name': rec.fatag_bracode,
    #                                          'rs_assigned_id': user_id.id,
    #                                          'rs_designation': user_id.rs_designation,
    #                                          'rs_assi_date': today,
    #                                          'rs_emp_no': picking_id.rs_user_id.rs_employee_id,
    #                                          'rs_to_emp_no': user_id.rs_employee_id,
    #                                          'rs_circle': rec.circle_name.id,
    #                                          'rs_tag_sold': rec.fastag_sold,
    #                                          'rs_fault_tags': rec.rs_faulty_stag,
    #                                          'rs_unlinked': rec.unlink_fastag,
    #                                          'rs_balance_stock': 0,
    #                                          'rs_name': rec.picking_id.name
    #                                          })
    #                 print('scheculed action report sucess=========================================')
    #         transfer_id.sudo().create(trans_list)
    #         all_transfer_id.sudo().create(all_transfer_lst)

    # def transfer_circle_update(self):
    #     # transfer_id = self.search([('rs_circle_id', '=', False)])
    #     # print("================================",transfer_id)
    #     # for rec in transfer_id:
    #     #     move_id = rec.move_ids_without_package
    #     #     for move in move_id:
    #     #         rec.sudo().update({'rs_circle_id': move.circle_name.id})
    #     query = """SELECT id FROM stock_picking WHERE rs_circle_id IS NULL"""
    #     self.env.cr.execute(query)
    #     picking_id = self.env.cr.fetchall()
    #     print('picking=============================',picking_id)

    # def _compute_barcode(self):
    #     from_bar = self.from_fastags
    #     from_first = from_bar[0:5]
    #     from_sec = from_bar[6:8]
    #     from_thr = from_bar[9:]
    #     self.from_fastags = "%s-%s-%s" % (from_first, from_sec, from_thr)
    #     to_bar = self.to_fastags
    #     to_first = to_bar[0:5]
    #     to_sec = to_bar[6:8]
    #     to_thr = to_bar[9:]
    #     self.to_fastags = "%s-%s-%s" % (to_first, to_sec, to_thr)
    @api.onchange('rs_user_id')
    def onchange_product_id_count(self):
        product_ids = self.env['product.template'].search_count(
            [])
        if product_ids:
            self.product_id_count = product_ids
            print("conttttttttttttttt",self.product_id_count)
        else:
            self.product_id_count = ""

    def transfer_update(self):
        self.sudo().env.cr.execute("""INSERT INTO transfer_report
                                                    (name, rs_date_dispatch, assigned_id, rs_date_transfer, rs_from_emp_no, rs_to_emp_no)
                                                    SELECT pp.barcode,st.rs_assi_date,st.rs_destination_id,st.rs_assi_date,rs.rs_employee_id,rd.rs_employee_id
                                                    FROM stock_picking st INNER JOIN stock_move sm ON sm.picking_id = st.id
                                                    INNER JOIN product_product pp ON sm.product_id = pp.id
                                                    INNER JOIN res_users rd ON rd.id = st.rs_destination_id
                                                    INNER JOIN res_users rs ON rs.id = st.rs_user_id WHERE st.id = %s
                                                                """ % (self.id))
        # delete_all_transfer_sql = """DELETE FROM all_transfer_report WHERE name is null """
        # self.sudo().env.cr.execute(delete_all_transfer_sql)
        # delete_transfer_sql = """DELETE FROM transfer_report WHERE name is null """
        # self.sudo().env.cr.execute(delete_transfer_sql)

    def transfer_delete(self):
        delete_transfer_sql = """DELETE FROM transfer_report WHERE id IN (SELECT id FROM transfer_report WHERE name is null LIMIT 1500) """
        self.sudo().env.cr.execute(delete_transfer_sql)

    def all_transfer_delete(self):
        delete_all_transfer_sql = """DELETE FROM all_transfer_report WHERE name is null """
        self.sudo().env.cr.execute(delete_all_transfer_sql)

    def unlink(self):
        self.env['all.transfer.report'].sudo().search(
            [('rs_name', '=', self.name)]
        ).unlink()
        now = datetime.strftime(
            fields.Datetime.context_timestamp(self, datetime.now()),
            "%Y-%m-%d %H:%M:%S")
        list = []
        for move in self.move_ids_without_package:
            list.append((0, 0, {'product_barcode': move.product_id.barcode
                                }))

        self.env['transfer.details'].sudo().create(
            {'name': self.env.user.id,
             'date': now,
             'transfer_name': self.name,
             'fastag_count': self.fastag_count,
             'fastag_details_ids': list
             })
        return super(StockPicking, self).unlink()

    @api.onchange('rs_filter_fastag')
    def _onchange_circledomain(self):
        print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        user_id = self.env['res.users'].search(
            [('id', '=', self.rs_user_id.id)])
        if user_id.rs_designation == 'em':
            listids = []
            if user_id.rs_circle_ids:
                for each in user_id.rs_circle_ids:
                    listids.append(each.id)
                    print(each.id)
                res = {}
                res['domain'] = {'rs_circle': [('id', 'in', listids)]}
                return res
        # else:
        #     res = {}
        #     res['domain'] = {'rs_circle': [('id', '=', user_id.rs_circle_id.id)]}
        #     return res

    # def get_serial_wise_barcode(self):
    #     # product_ids = self.env['product.product'].search(
    #     #     [('warehouse_emp_no', '=', self.env.user.rs_employee_id)])
    #     # print("===", product_ids, self.env.user.rs_employee_id, self.no_fastags,
    #     #       type(str(len(product_ids))))
    #     if self.rs_destination_id:
    #         raise UserError(
    #             _('Allredy assign transfer,If you want to transfer please click on "Create" Button'))
    #     if self.no_fastags == False:
    #         raise UserError(
    #             _('You can not create blank transfer please enter number of fastags greater then Zero'))
    #     # if int(self.no_fastags) > len(product_ids):
    #         raise UserError(
    #             _('Number of fastags less than selected fastag, Now %s fastags available !',
    #               str(len(product_ids))))
    #     else:
    #         list_barcode = []
    #         #circle mismatch
    #         user_id = self.env['res.users'].search(
    #             [('login', '=', self.rs_emp_mob_no)])
    #         user_em_id = self.env['res.users'].search(
    #             [('id', '=', self.rs_user_id.id)])
    #         if user_em_id.rs_designation == 'em':
    #             if self.rs_circle.id != user_id.rs_circle.id:
    #                 raise UserError(
    #                     'Mismatching circle name'
    #                 )
    #
    #         #circle count
    #             count = self.env['product.template'].search_count(
    #                 [('circle_name', '=', self.rs_circle.id)])
    #             if int(self.no_fastags) > count:
    #                 raise UserError(
    #                     _('Number of fastag is less than in the available circle %s ,Now only %s fastag is available !',
    #                       self.rs_circle.name, count))
    #         #tag class count
    #             count = self.env['product.template'].search_count(
    #                 [('categ_id', '=', self.category_id.id)])
    #             if int(self.no_fastags) > count:
    #                 raise UserError(
    #                     _('Number of fastag is less than in the available category %s ,Now only %s fastag is available !',
    #                       self.category_id.name, count))
    #
    #         # promoter restriction
    #         if user_id.rs_designation == 'fastag_promoter':
    #             records = self.env['product.template'].sudo().search_count(
    #                 [('warehouse_emp_no', '=', user_id.rs_employee_id)])
    #
    #             fastags_needed = int(records) + int(self.no_fastags)
    #             # print("=====fastags_needed===",fastags_needed,int(records),int(self.no_fastags))
    #             if int(fastags_needed) > 100:
    #                 raise UserError(
    #                     _('Promoter %s Already there are %s FASTag you can assign %s !',
    #                       user_id.name, int(records), int(records) - 100))
    #         # TL Restriction
    #         if user_id.rs_designation == 'fastag_tl':
    #             records = self.env['product.template'].sudo().search_count(
    #                 [('warehouse_emp_no', '=', user_id.rs_employee_id)])
    #
    #             fastags_needed = int(records) + int(self.no_fastags)
    #             print("=====fastags_needed===", fastags_needed, int(records),
    #                   int(self.no_fastags))
    #             if int(fastags_needed) > 1000:
    #                 raise UserError(
    #                     _('TL %s Already there are %s FASTag you can assign only %s !',
    #                       user_id.name, int(records), int(records) - 1000))
    #
    #         product_count = self.env['product.template'].search_count([])
    #         print('product count',product_count)
    #         # product unlink
    #         unlink_count = self.env['product.template'].search_count(
    #             [('unlink_fastag', '=', True)])
    #         unlink_pro = product_count - unlink_count
    #         if int(self.no_fastags) > unlink_pro:
    #             raise UserError(
    #                 _('Only %s fastag is available',
    #                    unlink_pro))
    #
    #         # product sold
    #         sold_count = self.env['product.template'].search_count(
    #             [('fastag_sold', '=', 'yes')])
    #         sold_pro = product_count - sold_count
    #         if int(self.no_fastags) > sold_pro:
    #             raise UserError(
    #                 _('Only %s fastag is available',
    #                   sold_pro))
    #
    #         #product faulty
    #         fault_count = self.env['product.template'].search_count(
    #             [('rs_faulty_stag', '=', 'yes')])
    #         fault_pro = product_count - fault_count
    #         if int(self.no_fastags) > fault_pro:
    #             raise UserError(
    #                 _('Only %s fastag is available',
    #                   fault_pro))
    #
    #         if self.env.user.id == 2061:
    #             product = self.env['product.product'].search(
    #                 [('warehouse_emp_no', '=', self.env.user.rs_employee_id),
    #                  ('fastag_sold', '=', 'no'), ('rs_faulty_stag', '=', 'no'),
    #                  ('unlink_fastag', '=', False)])
    #             if len(product) >= int(self.no_fastags):
    #                 for product_id in product[
    #                                   :int(self.no_fastags)]:
    #                     self.env['stock.move'].sudo().create(
    #                         {'picking_id': self.id, 'product_id': product_id.id,
    #                          'name': product_id.name,
    #                          'fatag_bracode': product_id.barcode,
    #                          'category_id': product_id.categ_id.id,
    #                          'circle_name': self.rs_circle.id,
    #                          'emp_mobile_no': self.rs_emp_mob_no,
    #                          'location_id': 1,
    #                          'product_uom': 1,
    #                          'location_dest_id': 1})
    #
    #                     # product_id.sudo().write({'internal_ref': self.name})
    #                     product_id.product_tmpl_id.sudo().update(
    #                         {'warehouse_emp_no': None})
    #                     #      'assigned_to_mob': user_id.login,
    #                     #      'product_assigned_to': user_id.id,
    #                     #      'internal_ref': self.name})
    #                     self.sudo().update({'rs_destination_id': user_id.id,
    #                                         'rs_emp_no': self.rs_emp_mob_no,
    #                                         'rs_circle_id': self.rs_circle.id
    #                                         })
    #             template = self.env.ref(
    #                 'rn_vehical_class.inventory_trasfer_assigned_email_template')
    #             self.env['mail.template'].browse(template.id).send_mail(
    #                 self.id)
    #         else:
    #             if user_id:
    #                 # avail_circle_product = self.env['product.product'].search(
    #                 #     [(
    #                 #      'warehouse_emp_no', '=', self.env.user.rs_employee_id),
    #                 #      ('circle_name', '=', self.rs_circle.id),
    #                 #      ('fastag_sold', '=', 'no'),
    #                 #      ('rs_faulty_stag', '=', 'no'),
    #                 #      ('unlink_fastag', '=', False)])
    #                 query = """
    #                                                                                                                SELECT *
    #                                                                                                             FROM product_product pp
    #                                                                                                             LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
    #                                                                                                             WHERE pt.circle_name = %(circle)s AND pt.warehouse_emp_no = %(emp)s
    #                                                                                                             AND pt.categ_id = %(categ)s
    #                                                                                                             AND pt.fastag_sold = 'no' AND pt.rs_faulty_stag = 'no' AND pt.unlink_fastag IS NOT TRUE
    #                                                                                                             order by pt.id asc    """
    #
    #                 self.env.cr.execute(query,
    #                                     {'circle': self.rs_circle.id,
    #                                      'emp': self.env.user.rs_employee_id,
    #                                      'categ': self.category_id.id
    #                                      })
    #                 avail_circle_product = self.env.cr.fetchall()
    #
    #                 if len(avail_circle_product) >= int(self.no_fastags):
    #                     for product_id in avail_circle_product[
    #                                       :int(self.no_fastags)]:
    #                         stock = self.env['stock.move'].sudo().create({})
    #                         query1 = """UPDATE stock_move SET picking_id=%(picking_id)s,
    #
    #                                                                       product_id=%(product_id)s,
    #                                                                       name=%(name)s,
    #                                                                       fatag_bracode = %(fatag_bracode)s,
    #                                                                         category_id=%(category_id)s,
    #                                                                         circle_name=%(circle_name)s,
    #                                                                         emp_mobile_no=%(emp_mobile_no)s,
    #                                                                         location_id=%(location_id)s,
    #                                                                         product_uom=%(product_uom)s,
    #                                                                         location_dest_id=%(location_dest_id)s
    #                                                                         WHERE id = %(id)s
    #                                              """
    #                         self.env.cr.execute(query1, {
    #                             'picking_id': self.id,
    #                              'product_id': product_id[0],
    #                              'name': product_id[1],
    #                              'fatag_bracode': product_id[4],
    #                              'category_id': product_id[24],
    #                              'circle_name': self.rs_circle.id,
    #                              'emp_mobile_no': self.rs_emp_mob_no,
    #                              'location_id': 1,
    #                              'product_uom': 1,
    #                              'location_dest_id': 1,
    #                             'id':stock.id
    #                             })
    #                         # self.env['stock.move'].sudo().create(
    #                         #     {'picking_id': self.id,
    #                         #      'product_id': product_id[0],
    #                         #      'name': product_id[1],
    #                         #      'fatag_bracode': product_id[4],
    #                         #      'category_id': product_id[25],
    #                         #      'circle_name': self.rs_circle.id,
    #                         #      'emp_mobile_no': self.rs_emp_mob_no,
    #                         #      'location_id': 1,
    #                         #      'product_uom': 1,
    #                         #      'location_dest_id': 1})
    #
    #                         # product_id.sudo().write({'internal_ref': self.name})
    #                         # product_id.product_tmpl_id.sudo().update(
    #                         #     {'warehouse_emp_no': user_id.rs_employee_id,
    #                         #      'assigned_to_mob': user_id.login,
    #                         #      'product_assigned_to': user_id.id,
    #                         #      'internal_ref': self.name})
    #                         query = """
    #                      UPDATE product_template
    #                     SET warehouse_emp_no = Null,
    #                     product_assigned_to = %(assign)s
    #                     WHERE id = (SELECT product_tmpl_id
    #                                         FROM product_product WHERE id=%(product_id)s)
    #                                                                         """
    #
    #
    #                         self.env.cr.execute(query,
    #                                             {'product_id': product_id[0],
    #                                              'assign': user_id.id
    #                                              })
    #                         # product_id.product_tmpl_id.sudo().update(
    #                         #     {'warehouse_emp_no': None})
    #                         self.sudo().update({'rs_destination_id': user_id.id,
    #                                             'rs_emp_no': self.rs_emp_mob_no,
    #                                             'rs_circle_id': self.rs_circle.id
    #                                             })
    #                 else:
    #                     raise UserError(
    #                         _('No available fastag',
    #                           ))
    #                 template = self.env.ref(
    #                     'rn_vehical_class.inventory_trasfer_assigned_email_template')
    #                 self.env['mail.template'].browse(template.id).send_mail(self.id)
    #
    #             else:
    #                 raise UserError(_('Please Check Employee Mobile Number'))
    #     return True
    # def get_serial_wise_barcode(self):
    #     if self.rs_destination_id:
    #         raise UserError(
    #             _('Already assign transfer,If you want to transfer please click on "Create" Button'))
    #     else:
    #         user_id = self.env['res.users'].search(
    #             [('login', '=', self.rs_emp_mob_no)])
    #
    #         # circle mismatch
    #         user_em_id = self.env['res.users'].search(
    #             [('id', '=', self.rs_user_id.id)])
    #         if user_em_id.rs_designation == 'em':
    #             if self.rs_circle.id != user_id.rs_circle.id:
    #                 raise UserError(
    #                     'Mismatching circle name'
    #                 )
    #
    #         update_transfer_records = []
    #         update_product_id = []
    #         no_product = []
    #
    #         if self.env.user.id == 2061:
    #             if user_id:
    #
    #                 avail_circle_product = self.env['product.product'].search(
    #                     [
    #                         ('fastag_sold', '=', 'no'),
    #                         ('rs_faulty_stag', '=', 'no'),
    #                         ('unlink_fastag', '=', False),
    #                         ('categ_id', '=', self.category_id.id),
    #                         ('warehouse_emp_no', '=',
    #                          self.env.user.rs_employee_id)])
    #
    #                 if self.sequence_fastag == True:
    #                     if self.from_fastags == False:
    #                         raise UserError(
    #                             _('You can not create blank transfer Please enter beginning barcode .'))
    #                     if self.to_fastags == False:
    #                         raise UserError(
    #                             _('You need to provide end range of barcode .'))
    #
    #                     not_avail_circle_product = self.env[
    #                         'product.product'].search(
    #                         ['|','|',('fastag_sold', '=', 'yes'),
    #                             ('rs_faulty_stag', '=', 'yes'),
    #                             ('unlink_fastag', '=', True),
    #                             ])
    #
    #                     all_product = self.env['product.product'].search(
    #                         [('categ_id', '=', self.category_id.id),
    #                             ('warehouse_emp_no', '=',
    #                              self.env.user.rs_employee_id)])
    #
    #                     all_product = list(all_product)
    #                     not_avail_circle_product = list(not_avail_circle_product)
    #                     all_product_sort = sorted(all_product)
    #
    #                     first = self.env['product.product'].search(
    #                         [('barcode', '=', self.from_fastags)])
    #                     if first not in all_product:
    #                         raise UserError(
    #                             _('First barcode is not available'))
    #                     last = self.env['product.product'].search(
    #                         [('barcode', '=', self.to_fastags)])
    #                     if last not in all_product:
    #                         raise UserError(
    #                             _('Last barcode is not available'))
    #                     ind = all_product_sort.index(first)
    #                     ind2 = all_product_sort.index(last)
    #
    #                     check = (ind2 + 1 - ind)
    #                     print('check', check)
    #                     check = str(check)
    #                     # promoter restriction
    #
    #                     if user_id.rs_designation == 'fastag_promoter':
    #
    #                         fastags_needed = int(check) + len(
    #                             avail_circle_product)
    #                         if len(avail_circle_product) >= 100:
    #                             raise UserError(
    #                                 _('Promoter %s fastag count is exceeds the limit 100',
    #                                   user_id.name))
    #                         elif int(fastags_needed) > 100:
    #                             raise UserError(
    #                                 _('Promoter %s Already there are %s FASTag you can assign %s !',
    #                                   user_id.name, len(avail_circle_product),
    #                                   100 - len(avail_circle_product)))
    #
    #                     # TL Restriction
    #                     if user_id.rs_designation == 'fastag_tl':
    #
    #                         fastags_needed = int(check) + len(
    #                             avail_circle_product)
    #                         if len(avail_circle_product) >= 1000:
    #                             raise UserError(
    #                                 _('Promoter %s fastag count is exceeds the limit 100',
    #                                   user_id.name))
    #                         elif int(fastags_needed) > 1000:
    #                             raise UserError(
    #                                 _('Promoter %s Already there are %s FASTag you can assign %s !',
    #                                   user_id.name, len(avail_circle_product),
    #                                   1000 - len(avail_circle_product)))
    #
    #                     if len(all_product) >= int(check):
    #                         print("YES-------------")
    #                         for product_id in all_product_sort[
    #                                           ind:ind2 + 1]:
    #                             print('product',product_id)
    #                             if product_id in not_avail_circle_product:
    #                                 no_product.append(product_id.barcode)
    #                             else:
    #                                 # stock = self.env['stock.move'].sudo().create({})
    #                                 transfer_update_values = {
    #                                     'picking_id': self.id,
    #                                     'product_id': product_id.id,
    #                                     'name': product_id.name,
    #                                     'fatag_bracode': product_id.barcode,
    #                                     'category_id': product_id.categ_id.id,
    #                                     'circle_name': self.rs_circle.id,
    #                                     'emp_mobile_no': self.rs_emp_mob_no,
    #                                     'location_id': 1,
    #                                     'product_uom': 1,
    #                                     'location_dest_id': 1,
    #                                     # 'id': stock.id
    #                                 }
    #                                 update_transfer_records.append(
    #                                     transfer_update_values)
    #                                 prduct_update_value = {
    #                                     'product_id': product_id.id,
    #                                     'assign': user_id.id
    #                                     }
    #                                 update_product_id.append(prduct_update_value)
    #                         # query1 = """UPDATE stock_move SET picking_id=%(picking_id)s,
    #                         #
    #                         #                                                                               product_id=%(product_id)s,
    #                         #                                                                               name=%(name)s,
    #                         #                                                                               fatag_bracode = %(fatag_bracode)s,
    #                         #                                                                                 category_id=%(category_id)s,
    #                         #                                                                                 circle_name=%(circle_name)s,
    #                         #                                                                                 emp_mobile_no=%(emp_mobile_no)s,
    #                         #                                                                                 location_id=%(location_id)s,
    #                         #                                                                                 product_uom=%(product_uom)s,
    #                         #                                                                                 location_dest_id=%(location_dest_id)s
    #                         #                                                                                 WHERE id = %(id)s
    #                         #                                                      """
    #                         #
    #                         # self.env.cr.executemany(query1, update_transfer_records)
    #                         #
    #                         # query = """
    #                         #                         UPDATE product_template
    #                         #                        SET warehouse_emp_no = Null,
    #                         #                        product_assigned_to = %(assign)s
    #                         #                        WHERE id = (SELECT product_tmpl_id
    #                         #                                            FROM product_product WHERE id=%(product_id)s)
    #                         #                                                                            """
    #                         #
    #                         # self.env.cr.executemany(query,
    #                         #                     update_product_id)
    #                         #
    #                         # self.sudo().update(
    #                         #     {'rs_destination_id': user_id.id,
    #                         #      'rs_emp_no': self.rs_emp_mob_no,
    #                         #      'rs_circle_id': self.rs_circle.id
    #                         #      })
    #                         context = {
    #                             # 'default_move_type': 'out_invoice',
    #                             'default_order_line_form': [
    #                                 update_transfer_records
    #                             ],
    #                             'default_barcode':[
    #                                 no_product
    #                             ]
    #
    #                         }
    #                         return {
    #                             'type': 'ir.actions.act_window',
    #                             'name': 'Confirm Transfer ',
    #                             'view_mode': 'form',
    #                             'target': 'new',
    #                             'res_model': 'seequence.wizard',
    #                             'context': context
    #                         }
    #                     else:
    #
    #                         raise UserError(
    #                             _('No available fastag'
    #                               ))
    #
    #                 else:
    #                     if self.no_fastags == False:
    #                         raise UserError(
    #                             _('You can not create blank transfer please enter number of fastags greater then Zero'))
    #
    #                     else:
    #                         # promoter restriction
    #
    #                         if user_id.rs_designation == 'fastag_promoter':
    #
    #                             fastags_needed = len(
    #                                 avail_circle_product) + int(self.no_fastags)
    #                             if len(avail_circle_product) >= 100:
    #                                 raise UserError(
    #                                     _('Promoter %s fastag count is exceeds the limit 100',
    #                                       user_id.name))
    #                             elif int(fastags_needed) > 100:
    #                                 raise UserError(
    #                                     _('Promoter %s Already there are %s FASTag you can assign %s !',
    #                                       user_id.name,
    #                                       len(avail_circle_product),
    #                                       100 - len(avail_circle_product)))
    #
    #                         # TL Restriction
    #                         if user_id.rs_designation == 'fastag_tl':
    #
    #                             fastags_needed = len(
    #                                 avail_circle_product) + int(self.no_fastags)
    #                             if int(avail_circle_product) >= 1000:
    #                                 raise UserError(
    #                                     _('Teamleader %s fastag count is exceeds the limit 1000',
    #                                       user_id.name))
    #                             elif int(fastags_needed) > 1000:
    #                                 raise UserError(
    #                                     _('Promoter %s Already there are %s FASTag you can assign %s !',
    #                                       user_id.name,
    #                                       len(avail_circle_product),
    #                                       1000 - len(avail_circle_product)))
    #
    #                         if len(avail_circle_product) >= int(
    #                                 self.no_fastags):
    #                             print("YES-------------")
    #                             for product_id in avail_circle_product[
    #                                               :int(self.no_fastags)]:
    #                                 stock = self.env[
    #                                     'stock.move'].sudo().create({})
    #                                 print('product_id',product_id)
    #                                 transfer_update_values = {
    #                                     'picking_id': self.id,
    #                                     'product_id': product_id.id,
    #                                     'name': product_id.name,
    #                                     'fatag_bracode': product_id.barcode,
    #                                     'category_id': product_id.categ_id.id,
    #                                     'circle_name': self.rs_circle.id,
    #                                     'emp_mobile_no': self.rs_emp_mob_no,
    #                                     'location_id': 1,
    #                                     'product_uom': 1,
    #                                     'location_dest_id': 1,
    #                                     'id': stock.id
    #                                 }
    #                                 update_transfer_records.append(
    #                                     transfer_update_values)
    #                                 prduct_update_value = {
    #                                     'product_id': product_id.id,
    #                                     'assign': user_id.id
    #                                 }
    #                                 update_product_id.append(
    #                                     prduct_update_value)
    #                             query1 = """UPDATE stock_move SET picking_id=%(picking_id)s,
    #
    #                                                                                                                                           product_id=%(product_id)s,
    #                                                                                                                                           name=%(name)s,
    #                                                                                                                                           fatag_bracode = %(fatag_bracode)s,
    #                                                                                                                                             category_id=%(category_id)s,
    #                                                                                                                                             circle_name=%(circle_name)s,
    #                                                                                                                                             emp_mobile_no=%(emp_mobile_no)s,
    #                                                                                                                                             location_id=%(location_id)s,
    #                                                                                                                                             product_uom=%(product_uom)s,
    #                                                                                                                                             location_dest_id=%(location_dest_id)s
    #                                                                                                                                             WHERE id = %(id)s
    #                                                                                                                  """
    #
    #                             self.env.cr.executemany(query1,
    #                                                 update_transfer_records)
    #
    #                             query = """
    #                                                                                     UPDATE product_template
    #                                                                                    SET warehouse_emp_no = Null,
    #                                                                                    product_assigned_to = %(assign)s
    #                                                                                    WHERE id = (SELECT product_tmpl_id
    #                                                                                                        FROM product_product WHERE id=%(product_id)s)
    #                                                                                                                                        """
    #
    #                             self.env.cr.executemany(query,
    #                                                 update_product_id)
    #
    #                             self.sudo().update(
    #                                 {'rs_destination_id': user_id.id,
    #                                  'rs_emp_no': self.rs_emp_mob_no,
    #                                  'rs_circle_id': self.rs_circle.id
    #                                  })
    #                         else:
    #
    #                             raise UserError(
    #                                 _('No available fastag'
    #                                   ))
    #                 template = self.env.ref(
    #                     'rn_vehical_class.inventory_trasfer_assigned_email_template')
    #                 self.env['mail.template'].browse(template.id).send_mail(
    #                     self.id)
    #
    #             else:
    #                 raise UserError(_('Please Check Employee Mobile Number'))
    #         else:
    #
    #             if user_id:
    #
    #                 avail_circle_product = self.env['product.product'].search(
    #                     [('circle_name', '=', self.rs_circle.id),
    #                      ('fastag_sold', '=', 'no'),
    #                      ('rs_faulty_stag', '=', 'no'),
    #                      ('unlink_fastag', '=', False),
    #                      ('categ_id', '=', self.category_id.id),
    #                      ('warehouse_emp_no', '=',
    #                       self.env.user.rs_employee_id)])
    #
    #                 if self.sequence_fastag == True:
    #                     if self.from_fastags == False:
    #                         raise UserError(
    #                             _('You can not create blank transfer Please enter beginning barcode .'))
    #                     if self.to_fastags == False:
    #                         raise UserError(
    #                             _('You need to provide end range of barcode .'))
    #
    #                     avail_circle_product = list(avail_circle_product)
    #                     avail_circle_product_sort = sorted(avail_circle_product)
    #                     # print(type(avail_circle_product),avail_circle_product)
    #                     first = self.env['product.product'].search(
    #                         [('barcode', '=', self.from_fastags)])
    #                     last = self.env['product.product'].search(
    #                         [('barcode', '=', self.to_fastags)])
    #                     ind = avail_circle_product_sort.index(first)
    #                     ind2 = avail_circle_product_sort.index(last)
    #                     # print('index value -of avail first barcode-----------',ind,ind2,'id---',id)
    #
    #                     # print('first or last barcode-----------',first,last)
    #
    #
    #                     check = (ind2 + 1 - ind)
    #                     print('check', check)
    #                     check = str(check)
    #                     # promoter restriction
    #
    #                     if user_id.rs_designation == 'fastag_promoter':
    #
    #                         fastags_needed = int(check) + len(
    #                             avail_circle_product)
    #                         if len(avail_circle_product) >= 100:
    #                             raise UserError(
    #                                 _('Promoter %s fastag count is exceeds the limit 100',
    #                                   user_id.name))
    #                         elif int(fastags_needed) > 100:
    #                             raise UserError(
    #                                 _('Promoter %s Already there are %s FASTag you can assign %s !',
    #                                   user_id.name, len(avail_circle_product),
    #                                   100 - len(avail_circle_product)))
    #
    #                     # TL Restriction
    #                     if user_id.rs_designation == 'fastag_tl':
    #
    #                         fastags_needed = int(check) + len(
    #                             avail_circle_product)
    #                         if len(avail_circle_product) >= 1000:
    #                             raise UserError(
    #                                 _('Promoter %s fastag count is exceeds the limit 100',
    #                                   user_id.name))
    #                         elif int(fastags_needed) > 1000:
    #                             raise UserError(
    #                                 _('Promoter %s Already there are %s FASTag you can assign %s !',
    #                                   user_id.name, len(avail_circle_product),
    #                                   1000 - len(avail_circle_product)))
    #                     if len(avail_circle_product) >= int(check):
    #                         print("YES-------------")
    #
    #                         for product_id in avail_circle_product_sort[
    #                                           ind:ind2 + 1]:
    #                             stock = self.env['stock.move'].sudo().create({})
    #                             transfer_update_values = {
    #                                 'picking_id': self.id,
    #                                 'product_id': product_id.id,
    #                                 'name': product_id.name,
    #                                 'fatag_bracode': product_id.barcode,
    #                                 'category_id': product_id.categ_id.id,
    #                                 'circle_name': self.rs_circle.id,
    #                                 'emp_mobile_no': self.rs_emp_mob_no,
    #                                 'location_id': 1,
    #                                 'product_uom': 1,
    #                                 'location_dest_id': 1,
    #                                 'id': stock.id
    #                             }
    #                             update_transfer_records.append(
    #                                 transfer_update_values)
    #                             prduct_update_value = {
    #                                 'product_id': product_id.id,
    #                                 'assign': user_id.id
    #                             }
    #                             update_product_id.append(prduct_update_value)
    #                         query1 = """UPDATE stock_move SET picking_id=%(picking_id)s,
    #
    #                                                                                                                                       product_id=%(product_id)s,
    #                                                                                                                                       name=%(name)s,
    #                                                                                                                                       fatag_bracode = %(fatag_bracode)s,
    #                                                                                                                                         category_id=%(category_id)s,
    #                                                                                                                                         circle_name=%(circle_name)s,
    #                                                                                                                                         emp_mobile_no=%(emp_mobile_no)s,
    #                                                                                                                                         location_id=%(location_id)s,
    #                                                                                                                                         product_uom=%(product_uom)s,
    #                                                                                                                                         location_dest_id=%(location_dest_id)s
    #                                                                                                                                         WHERE id = %(id)s
    #                                                                                                              """
    #
    #                         self.env.cr.executemany(query1, update_transfer_records)
    #
    #                         query = """
    #                                                                                 UPDATE product_template
    #                                                                                SET warehouse_emp_no = Null,
    #                                                                                product_assigned_to = %(assign)s
    #                                                                                WHERE id = (SELECT product_tmpl_id
    #                                                                                                    FROM product_product WHERE id=%(product_id)s)
    #                                                                                                                                    """
    #
    #                         self.env.cr.executemany(query,
    #                                             update_product_id)
    #
    #                         self.sudo().update(
    #                             {'rs_destination_id': user_id.id,
    #                              'rs_emp_no': self.rs_emp_mob_no,
    #                              'rs_circle_id': self.rs_circle.id
    #                              })
    #                     else:
    #
    #                         raise UserError(
    #                             _('No available fastag'
    #                               ))
    #
    #                 else:
    #                     if self.no_fastags == False:
    #                         raise UserError(
    #                             _('You can not create blank transfer please enter number of fastags greater then Zero'))
    #
    #                     else:
    #                         # promoter restriction
    #
    #                         if user_id.rs_designation == 'fastag_promoter':
    #
    #                             fastags_needed = len(
    #                                 avail_circle_product) + int(self.no_fastags)
    #                             if len(avail_circle_product) >= 100:
    #                                 raise UserError(
    #                                     _('Promoter %s fastag count is exceeds the limit 100',
    #                                       user_id.name))
    #                             elif int(fastags_needed) > 100:
    #                                 raise UserError(
    #                                     _('Promoter %s Already there are %s FASTag you can assign %s !',
    #                                       user_id.name,
    #                                       len(avail_circle_product),
    #                                       100 - len(avail_circle_product)))
    #
    #                         # TL Restriction
    #                         if user_id.rs_designation == 'fastag_tl':
    #
    #                             fastags_needed = len(
    #                                 avail_circle_product) + int(self.no_fastags)
    #                             if int(avail_circle_product) >= 1000:
    #                                 raise UserError(
    #                                     _('Teamleader %s fastag count is exceeds the limit 1000',
    #                                       user_id.name))
    #                             elif int(fastags_needed) > 1000:
    #                                 raise UserError(
    #                                     _('Promoter %s Already there are %s FASTag you can assign %s !',
    #                                       user_id.name,
    #                                       len(avail_circle_product),
    #                                       1000 - len(avail_circle_product)))
    #
    #                         if len(avail_circle_product) >= int(
    #                                 self.no_fastags):
    #                             print("YES-------------")
    #                             for product_id in avail_circle_product[
    #                                               :int(self.no_fastags)]:
    #                                 stock = self.env[
    #                                     'stock.move'].sudo().create({})
    #                                 transfer_update_values = {
    #                                     'picking_id': self.id,
    #                                     'product_id': product_id.id,
    #                                     'name': product_id.name,
    #                                     'fatag_bracode': product_id.barcode,
    #                                     'category_id': product_id.categ_id.id,
    #                                     'circle_name': self.rs_circle.id,
    #                                     'emp_mobile_no': self.rs_emp_mob_no,
    #                                     'location_id': 1,
    #                                     'product_uom': 1,
    #                                     'location_dest_id': 1,
    #                                     'id': stock.id
    #                                 }
    #                                 update_transfer_records.append(
    #                                     transfer_update_values)
    #                                 prduct_update_value = {
    #                                     'product_id': product_id.id,
    #                                     'assign': user_id.id
    #                                 }
    #                                 update_product_id.append(
    #                                     prduct_update_value)
    #                             query1 = """UPDATE stock_move SET picking_id=%(picking_id)s,
    #
    #                                                                                                                                           product_id=%(product_id)s,
    #                                                                                                                                           name=%(name)s,
    #                                                                                                                                           fatag_bracode = %(fatag_bracode)s,
    #                                                                                                                                             category_id=%(category_id)s,
    #                                                                                                                                             circle_name=%(circle_name)s,
    #                                                                                                                                             emp_mobile_no=%(emp_mobile_no)s,
    #                                                                                                                                             location_id=%(location_id)s,
    #                                                                                                                                             product_uom=%(product_uom)s,
    #                                                                                                                                             location_dest_id=%(location_dest_id)s
    #                                                                                                                                             WHERE id = %(id)s
    #                                                                                                                  """
    #
    #                             self.env.cr.executemany(query1,
    #                                                 update_transfer_records)
    #
    #                             query = """
    #                                                                                     UPDATE product_template
    #                                                                                    SET warehouse_emp_no = Null,
    #                                                                                    product_assigned_to = %(assign)s
    #                                                                                    WHERE id = (SELECT product_tmpl_id
    #                                                                                                        FROM product_product WHERE id=%(product_id)s)
    #                                                                                                                                        """
    #
    #                             self.env.cr.executemany(query,
    #                                                 update_product_id)
    #
    #                             self.sudo().update(
    #                                 {'rs_destination_id': user_id.id,
    #                                  'rs_emp_no': self.rs_emp_mob_no,
    #                                  'rs_circle_id': self.rs_circle.id
    #                                  })
    #
    #                         else:
    #
    #                             raise UserError(
    #                                 _('No available fastag'
    #                                   ))
    #                 template = self.env.ref(
    #                     'rn_vehical_class.inventory_trasfer_assigned_email_template')
    #                 self.env['mail.template'].browse(template.id).send_mail(
    #                     self.id)
    #
    #             else:
    #                 raise UserError(_('Please Check Employee Mobile Number'))
    #     return True
    def get_serial_wise_barcode(self):
        if self.rs_destination_id:
            raise UserError(
                _('Already assign transfer,If you want to transfer please click on "Create" Button'))
        else:
            user_id = self.env['res.users'].search(
                [('login', '=', self.rs_emp_mob_no)])

            # circle mismatch
            user_em_id = self.env['res.users'].search(
                [('id', '=', self.rs_user_id.id)])
            if user_em_id.rs_designation == 'em':
                if self.rs_circle.id != user_id.rs_circle.id:
                    raise UserError(
                        'Mismatching circle name'
                    )

            update_transfer_records = []
            update_product_id = []

            if self.env.user.id == 673:
                if user_id:
                    if self.sequence_fastag == True:
                        if self.from_fastags == False:
                            raise UserError(
                                _('You can not create blank transfer Please enter beginning barcode .'))
                        if self.to_fastags == False:
                            raise UserError(
                                _('You need to provide end range of barcode .'))

                        from_bar = self.from_fastags
                        if len(from_bar) != 16:
                            raise UserError(
                                _('Please remove the hyphen in first barcode or write proper barcode'))
                        from_first = from_bar[0:6]
                        from_sec = from_bar[6:9]
                        from_thr = from_bar[9:]
                        from_fastags = "%s-%s-%s" % (
                        from_first, from_sec, from_thr)

                        to_bar = self.to_fastags
                        if len(to_bar) != 16:
                            raise UserError(
                                _('Please remove the hyphen in last barcode or write proper barcode'))
                        to_first = to_bar[0:6]
                        to_sec = to_bar[6:9]
                        to_thr = to_bar[9:]
                        to_fastags = "%s-%s-%s" % (
                        to_first, to_sec, to_thr)


                        from_barcode = self.env['product.product'].search(
                            [
                                ('fastag_sold', '=', 'no'),
                                ('rs_faulty_stag', '=', 'no'),
                                ('unlink_fastag', '=', False),
                                ('categ_id', '=', self.category_id.id),
                                ('warehouse_emp_no', '=',
                                 self.env.user.rs_employee_id),
                            ('barcode', '=', from_fastags)])
                        from_id = from_barcode.id
                        if not from_barcode:
                            sold_from_barcode = self.env['product.product'].search(
                                [
                                    ('fastag_sold', '=', 'yes'),
                                    ('categ_id', '=', self.category_id.id),
                                    ('warehouse_emp_no', '=',
                                     self.env.user.rs_employee_id),
                                    ('barcode', '=', from_fastags)])
                            if sold_from_barcode:
                                raise UserError(
                                    _('First barcode %s is soldout', from_fastags))
                            unlink_from_barcode = self.env['product.product'].search(
                                [
                                    ('unlink_fastag', '=', True),
                                    ('categ_id', '=', self.category_id.id),
                                    ('warehouse_emp_no', '=',
                                     self.env.user.rs_employee_id),
                                    ('barcode', '=', from_fastags)])
                            if unlink_from_barcode:
                                raise UserError(
                                    _('First barcode %s is unlinked', from_fastags))
                        to_barcode = self.env['product.product'].search(
                            [
                                ('fastag_sold', '=', 'no'),
                                ('rs_faulty_stag', '=', 'no'),
                                ('unlink_fastag', '=', False),
                                ('categ_id', '=', self.category_id.id),
                                ('warehouse_emp_no', '=',
                                 self.env.user.rs_employee_id),
                                ('barcode', '=', to_fastags)])
                        to_id = to_barcode.id
                        if not to_barcode:
                            sold_to_barcode = self.env['product.product'].search(
                                [
                                    ('fastag_sold', '=', 'yes'),
                                    ('categ_id', '=', self.category_id.id),
                                    ('warehouse_emp_no', '=',
                                     self.env.user.rs_employee_id),
                                    ('barcode', '=', to_fastags)])
                            if sold_to_barcode:
                                raise UserError(
                                    _('Last barcode %s is soldout', to_fastags))
                            unlink_to_barcode = self.env['product.product'].search(
                                [
                                    ('unlink_fastag', '=', True),
                                    ('categ_id', '=', self.category_id.id),
                                    ('warehouse_emp_no', '=',
                                     self.env.user.rs_employee_id),
                                    ('barcode', '=', to_fastags)])
                            if unlink_to_barcode:
                                raise UserError(
                                    _('Last barcode %s is unlinked', to_fastags))
                        ids = []
                        for id in range(from_id, to_id + 1):
                            ids.append(id)

                        avail_product = self.env[
                            'product.product'].search(
                            [
                                ('fastag_sold', '=', 'no'),
                                ('rs_faulty_stag', '=', 'no'),
                                ('unlink_fastag', '=', False),
                                ('categ_id', '=', self.category_id.id),
                                ('warehouse_emp_no', '=',
                                 self.env.user.rs_employee_id),('id','in',ids)])
                        not_avail_product = self.env['product.product'].search(
                            ['|', '|', ('fastag_sold', '=', 'yes'),
                             ('rs_faulty_stag', '=', 'yes'),
                             ('unlink_fastag', '=', True),
                             ('id', 'in', ids)])
                        sold_id = []
                        fault_id = []
                        unlink_id = []
                        if not_avail_product:
                            context = {}
                            for bar_id in not_avail_product:
                                if bar_id.fastag_sold == 'yes':
                                    sold_id.append(bar_id.barcode)
                                if bar_id.rs_faulty_stag == 'yes':
                                    fault_id.append(bar_id.barcode)
                                if bar_id.unlink_fastag == True:
                                    unlink_id.append(bar_id.barcode)
                            if sold_id != []:
                                context.update({
                                    'default_sold': ('\n'.join(sold_id))})
                            if fault_id != []:
                                context.update({
                                    'default_fault': ('\n'.join(fault_id))})
                            if unlink_id != []:
                                context.update({
                                    'default_unlink': ('\n'.join(unlink_id))
                                })
                            return {
                                'type': 'ir.actions.act_window',
                                'name': 'Barcode Not Available',
                                'view_mode': 'form',
                                'view_type': 'form',
                                'res_model': 'seequence.wizard',
                                'target': 'new',
                                'context': context
                            }
                        if user_id.rs_designation == 'fastag_promoter':
                            records = self.env[
                                'product.product'].sudo().search_count(
                                [('product_assigned_to', '=',
                                  user_id.id),
                                 ('fastag_sold', '=', 'no'),
                                 ('rs_faulty_stag', '=', 'no'),
                                 ('unlink_fastag', '=', False)])

                            fastags_needed = len(avail_product) + int(records)
                            if int(records) >= 100:
                                raise UserError(
                                    _('Promoter %s fastag count is exceeds the limit 100',
                                      user_id.name))
                            elif int(fastags_needed) > 100:
                                raise UserError(
                                    _('Promoter %s Already there are %s FASTag you can assign %s !',
                                      user_id.name, int(records),
                                      100 - int(records)))

                        # TL Restriction
                        if user_id.rs_designation == 'fastag_tl':

                            records = self.env[
                                'product.product'].sudo().search_count(
                                [('product_assigned_to', '=',
                                  user_id.id),
                                 ('fastag_sold', '=', 'no'),
                                 ('rs_faulty_stag', '=', 'no'),
                                 ('unlink_fastag', '=', False)])

                            fastags_needed = len(avail_product) + int(records)
                            if int(records) >= 1000:
                                raise UserError(
                                    _('Promoter %s fastag count is exceeds the limit 100',
                                      user_id.name))
                            elif int(fastags_needed) > 1000:
                                raise UserError(
                                    _('Promoter %s Already there are %s FASTag you can assign %s !',
                                      user_id.name, int(records),
                                      1000 - int(records)))

                        # if len(avail_product) == ((int(to_id) - int(from_id)) + 1):
                        for product_id in avail_product:
                                stock = self.env['stock.move'].sudo().create({})
                                transfer_update_values = {
                                    'picking_id': self.id,
                                    'product_id': product_id.id,
                                    'name': product_id.name,
                                    'fatag_bracode': product_id.barcode,
                                    'category_id': product_id.categ_id.id,
                                    'circle_name': self.rs_circle.id,
                                    'emp_mobile_no': self.rs_emp_mob_no,
                                    'location_id': 24,
                                    'product_uom': 1,
                                    'location_dest_id': 24,
                                    'id': stock.id
                                }
                                update_transfer_records.append(
                                    transfer_update_values)
                                prduct_update_value = {
                                    'product_id': product_id.id,
                                    'assign': user_id.id
                                }
                                update_product_id.append(prduct_update_value)
                        query1 = """UPDATE stock_move SET picking_id=%(picking_id)s, 

                                                                                                          product_id=%(product_id)s, 
                                                                                                          name=%(name)s,
                                                                                                          fatag_bracode = %(fatag_bracode)s,
                                                                                                            category_id=%(category_id)s, 
                                                                                                            circle_name=%(circle_name)s,
                                                                                                            emp_mobile_no=%(emp_mobile_no)s,
                                                                                                            location_id=%(location_id)s,
                                                                                                            product_uom=%(product_uom)s,
                                                                                                            location_dest_id=%(location_dest_id)s
                                                                                                            WHERE id = %(id)s 
                                                                                 """

                        self.env.cr.executemany(query1,
                                                    update_transfer_records)

                        query = """
                                                    UPDATE product_template
                                                   SET warehouse_emp_no = Null,
                                                   product_assigned_to = %(assign)s
                                                   WHERE id = (SELECT product_tmpl_id
                                                                       FROM product_product WHERE id=%(product_id)s)
                                                                                                       """

                        self.env.cr.executemany(query,
                                                    update_product_id)

                        self.sudo().update(
                                {'rs_destination_id': user_id.id,
                                 'rs_emp_no': self.rs_emp_mob_no,
                                 'rs_circle_id': self.rs_circle.id
                                 })

                        # create list for insert records to unacknowledged report
                        self.sudo().env.cr.execute("""INSERT INTO unacknowledged_report ( rs_name, rs_barcode, assigned_id, rs_from_emp_no,
                                   rs_to_emp_no,rs_circle_id) 
                                                               SELECT st.name,sm.fatag_bracode, st.rs_destination_id,rs.rs_employee_id,
                                                               rd.rs_employee_id,sm.circle_name
                                                               FROM stock_picking st INNER JOIN stock_move sm ON sm.picking_id = st.id 
                                                               INNER JOIN res_users rd ON rd.id = st.rs_destination_id
                                                               INNER JOIN res_users rs ON rs.id = st.rs_user_id WHERE st.id = %s
                                                               """ % (self.id))

                        # for product_id in avail_product:
                        #     unawk_tag_obj = self.env['unacknowledged.report']
                        #     a = unawk_tag_obj.create({'rs_name': self.name,
                        #                               'rs_barcode': product_id.barcode,
                        #                               'assigned_id': self.sudo().rs_destination_id.id,
                        #                               'rs_from_emp_no': self.rs_user_id.rs_employee_id,
                        #                               'rs_to_emp_no': self.sudo().rs_destination_id.rs_employee_id,
                        #                               'rs_circle_id': self.rs_circle.id
                        #                               })
                        # else:
                        #
                        #     raise UserError(
                        #         _('No available fastag'
                        #           ))

                    else:
                        if self.no_fastags == False:
                            raise UserError(
                                _('You can not create blank transfer please enter number of fastags greater then Zero'))

                        else:
                            # promoter restriction
                            avail_circle_product = self.env[
                                'product.product'].search(
                                [
                                    ('fastag_sold', '=', 'no'),
                                    ('rs_faulty_stag', '=', 'no'),
                                    ('unlink_fastag', '=', False),
                                    ('categ_id', '=', self.category_id.id),
                                    ('warehouse_emp_no', '=',
                                     self.env.user.rs_employee_id)])

                            if user_id.rs_designation == 'fastag_promoter':
                                records = self.env[
                                    'product.template'].sudo().search_count(
                                    [('product_assigned_to', '=',
                                  user_id.id),
                                     ('fastag_sold', '=', 'no'),
                                     ('rs_faulty_stag', '=', 'no'),
                                     ('unlink_fastag', '=', False)])

                                fastags_needed = int(records) + int(self.no_fastags)
                                if int(records) >= 100:
                                    raise UserError(
                                        _('Promoter %s fastag count is exceeds the limit 100',
                                          user_id.name))
                                elif int(fastags_needed) > 100:
                                    raise UserError(
                                        _('Promoter %s Already there are %s FASTag you can assign %s !',
                                          user_id.name,
                                          int(records),
                                          100 - int(records)))

                            # TL Restriction
                            if user_id.rs_designation == 'fastag_tl':

                                records = self.env[
                                    'product.template'].sudo().search_count(
                                    [('product_assigned_to', '=',
                                  user_id.id),
                                     ('fastag_sold', '=', 'no'),
                                     ('rs_faulty_stag', '=', 'no'),
                                     ('unlink_fastag', '=', False)])

                                fastags_needed = int(records) + int(
                                    self.no_fastags)
                                if int(records) >= 1000:
                                    raise UserError(
                                        _('Promoter %s fastag count is exceeds the limit 100',
                                          user_id.name))
                                elif int(fastags_needed) > 1000:
                                    raise UserError(
                                        _('Promoter %s Already there are %s FASTag you can assign %s !',
                                          user_id.name,
                                          int(records),
                                          1000 - int(records)))

                            if len(avail_circle_product) >= int(
                                    self.no_fastags):
                                print("YES-------------")
                                for product_id in avail_circle_product[
                                                  :int(self.no_fastags)]:
                                    stock = self.env[
                                        'stock.move'].sudo().create({})
                                    print('product_id', product_id)
                                    transfer_update_values = {
                                        'picking_id': self.id,
                                        'product_id': product_id.id,
                                        'name': product_id.name,
                                        'fatag_bracode': product_id.barcode,
                                        'category_id': product_id.categ_id.id,
                                        'circle_name': self.rs_circle.id,
                                        'emp_mobile_no': self.rs_emp_mob_no,
                                        'location_id': 24,
                                        'product_uom': 1,
                                        'location_dest_id': 24,
                                        'id': stock.id
                                    }
                                    update_transfer_records.append(
                                        transfer_update_values)

                                    prduct_update_value = {
                                        'product_id': product_id.id,
                                        'assign': user_id.id,
                                        'order': self.select_order_id.name
                                    }
                                    update_product_id.append(
                                        prduct_update_value)

                                query1 = """UPDATE stock_move SET picking_id=%(picking_id)s,

                                                                                                                                              product_id=%(product_id)s,
                                                                                                                                              name=%(name)s,
                                                                                                                                              fatag_bracode = %(fatag_bracode)s,
                                                                                                                                                category_id=%(category_id)s,
                                                                                                                                                circle_name=%(circle_name)s,
                                                                                                                                                emp_mobile_no=%(emp_mobile_no)s,
                                                                                                                                                location_id=%(location_id)s,
                                                                                                                                                product_uom=%(product_uom)s,
                                                                                                                                                location_dest_id=%(location_dest_id)s
                                                                                                                                                WHERE id = %(id)s
                                                                                                                     """

                                self.env.cr.executemany(query1,
                                                        update_transfer_records)
                                if self.select_order_id:

                                    query = """
                                                                                            UPDATE product_template
                                                                                           SET warehouse_emp_no = Null,
                                                                                           product_assigned_to = %(assign)s,
                                                                                           order_id = %(order)s
                                                                                           WHERE id = (SELECT product_tmpl_id
                                                                                                               FROM product_product WHERE id=%(product_id)s)
                                                                                                                                               """

                                    self.env.cr.executemany(query,
                                                            update_product_id)
                                else:
                                    query = """
                                                                                                                                UPDATE product_template
                                                                                                                               SET warehouse_emp_no = Null,
                                                                                                                               product_assigned_to = %(assign)s
                                                                                                                               WHERE id = (SELECT product_tmpl_id
                                                                                                                                                   FROM product_product WHERE id=%(product_id)s)
                                                                                                                                                                                   """

                                    self.env.cr.executemany(query,
                                                            update_product_id)
                                self.sudo().update(
                                    {'rs_destination_id': user_id.id,
                                     'rs_emp_no': self.rs_emp_mob_no,
                                     'rs_circle_id': self.rs_circle.id
                                     })

                                # create list for insert records to unacknowledged report
                                for product_id in avail_circle_product[:int(self.no_fastags)]:
                                    unawk_tag_obj = self.env['unacknowledged.report']
                                    a = unawk_tag_obj.create({'rs_name': self.name,
                                                              'rs_barcode': product_id.barcode,
                                                              'assigned_id': self.sudo().rs_destination_id.id,
                                                              'rs_from_emp_no': self.rs_user_id.rs_employee_id,
                                                              'rs_to_emp_no': self.sudo().rs_destination_id.rs_employee_id,
                                                              'rs_circle_id': self.rs_circle.id
                                                              })
                            else:

                                raise UserError(
                                    _('No available fastag'
                                      ))
                    template = self.env.ref(
                        'rn_vehical_class.inventory_trasfer_assigned_email_template')
                    self.env['mail.template'].browse(template.id).send_mail(
                        self.id)
                    self.select_order_id.tag_fulfillment_status = 'transferred'

                else:
                    raise UserError(_('Please Check Employee Mobile Number'))
            else:

                if user_id:

                    if self.sequence_fastag == True:
                        if self.from_fastags == False:
                            raise UserError(
                                _('You can not create blank transfer Please enter beginning barcode .'))
                        if self.to_fastags == False:
                            raise UserError(
                                _('You need to provide end range of barcode .'))

                        from_bar = self.from_fastags
                        if len(from_bar) != 16:
                            raise UserError(
                                _('Please remove the hyphen in barcode or write proper barcode'))
                        from_first = from_bar[0:6]
                        from_sec = from_bar[6:9]
                        from_thr = from_bar[9:]
                        from_fastags = "%s-%s-%s" % (
                            from_first, from_sec, from_thr)
                        to_bar = self.to_fastags
                        if len(to_bar) != 16:
                            raise UserError(
                                _('Please remove the hyphen in barcode or write proper barcode'))
                        to_first = to_bar[0:6]
                        to_sec = to_bar[6:9]
                        to_thr = to_bar[9:]
                        to_fastags = "%s-%s-%s" % (
                            to_first, to_sec, to_thr)


                        from_barcode = self.env['product.product'].search(
                            [
                                ('fastag_sold', '=', 'no'),
                                ('rs_faulty_stag', '=', 'no'),
                                ('unlink_fastag', '=', False),
                                ('categ_id', '=', self.category_id.id),
                                ('warehouse_emp_no', '=',
                                 self.env.user.rs_employee_id),
                                ('barcode', '=', from_fastags)])
                        from_id = from_barcode.id
                        if not from_barcode:
                            sold_from_barcode = self.env['product.product'].search(
                                [
                                    ('fastag_sold', '=', 'yes'),
                                    ('categ_id', '=', self.category_id.id),
                                    ('warehouse_emp_no', '=',
                                     self.env.user.rs_employee_id),
                                    ('barcode', '=', from_fastags)])
                            if sold_from_barcode:
                                raise UserError(
                                    _('First barcode %s is soldout', from_fastags))
                            unlink_from_barcode = self.env['product.product'].search(
                                [
                                    ('unlink_fastag', '=', True),
                                    ('categ_id', '=', self.category_id.id),
                                    ('warehouse_emp_no', '=',
                                     self.env.user.rs_employee_id),
                                    ('barcode', '=', from_fastags)])
                            if unlink_from_barcode:
                                raise UserError(
                                    _('First barcode %s is unlinked', from_fastags))
                        to_barcode = self.env['product.product'].search(
                            [
                                ('fastag_sold', '=', 'no'),
                                ('rs_faulty_stag', '=', 'no'),
                                ('unlink_fastag', '=', False),
                                ('categ_id', '=', self.category_id.id),
                                ('warehouse_emp_no', '=',
                                 self.env.user.rs_employee_id),
                                ('barcode', '=', to_fastags)])
                        to_id = to_barcode.id
                        if not to_barcode:
                            sold_to_barcode = self.env['product.product'].search(
                                [
                                    ('fastag_sold', '=', 'yes'),
                                    ('categ_id', '=', self.category_id.id),
                                    ('warehouse_emp_no', '=',
                                     self.env.user.rs_employee_id),
                                    ('barcode', '=', to_fastags)])
                            if sold_to_barcode:
                                raise UserError(
                                    _('Last barcode %s is soldout', to_fastags))
                            unlink_to_barcode = self.env['product.product'].search(
                                [
                                    ('unlink_fastag', '=', True),
                                    ('categ_id', '=', self.category_id.id),
                                    ('warehouse_emp_no', '=',
                                     self.env.user.rs_employee_id),
                                    ('barcode', '=', to_fastags)])
                            if unlink_to_barcode:
                                raise UserError(
                                    _('Last barcode %s is unlinked', to_fastags))
                        ids = []
                        for id in range(from_id, to_id + 1):
                            ids.append(id)

                        avail_product = self.env[
                            'product.product'].search(
                            [
                                ('fastag_sold', '=', 'no'),
                                ('rs_faulty_stag', '=', 'no'),
                                ('unlink_fastag', '=', False),
                                ('categ_id', '=', self.category_id.id),
                                ('warehouse_emp_no', '=',
                                 self.env.user.rs_employee_id),
                                ('id', 'in', ids)])

                        not_avail_product = self.env['product.product'].search(
                            ['|', '|', ('fastag_sold', '=', 'yes'),
                             ('rs_faulty_stag', '=', 'yes'),
                             ('unlink_fastag', '=', True),
                             ('id', 'in', ids)])
                        sold_id = []
                        fault_id = []
                        unlink_id = []
                        if not_avail_product:
                            context = {}
                            for bar_id in not_avail_product:
                                if bar_id.fastag_sold == 'yes':
                                    sold_id.append(bar_id.barcode)
                                if bar_id.rs_faulty_stag == 'yes':
                                    fault_id.append(bar_id.barcode)
                                if bar_id.unlink_fastag == True:
                                    unlink_id.append(bar_id.barcode)
                            if sold_id != []:
                                context.update({
                                    'default_sold': ('\n'.join(sold_id))})
                            if fault_id != []:
                                context.update({
                                    'default_fault': ('\n'.join(fault_id))})
                            if unlink_id != []:
                                context.update({
                                    'default_unlink': ('\n'.join(unlink_id))
                                })
                            return {
                                'type': 'ir.actions.act_window',
                                'name': 'Barcode Not Available',
                                'view_mode': 'form',
                                'view_type': 'form',
                                'res_model': 'seequence.wizard',
                                'target': 'new',
                                'context': context
                            }
                        # faulty_product = self.env['product.product'].search(
                        #     [('rs_faulty_stag', '=', 'yes'),
                        #      ('id', 'in', ids)])
                        # fault_id = []
                        # if faulty_product:
                        #     for f_id in faulty_product:
                        #         fault_id.append(f_id.barcode)
                        #     context = {
                        #         'default_fault': ('\n'.join(fault_id))
                        #     }
                        #     return {
                        #         'type': 'ir.actions.act_window',
                        #         'name': 'Faulty Barcode',
                        #         'view_mode': 'form',
                        #         'view_type': 'form',
                        #         'res_model': 'seequence.wizard',
                        #         'target': 'new',
                        #         'context': context
                        #     }
                        # unlink_product = self.env['product.product'].search(
                        #     [('unlink_fastag', '=', True),
                        #      ('id', 'in', ids)])
                        # unlink_id = []
                        # if unlink_product:
                        #     for u_id in unlink_product:
                        #         unlink_id.append(u_id.barcode)
                        #     context = {
                        #         'default_unlink': ('\n'.join(unlink_id))
                        #     }
                        #     return {
                        #         'type': 'ir.actions.act_window',
                        #         'name': 'Unlink Barcode',
                        #         'view_mode': 'form',
                        #         'view_type': 'form',
                        #         'res_model': 'seequence.wizard',
                        #         'target': 'new',
                        #         'context': context
                        #     }

                        if user_id.rs_designation == 'fastag_promoter':
                            records = self.env[
                                'product.template'].sudo().search_count(
                                [('product_assigned_to', '=',
                                  user_id.id),
                                 ('fastag_sold', '=', 'no'),
                                 ('rs_faulty_stag', '=', 'no'),
                                 ('unlink_fastag', '=', False)])

                            fastags_needed = len(avail_product) + int(records)
                            if int(records) >= 100:
                                raise UserError(
                                    _('Promoter %s fastag count is exceeds the limit 100',
                                      user_id.name))
                            elif int(fastags_needed) > 100:
                                raise UserError(
                                    _('Promoter %s Already there are %s FASTag you can assign %s !',
                                      user_id.name, int(records),
                                      100 - int(records)))

                        # TL Restriction
                        if user_id.rs_designation == 'fastag_tl':

                            records = self.env[
                                'product.template'].sudo().search_count(
                                [('product_assigned_to', '=',
                                  user_id.id),
                                 ('fastag_sold', '=', 'no'),
                                 ('rs_faulty_stag', '=', 'no'),
                                 ('unlink_fastag', '=', False)])

                            fastags_needed = len(avail_product) + int(records)
                            if int(records) >= 1000:
                                raise UserError(
                                    _('Promoter %s fastag count is exceeds the limit 100',
                                      user_id.name))
                            elif int(fastags_needed) > 1000:
                                raise UserError(
                                    _('Promoter %s Already there are %s FASTag you can assign %s !',
                                      user_id.name, int(records),
                                      1000 - int(records)))

                        # if len(avail_product) == (
                        #         (int(to_id) - int(from_id)) + 1):
                        for product_id in avail_product:
                                stock = self.env['stock.move'].sudo().create({})
                                transfer_update_values = {
                                    'picking_id': self.id,
                                    'product_id': product_id.id,
                                    'name': product_id.name,
                                    'fatag_bracode': product_id.barcode,
                                    'category_id': product_id.categ_id.id,
                                    'circle_name': self.rs_circle.id,
                                    'emp_mobile_no': self.rs_emp_mob_no,
                                    'location_id': 24,
                                    'product_uom': 1,
                                    'location_dest_id': 24,
                                    'id': stock.id
                                }
                                update_transfer_records.append(
                                    transfer_update_values)
                                prduct_update_value = {
                                    'product_id': product_id.id,
                                    'assign': user_id.id
                                }
                                update_product_id.append(prduct_update_value)
                        query1 = """UPDATE stock_move SET picking_id=%(picking_id)s, 

                                                                                                                                          product_id=%(product_id)s, 
                                                                                                                                          name=%(name)s,
                                                                                                                                          fatag_bracode = %(fatag_bracode)s,
                                                                                                                                            category_id=%(category_id)s, 
                                                                                                                                            circle_name=%(circle_name)s,
                                                                                                                                            emp_mobile_no=%(emp_mobile_no)s,
                                                                                                                                            location_id=%(location_id)s,
                                                                                                                                            product_uom=%(product_uom)s,
                                                                                                                                            location_dest_id=%(location_dest_id)s
                                                                                                                                            WHERE id = %(id)s 
                                                                                                                 """

                        self.env.cr.executemany(query1,
                                                    update_transfer_records)

                        query = """
                                                                                    UPDATE product_template
                                                                                   SET warehouse_emp_no = Null,
                                                                                   product_assigned_to = %(assign)s
                                                                                   WHERE id = (SELECT product_tmpl_id
                                                                                                       FROM product_product WHERE id=%(product_id)s)
                                                                                                                                       """

                        self.env.cr.executemany(query,
                                                    update_product_id)

                        self.sudo().update(
                                {'rs_destination_id': user_id.id,
                                 'rs_emp_no': self.rs_emp_mob_no,
                                 'rs_circle_id': self.rs_circle.id
                                 })

                        # create list for insert records to unacknowledged report
                        for product_id in avail_product:
                            unawk_tag_obj = self.env['unacknowledged.report']
                            a = unawk_tag_obj.create({'rs_name': self.name,
                                                      'rs_barcode': product_id.barcode,
                                                      'assigned_id': self.sudo().rs_destination_id.id,
                                                      'rs_from_emp_no': self.rs_user_id.rs_employee_id,
                                                      'rs_to_emp_no': self.sudo().rs_destination_id.rs_employee_id,
                                                      'rs_circle_id': self.rs_circle.id
                                                      })
                        # else:
                        #
                        #     raise UserError(
                        #         _('No available fastag'
                        #           ))

                    else:
                        if self.no_fastags == False:
                            raise UserError(
                                _('You can not create blank transfer please enter number of fastags greater then Zero'))

                        else:
                            avail_circle_product = self.env[
                                'product.product'].search(
                                [('circle_name', '=', self.rs_circle.id),
                                 ('fastag_sold', '=', 'no'),
                                 ('rs_faulty_stag', '=', 'no'),
                                 ('unlink_fastag', '=', False),
                                 ('categ_id', '=', self.category_id.id),
                                 ('warehouse_emp_no', '=',
                                  self.env.user.rs_employee_id)])
                            # promoter restriction

                            if user_id.rs_designation == 'fastag_promoter':

                                records = self.env[
                                    'product.template'].sudo().search_count(
                                    [('product_assigned_to', '=',
                                  user_id.id),
                                     ('fastag_sold', '=', 'no'),
                                     ('rs_faulty_stag', '=', 'no'),
                                     ('unlink_fastag', '=', False)])

                                fastags_needed = int(records) + int(
                                    self.no_fastags)
                                if int(records) >= 100:
                                    raise UserError(
                                        _('Promoter %s fastag count is exceeds the limit 100',
                                          user_id.name))
                                elif int(fastags_needed) > 100:
                                    raise UserError(
                                        _('Promoter %s Already there are %s FASTag you can assign %s !',
                                          user_id.name,
                                          int(records),
                                          100 - int(records)))

                            # TL Restriction
                            if user_id.rs_designation == 'fastag_tl':

                                records = self.env[
                                    'product.template'].sudo().search_count(
                                    [('product_assigned_to', '=',
                                  user_id.id),
                                     ('fastag_sold', '=', 'no'),
                                     ('rs_faulty_stag', '=', 'no'),
                                     ('unlink_fastag', '=', False)])

                                fastags_needed = int(records) + int(
                                    self.no_fastags)
                                if int(records) >= 1000:
                                    raise UserError(
                                        _('Promoter %s fastag count is exceeds the limit 100',
                                          user_id.name))
                                elif int(fastags_needed) > 1000:
                                    raise UserError(
                                        _('Promoter %s Already there are %s FASTag you can assign %s !',
                                          user_id.name,
                                          int(records),
                                          1000 - int(records)))

                            if len(avail_circle_product) >= int(
                                    self.no_fastags):
                                print("YES-------------")
                                for product_id in avail_circle_product[
                                                  :int(self.no_fastags)]:
                                    stock = self.env[
                                        'stock.move'].sudo().create({})
                                    transfer_update_values = {
                                        'picking_id': self.id,
                                        'product_id': product_id.id,
                                        'name': product_id.name,
                                        'fatag_bracode': product_id.barcode,
                                        'category_id': product_id.categ_id.id,
                                        'circle_name': self.rs_circle.id,
                                        'emp_mobile_no': self.rs_emp_mob_no,
                                        'location_id': 24,
                                        'product_uom': 1,
                                        'location_dest_id': 24,
                                        'id': stock.id
                                    }
                                    update_transfer_records.append(
                                        transfer_update_values)
                                    prduct_update_value = {
                                        'product_id': product_id.id,
                                        'assign': user_id.id,
                                        'order':self.select_order_id.name
                                    }
                                    update_product_id.append(
                                        prduct_update_value)
                                query1 = """UPDATE stock_move SET picking_id=%(picking_id)s, 

                                                                                                                                              product_id=%(product_id)s, 
                                                                                                                                              name=%(name)s,
                                                                                                                                              fatag_bracode = %(fatag_bracode)s,
                                                                                                                                                category_id=%(category_id)s, 
                                                                                                                                                circle_name=%(circle_name)s,
                                                                                                                                                emp_mobile_no=%(emp_mobile_no)s,
                                                                                                                                                location_id=%(location_id)s,
                                                                                                                                                product_uom=%(product_uom)s,
                                                                                                                                                location_dest_id=%(location_dest_id)s
                                                                                                                                                WHERE id = %(id)s 
                                                                                                                     """

                                self.env.cr.executemany(query1,
                                                        update_transfer_records)
                                if self.select_order_id:

                                    query = """
                                                                                            UPDATE product_template
                                                                                           SET warehouse_emp_no = Null,
                                                                                           product_assigned_to = %(assign)s,
                                                                                           order_id = %(order)s
                                                                                           WHERE id = (SELECT product_tmpl_id
                                                                                                               FROM product_product WHERE id=%(product_id)s)
                                                                                                                                               """

                                    self.env.cr.executemany(query,
                                                            update_product_id)
                                else:

                                    query = """
                                                                                                                                UPDATE product_template
                                                                                                                               SET warehouse_emp_no = Null,
                                                                                                                               product_assigned_to = %(assign)s
                                                                                                                               WHERE id = (SELECT product_tmpl_id
                                                                                                                                                   FROM product_product WHERE id=%(product_id)s)
                                                                                                                                                                                   """

                                    self.env.cr.executemany(query,
                                                            update_product_id)

                                self.sudo().update(
                                    {'rs_destination_id': user_id.id,
                                     'rs_emp_no': self.rs_emp_mob_no,
                                     'rs_circle_id': self.rs_circle.id
                                     })

                                # create list for insert records to unacknowledged report
                                for product_id in avail_circle_product[:int(self.no_fastags)]:
                                    unawk_tag_obj = self.env['unacknowledged.report']
                                    a = unawk_tag_obj.create({'rs_name': self.name,
                                                              'rs_barcode': product_id.barcode,
                                                              'assigned_id': self.sudo().rs_destination_id.id,
                                                              'rs_from_emp_no': self.rs_user_id.rs_employee_id,
                                                              'rs_to_emp_no': self.sudo().rs_destination_id.rs_employee_id,
                                                              'rs_circle_id': self.rs_circle.id
                                                              })

                            else:

                                raise UserError(
                                    _('No available fastag'
                                      ))
                    template = self.env.ref(
                        'rn_vehical_class.inventory_trasfer_assigned_email_template')
                    self.env['mail.template'].browse(template.id).send_mail(
                        self.id)
                    self.select_order_id.tag_fulfillment_status = 'transferred'
                else:
                    raise UserError(_('Please Check Employee Mobile Number'))
        return True

    def wizard_action(self):
        if self.rs_destination_id:
            raise UserError(
                _('Already assign transfer,If you want to transfer please click on "Create" Button'))
        else:
            user_id = self.env['res.users'].search(
                [('login', '=', self.rs_emp_mob_no)])

            # circle mismatch
            user_em_id = self.env['res.users'].search(
                [('id', '=', self.rs_user_id.id)])
            if user_em_id.rs_designation == 'em':
                if self.rs_circle.id != user_id.rs_circle.id:
                    raise UserError(
                        'Mismatching circle name'
                    )

            update_transfer_records = []
            update_product_id = []

            if self.env.user.id == 673:
                if user_id:
                    if self.sequence_fastag == True:
                        if self.from_fastags == False:
                            raise UserError(
                                _('You can not create blank transfer Please enter beginning barcode .'))
                        if self.to_fastags == False:
                            raise UserError(
                                _('You need to provide end range of barcode .'))

                        from_bar = self.from_fastags
                        if len(from_bar) != 16:
                            raise UserError(
                                _('Please remove the hyphen in barcode or write proper barcode'))
                        from_first = from_bar[0:6]
                        from_sec = from_bar[6:9]
                        from_thr = from_bar[9:]
                        from_fastags = "%s-%s-%s" % (
                            from_first, from_sec, from_thr)

                        to_bar = self.to_fastags
                        if len(to_bar) != 16:
                            raise UserError(
                                _('Please remove the hyphen in barcode or write proper barcode'))
                        to_first = to_bar[0:6]
                        to_sec = to_bar[6:9]
                        to_thr = to_bar[9:]
                        to_fastags = "%s-%s-%s" % (
                            to_first, to_sec, to_thr)


                        from_barcode = self.env['product.product'].search(
                            [
                                ('fastag_sold', '=', 'no'),
                                ('rs_faulty_stag', '=', 'no'),
                                ('unlink_fastag', '=', False),
                                ('categ_id', '=', self.category_id.id),
                                ('warehouse_emp_no', '=',
                                 self.env.user.rs_employee_id),
                                ('barcode', '=', from_fastags)])
                        from_id = from_barcode.id
                        if not from_barcode:
                            raise UserError(
                                _('Barcode not available'))
                        to_barcode = self.env['product.product'].search(
                            [
                                ('fastag_sold', '=', 'no'),
                                ('rs_faulty_stag', '=', 'no'),
                                ('unlink_fastag', '=', False),
                                ('categ_id', '=', self.category_id.id),
                                ('warehouse_emp_no', '=',
                                 self.env.user.rs_employee_id),
                                ('barcode', '=', to_fastags)])
                        to_id = to_barcode.id
                        if not to_barcode:
                            raise UserError(
                                _('Barcode not available'))
                        ids = []
                        for id in range(from_id, to_id + 1):
                            ids.append(id)

                        avail_product = self.env[
                            'product.product'].search(
                            [
                                ('fastag_sold', '=', 'no'),
                                ('rs_faulty_stag', '=', 'no'),
                                ('unlink_fastag', '=', False),
                                ('categ_id', '=', self.category_id.id),
                                ('warehouse_emp_no', '=',
                                 self.env.user.rs_employee_id),
                                ('id', 'in', ids)])

                        if user_id.rs_designation == 'fastag_promoter':
                            records = self.env[
                                'product.product'].sudo().search_count(
                                [('product_assigned_to', '=',
                                  user_id.id),
                                 ('fastag_sold', '=', 'no'),
                                 ('rs_faulty_stag', '=', 'no'),
                                 ('unlink_fastag', '=', False)])

                            fastags_needed = len(avail_product) + int(records)
                            if int(records) >= 100:
                                raise UserError(
                                    _('Promoter %s fastag count is exceeds the limit 100',
                                      user_id.name))
                            elif int(fastags_needed) > 100:
                                raise UserError(
                                    _('Promoter %s Already there are %s FASTag you can assign %s !',
                                      user_id.name, int(records),
                                      100 - int(records)))

                        # TL Restriction
                        if user_id.rs_designation == 'fastag_tl':

                            records = self.env[
                                'product.product'].sudo().search_count(
                                [('product_assigned_to', '=',
                                  user_id.id),
                                 ('fastag_sold', '=', 'no'),
                                 ('rs_faulty_stag', '=', 'no'),
                                 ('unlink_fastag', '=', False)])

                            fastags_needed = len(avail_product) + int(records)
                            if int(records) >= 1000:
                                raise UserError(
                                    _('Promoter %s fastag count is exceeds the limit 100',
                                      user_id.name))
                            elif int(fastags_needed) > 1000:
                                raise UserError(
                                    _('Promoter %s Already there are %s FASTag you can assign %s !',
                                      user_id.name, int(records),
                                      1000 - int(records)))

                        # if len(avail_product) == ((int(to_id) - int(from_id)) + 1):
                        for product_id in avail_product:
                            stock = self.env['stock.move'].sudo().create({})
                            transfer_update_values = {
                                'picking_id': self.id,
                                'product_id': product_id.id,
                                'name': product_id.name,
                                'fatag_bracode': product_id.barcode,
                                'category_id': product_id.categ_id.id,
                                'circle_name': self.rs_circle.id,
                                'emp_mobile_no': self.rs_emp_mob_no,
                                'location_id': 24,
                                'product_uom': 1,
                                'location_dest_id': 24,
                                'id': stock.id
                            }
                            update_transfer_records.append(
                                transfer_update_values)
                            prduct_update_value = {
                                'product_id': product_id.id,
                                'assign': user_id.id
                            }
                            update_product_id.append(prduct_update_value)
                        query1 = """UPDATE stock_move SET picking_id=%(picking_id)s, 

                                                                                                                 product_id=%(product_id)s, 
                                                                                                                 name=%(name)s,
                                                                                                                 fatag_bracode = %(fatag_bracode)s,
                                                                                                                   category_id=%(category_id)s, 
                                                                                                                   circle_name=%(circle_name)s,
                                                                                                                   emp_mobile_no=%(emp_mobile_no)s,
                                                                                                                   location_id=%(location_id)s,
                                                                                                                   product_uom=%(product_uom)s,
                                                                                                                   location_dest_id=%(location_dest_id)s
                                                                                                                   WHERE id = %(id)s 
                                                                                        """

                        self.env.cr.executemany(query1,
                                                update_transfer_records)

                        query = """
                                                           UPDATE product_template
                                                          SET warehouse_emp_no = Null,
                                                          product_assigned_to = %(assign)s
                                                          WHERE id = (SELECT product_tmpl_id
                                                                              FROM product_product WHERE id=%(product_id)s)
                                                                                                              """

                        self.env.cr.executemany(query,
                                                update_product_id)

                        self.sudo().update(
                            {'rs_destination_id': user_id.id,
                             'rs_emp_no': self.rs_emp_mob_no,
                             'rs_circle_id': self.rs_circle.id
                             })

                        # create list for insert records to unacknowledged report
                        for product_id in avail_product:
                            unawk_tag_obj = self.env['unacknowledged.report']
                            a = unawk_tag_obj.create({'rs_name': self.name,
                                                      'rs_barcode': product_id.barcode,
                                                      'assigned_id': self.sudo().rs_destination_id.id,
                                                      'rs_from_emp_no': self.rs_user_id.rs_employee_id,
                                                      'rs_to_emp_no': self.sudo().rs_destination_id.rs_employee_id,
                                                      'rs_circle_id': self.rs_circle.id
                                                      })
                        # else:
                        #
                        #     raise UserError(
                        #         _('No available fastag'
                        #           ))
                    template = self.env.ref(
                        'rn_vehical_class.inventory_trasfer_assigned_email_template')
                    self.env['mail.template'].browse(template.id).send_mail(
                        self.id)

                else:
                    raise UserError(_('Please Check Employee Mobile Number'))
            else:

                if user_id:

                    if self.sequence_fastag == True:
                        if self.from_fastags == False:
                            raise UserError(
                                _('You can not create blank transfer Please enter beginning barcode .'))
                        if self.to_fastags == False:
                            raise UserError(
                                _('You need to provide end range of barcode .'))

                        from_bar = self.from_fastags
                        if len(from_bar) != 16:
                            raise UserError(
                                _('Please remove the hyphen in barcode or write proper barcode'))
                        from_first = from_bar[0:6]
                        from_sec = from_bar[6:9]
                        from_thr = from_bar[9:]
                        from_fastags = "%s-%s-%s" % (
                            from_first, from_sec, from_thr)

                        to_bar = self.to_fastags
                        if len(to_bar) != 16:
                            raise UserError(
                                _('Please remove the hyphen in barcode or write proper barcode'))
                        to_first = to_bar[0:6]
                        to_sec = to_bar[6:9]
                        to_thr = to_bar[9:]
                        to_fastags = "%s-%s-%s" % (
                            to_first, to_sec, to_thr)


                        from_barcode = self.env['product.product'].search(
                            [
                                ('fastag_sold', '=', 'no'),
                                ('rs_faulty_stag', '=', 'no'),
                                ('unlink_fastag', '=', False),
                                ('categ_id', '=', self.category_id.id),
                                ('warehouse_emp_no', '=',
                                 self.env.user.rs_employee_id),
                                ('barcode', '=', from_fastags)])
                        from_id = from_barcode.id
                        if not from_barcode:
                            raise UserError(
                                _('Barcode not available'))
                        to_barcode = self.env['product.product'].search(
                            [
                                ('fastag_sold', '=', 'no'),
                                ('rs_faulty_stag', '=', 'no'),
                                ('unlink_fastag', '=', False),
                                ('categ_id', '=', self.category_id.id),
                                ('warehouse_emp_no', '=',
                                 self.env.user.rs_employee_id),
                                ('barcode', '=', to_fastags)])
                        to_id = to_barcode.id
                        if not to_barcode:
                            raise UserError(
                                _('Barcode not available'))
                        ids = []
                        for id in range(from_id, to_id + 1):
                            ids.append(id)

                        avail_product = self.env[
                            'product.product'].search(
                            [
                                ('fastag_sold', '=', 'no'),
                                ('rs_faulty_stag', '=', 'no'),
                                ('unlink_fastag', '=', False),
                                ('categ_id', '=', self.category_id.id),
                                ('warehouse_emp_no', '=',
                                 self.env.user.rs_employee_id),
                                ('id', 'in', ids)])

                        if user_id.rs_designation == 'fastag_promoter':
                            records = self.env[
                                'product.template'].sudo().search_count(
                                [('product_assigned_to', '=',
                                  user_id.id),
                                 ('fastag_sold', '=', 'no'),
                                 ('rs_faulty_stag', '=', 'no'),
                                 ('unlink_fastag', '=', False)])

                            fastags_needed = len(avail_product) + int(records)
                            if int(records) >= 100:
                                raise UserError(
                                    _('Promoter %s fastag count is exceeds the limit 100',
                                      user_id.name))
                            elif int(fastags_needed) > 100:
                                raise UserError(
                                    _('Promoter %s Already there are %s FASTag you can assign %s !',
                                      user_id.name, int(records),
                                      100 - int(records)))

                        # TL Restriction
                        if user_id.rs_designation == 'fastag_tl':

                            records = self.env[
                                'product.template'].sudo().search_count(
                                [('product_assigned_to', '=',
                                  user_id.id),
                                 ('fastag_sold', '=', 'no'),
                                 ('rs_faulty_stag', '=', 'no'),
                                 ('unlink_fastag', '=', False)])

                            fastags_needed = len(avail_product) + int(records)
                            if int(records) >= 1000:
                                raise UserError(
                                    _('Promoter %s fastag count is exceeds the limit 100',
                                      user_id.name))
                            elif int(fastags_needed) > 1000:
                                raise UserError(
                                    _('Promoter %s Already there are %s FASTag you can assign %s !',
                                      user_id.name, int(records),
                                      1000 - int(records)))

                        # if len(avail_product) == (
                        #         (int(to_id) - int(from_id)) + 1):
                        for product_id in avail_product:
                            stock = self.env['stock.move'].sudo().create({})
                            transfer_update_values = {
                                'picking_id': self.id,
                                'product_id': product_id.id,
                                'name': product_id.name,
                                'fatag_bracode': product_id.barcode,
                                'category_id': product_id.categ_id.id,
                                'circle_name': self.rs_circle.id,
                                'emp_mobile_no': self.rs_emp_mob_no,
                                'location_id': 24,
                                'product_uom': 1,
                                'location_dest_id': 24,
                                'id': stock.id
                            }
                            update_transfer_records.append(
                                transfer_update_values)
                            prduct_update_value = {
                                'product_id': product_id.id,
                                'assign': user_id.id
                            }
                            update_product_id.append(prduct_update_value)
                        query1 = """UPDATE stock_move SET picking_id=%(picking_id)s, 

                                                                                                                                                 product_id=%(product_id)s, 
                                                                                                                                                 name=%(name)s,
                                                                                                                                                 fatag_bracode = %(fatag_bracode)s,
                                                                                                                                                   category_id=%(category_id)s, 
                                                                                                                                                   circle_name=%(circle_name)s,
                                                                                                                                                   emp_mobile_no=%(emp_mobile_no)s,
                                                                                                                                                   location_id=%(location_id)s,
                                                                                                                                                   product_uom=%(product_uom)s,
                                                                                                                                                   location_dest_id=%(location_dest_id)s
                                                                                                                                                   WHERE id = %(id)s 
                                                                                                                        """

                        self.env.cr.executemany(query1,
                                                update_transfer_records)

                        query = """
                                                                                           UPDATE product_template
                                                                                          SET warehouse_emp_no = Null,
                                                                                          product_assigned_to = %(assign)s
                                                                                          WHERE id = (SELECT product_tmpl_id
                                                                                                              FROM product_product WHERE id=%(product_id)s)
                                                                                                                                              """

                        self.env.cr.executemany(query,
                                                update_product_id)

                        self.sudo().update(
                            {'rs_destination_id': user_id.id,
                             'rs_emp_no': self.rs_emp_mob_no,
                             'rs_circle_id': self.rs_circle.id
                             })

                        # create list for insert records to unacknowledged report
                        for product_id in avail_product[:int(self.no_fastags)]:
                            unawk_tag_obj = self.env['unacknowledged.report']
                            a = unawk_tag_obj.create({'rs_name': self.name,
                                                      'rs_barcode': product_id.barcode,
                                                      'assigned_id': self.sudo().rs_destination_id.id,
                                                      'rs_from_emp_no': self.rs_user_id.rs_employee_id,
                                                      'rs_to_emp_no': self.sudo().rs_destination_id.rs_employee_id,
                                                      'rs_circle_id': self.rs_circle.id
                                                      })
                        # else:
                        #
                        #     raise UserError(
                        #         _('No available fastag'
                        #           ))
                    template = self.env.ref(
                        'rn_vehical_class.inventory_trasfer_assigned_email_template')
                    self.env['mail.template'].browse(template.id).send_mail(
                        self.id)

                else:
                    raise UserError(_('Please Check Employee Mobile Number'))
        return True

    @api.onchange('fastag_count')
    def _onchange_circledomain(self):
        for rec in self:
            rec.fastag_count1 = rec.fastag_count
            
    def get_pro_count(self):
        # product_ids = self.env['product.template'].search(
        #     [('fastag_sold', '=', 'yes')])
        for rec in self:
            f_count = 0
            s_count = 0
            ft_count = 0
            for line in rec.move_ids_without_package:
                if line.fastag_sold == 'yes' or line.fastag_sold == 'no':
                    f_count += 1
                # product_id = line.sudo().product_id.product_tmpl_id
                # if product_id in product_ids:
                if line.fastag_sold == 'yes':
                        s_count += 1
                if line.rs_faulty_stag == 'yes':
                    ft_count += 1
            rec.fastag_count = f_count
            rec.fastag_sold = s_count
            rec.fastag_faulty = ft_count
            rec.fastag_count1 = rec.fastag_count

    @api.model
    def default_get(self, fields):
        res = super(StockPicking, self).default_get(fields)
        today = date.today()
        lst_date = str(today).split("-")
        today = lst_date[2] + "/" + lst_date[1] + "/" + lst_date[0]
        res.update({'picking_type_id': 7, 'fastag_trnsfr_date': today})
        return res

    @api.onchange('rs_destination_id')
    def get_office_address(self):
        self.rs_office_addres = self.rs_destination_id.rs_office_addres

    @api.model
    def create(self, vals):
        # query = """DELETE  FROM stock_picking WHERE rs_destination_id is Null"""
        # self.env.cr.execute(query)
        # transfer_id = self.env['transfer.report']
        today = date.today()
        lst_date = str(today).split("-")
        today = lst_date[2] + "/" + lst_date[1] + "/" + lst_date[0]
        res = super(StockPicking, self).create(vals)
        user_id = self.env['res.users'].search(
            [('login', '=', self.rs_emp_mob_no)])
        # if self.move_ids_without_package.emp_mobile_no:
        # if vals['move_ids_without_package']:
        # res = super(StockPicking, self).create(vals)
        for res in res:
            trans_list = []
            for move_id in res.move_ids_without_package:
                # product internal refernce
                product_id = move_id.product_id
                product_tem_id = self.env['product.template'].search(
                    [('barcode', '=', product_id.barcode)])
                # product_tem_id.sudo().write({'internal_ref': vals['name']})
                # product_id.sudo().write({'internal_ref': vals['name']})

                # product circle mismatch
                if move_id.product_id.circle_name != move_id.circle_name:
                    raise UserError(
                        _('%s circle name is not match with move line circle',
                          move_id.product_id.name))

                user_id = self.env['res.users'].search(
                    [('login', '=', move_id.emp_mobile_no)])

                # promoter circle mismath
                if user_id.rs_circle != move_id.circle_name:
                    raise UserError(
                        _('%s circle name is not match with move line circle',
                          user_id.name))

                #    promoter Restriction
                if user_id.rs_designation == 'fastag_promoter':
                    records = self.env['product.template'].sudo().search_count(
                        [('warehouse_emp_no', '=', user_id.rs_employee_id)])
                    if int(records) >= 101:
                        raise UserError(
                            _('Promoter %s Already there are %s FASTag you can assign only %s !',
                              user_id.name, int(records), int(records) - 100))

                #   TL Restriction
                if user_id.rs_designation == 'fastag_tl':
                    records = self.env['product.template'].sudo().search_count(
                        [('warehouse_emp_no', '=', user_id.rs_employee_id)])
                    if int(records) >= 1001:
                        raise UserError(
                            _('TL %s Already there are %s FASTag you can assign only %s !',
                              user_id.name, int(records), int(records) - 1000))
                if user_id:
                    res.sudo().update({'rs_destination_id': user_id.id,
                                       'rs_emp_no': move_id.emp_mobile_no,
                                       'rs_circle_id': move_id.circle_name})
                    print(self.name)
                    # move_id.product_id.product_tmpl_id.sudo().update(
                    #     {'warehouse_emp_no': user_id.rs_employee_id,
                    #      'product_assigned_to':user_id.id,
                    #      'assigned_to_mob':user_id.login
                    #      })
                    move_id.product_id.product_tmpl_id.sudo().update(
                        {'warehouse_emp_no': None
                         })
                if res.rs_destination_id:
                    self.sudo().update({'rs_destination_id': user_id.id,
                                        'rs_emp_no': self.rs_emp_mob_no,
                                        })
                    template = self.env.ref(
                        'rn_vehical_class.inventory_trasfer_assigned_email_template')
                    self.env['mail.template'].browse(template.id).send_mail(
                        res.id)
                # query = """DELETE  FROM stock_picking WHERE rs_destination_id = Null"""
                # self.env.cr.execute(query)
            # if not res.fastag_count:
            #     raise UserError(
            #         _('Zero fastag count'))
            # else:
            return res
        # else:
        #     if vals['rs_filter_fastag'] == True:
        #         print(vals)
        #         print('self',self)
        #         res = super(StockPicking, self).create(vals)
        #         for rec in res:
        #             print('res',rec)
        #         return res
        #     else:
        #         print('self', self)
        #         vals['name'] = self.env['ir.sequence'].next_by_code(
        #             'stock.picking.type')
        #         result = super(StockPicking, self).create(vals)
        #         return result
    # query = """DELETE  FROM stock_picking WHERE name = ''"""
    # self.env.cr.execute(query)


class StockMove(models.Model):
    _inherit = "stock.move"

    rs_fastage_dummy = fields.Many2many('vehical.class', string="Fastag")
    tag_id = fields.Char(related='product_id.default_code', string="Tag ID")
    rs_faulty_stag = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                      string="FAULTY", default='no')
    fastag_sold = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                   string="SOLD", default='no')
    fatag_bracode = fields.Char(related='product_id.barcode',
                                string="FASTAG BARCODE")
    circle_name = fields.Many2one('rs.circle.name', string="CIRCLE NAME")
    date_of_dispatch = fields.Char(string="DATE OF DISPATCH",
                                   compute='_set_date')
    consignment_no = fields.Char(string="CONSIGNMENT NO",
                                 default="Hand transfer")
    delivery_partner = fields.Char(string="DELIVERY PARTNER",
                                   default="Self Transfer")
    emp_mobile_no = fields.Char(string="EMP MOB NO", copy=False)
    unlink_fastag = fields.Boolean(related='product_id.unlink_fastag',
                                   string="Unlink",store=True)
    # reference = fields.Boolean()
    category_id = fields.Many2one('product.category', string="Tag Class")
    date = fields.Datetime(required=False)
    company_id = fields.Many2one(required=False)
    product_uom_qty = fields.Float(required=False)
    procure_method = fields.Selection(required=False)
    name = fields.Char(required=False)
    location_dest_id = fields.Many2one(required=False)
    location_id = fields.Many2one(required=False)
    product_id = fields.Many2one(required=False)
    product_uom = fields.Many2one(required=False)
    check_move_line = fields.Boolean(string='Check')


    # def _check_move_line(self):
    #     self.check_move_line = True
    #     query = """DELETE FROM stock_move WHERE fatag_bracode is null"""
    #     self.env.cr.execute(query)

    @api.onchange('product_id')
    def _onchange_circle_name(self):
        user_id = self.env['res.users'].search(
            [('id', '=', self.env.user.id)])
        if user_id.rs_designation == 'em':
            listids = []
            if user_id.rs_circle_ids:
                for each in user_id.rs_circle_ids:
                    listids.append(each.id)
                    print(each.id)
                res = {}
                res['domain'] = {'circle_name': [('id', 'in', listids)]}
                return res
        else:
            res = {}
            res['domain'] = {'circle_name': [('id', '=', user_id.rs_circle.id)]}
            return res

    @api.onchange('product_id')
    def fix_current_date(self):
        today = date.today()
        lst_date = str(today).split("-")
        self.date_of_dispatch = lst_date[2] + "/" + lst_date[1] + "/" + \
                                lst_date[0]

    def _set_date(self):
        today = date.today()
        lst_date = str(today).split("-")
        self.date_of_dispatch = lst_date[2] + "/" + lst_date[1] + "/" + \
                                lst_date[0]
    @api.model
    def create(self, vals):
        res = super(StockMove, self).create(vals)
        return res


    @api.onchange('fastag_sold')
    def transfer_change(self):
        bl_count = 0
        for rec in self:
            if rec.fastag_sold == 'yes':
                transfer_id = self.env['all.transfer.report'].search(
                    [('name', '=', rec.fatag_bracode)])
                if transfer_id:
                    for rec in transfer_id:
                        if rec:
                            rec.write({'rs_tag_sold': 'yes'})
                            # bl_count = 0
                            # rec.rs_balance_stock= bl_count
            else:
                if rec.fastag_sold == 'no':
                    transfer_id = self.env['all.transfer.report'].search(
                        [('name', '=', rec.fatag_bracode)])
                    if transfer_id:
                        for rec in transfer_id:
                            if rec:
                                rec.write({'rs_tag_sold': 'no'})

    @api.onchange('rs_faulty_stag')
    def stage_change(self):
        for rec in self:
            if rec.rs_faulty_stag == 'yes':
                transfer_id = self.env['all.transfer.report'].search(
                    [('name', '=', rec.fatag_bracode)])
                if transfer_id:
                    for rec in transfer_id:
                        if rec:
                            rec.write({'rs_fault_tags': 'yes'})
            else:
                if rec.rs_faulty_stag == 'no':
                    transfer_id = self.env['all.transfer.report'].search(
                        [('name', '=', rec.fatag_bracode)])
                    if transfer_id:
                        for rec in transfer_id:
                            if rec:
                                rec.write({'rs_fault_tags': 'no'})

class ProductTemplate(models.Model):
    _inherit = "product.template"
    _order = "inword_date desc, id desc"

    rs_vendor_name = fields.Integer(string="Vendor ID")
    inword_date = fields.Date(string='Uploded Date')
    category_id = fields.Many2many('res.partner.category', 'product_id',string="Tag Color",store=True)
    rs_tag_id = fields.Char(string='Vehicle Type ID')
    partner_id = fields.Many2one('res.partner', string='Vendor Name',
                                 domain="[('supplier_rank','=',1)]")
    assigned_to_mob = fields.Char(striassigned_to_mobng="Promoter Mobile")
    fastag_sold = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                   string="Sold", default='no')
    warehouse_emp_no = fields.Char(string="Employee No")
    rs_faulty_stag = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                      string="Faulty", default='no')
    product_assigned_to = fields.Many2one('res.users', copy=False,
                                          tracking=True,
                                          string='Assigned To')
    unlink_fastag = fields.Boolean(string="Unlink")
    internal_ref = fields.Char(string="Internal Ref")
    unlink_amount = fields.Float(string="Amount")
    category_id_list = fields.Char()
    order_id = fields.Char(string="Order Ref")
    unlink_amount2 = fields.Integer(string="Amount")

    _sql_constraints = [
        ('barcode_uniq', 'Check(1=1)',
         'Name must be unique per company!'),
    ]

    @api.onchange('category_id')
    def _onchange_category_id(self):
        print('category_list')
        if self.category_id:
            category_list = ','.join([p.name for p in self.category_id])
            self.category_id_list = category_list
        else:
            self.category_id_list = ''

    def product_update(self):
        query = """UPDATE product_template SET warehouse_emp_no = 'V5257501'
                                                             WHERE product_assigned_to = 4437"""
        self.env.cr.execute(query)


    def report_update(self):
        product_id = self.search([('fastag_sold', '=', 'no')])
        product = []
        for rec in product_id:
            values= {'bar': rec.barcode}
            product.append(values)
        query1 = """DELETE FROM all_transfer_report WHERE name = %(bar)s"""
        self.env.cr.executemany(query1, product)
        query2 = """DELETE FROM transfer_report WHERE name = %(bar)s"""
        self.env.cr.executemany(query2,product)

    def name_get(self):
        result = []
        for rec in self:
            str = rec.barcode
            res_first = str[14:]
            result.append((rec.id, '%s - %s' % (rec.name, res_first)))
        return result



    # @api.model
    # def create(self, vals):
    #     res = super(ProductTemplate, self).create(vals)
    #     product_count = self.search_count([('warehouse_emp_no','=',self.env.user.rs_employee_id)])
    #     if product_count > 7000:
    #         raise ValidationError("yOU CAN IMPORT ONLY 7000 PRODUCT")
    #     return res
    # @api.constrains('name')
    # def unique_name(self):
    #     product_id = self.search([('name','=',self.name),('id','!=',self.id)])
    #     if product_id:
    #         raise ValidationError(_("Name must be unique"))
    # @api.onchange('fastag_sold')
    # def _onchange_fastag_sold(self):
    #     if self.fastag_sold == 'yes':
    #         picking_id = self.env['stock.picking'].search(
    #             [('rs_destination_id', '=', self.product_assigned_to.id)])
    #         if picking_id:
    #             move_id = picking_id.move_ids_without_package
    #             for rec in move_id:
    #                 if rec.fatag_bracode == self.barcode:
    #                     rec.sudo().update({'fastag_sold': 'yes'
    #                                        })
    #         transfer_id = self.env['all.transfer.report'].search(
    #             [('name', '=', self.barcode)])
    #         transfer_id.sudo().update({'rs_tag_sold': 'yes'
    #                                    })
    #     else:
    #         picking_id = self.env['stock.picking'].search(
    #             [('rs_destination_id', '=', self.product_assigned_to.id)])
    #         if picking_id:
    #             move_id = picking_id.move_ids_without_package
    #             for rec in move_id:
    #                 if rec.fatag_bracode == self.barcode:
    #                     rec.sudo().update({'fastag_sold': 'no'
    #                                        })
    #         transfer_id = self.env['all.transfer.report'].search(
    #             [('name', '=', self.barcode)])
    #         transfer_id.sudo().update({'rs_tag_sold': 'no'
    #                                    })

    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        if self.fastag_sold == 'yes':
            picking_id = self.env['stock.picking'].search(
                [('rs_destination_id', '=', self.product_assigned_to.id)])
            print('picking', picking_id)
            if picking_id:
                move_id = picking_id.move_ids_without_package
                for rec in move_id:
                    if rec.fatag_bracode == self.barcode:
                        rec.sudo().write({'fastag_sold': 'yes'
                                          })
            transfer_id = self.env['all.transfer.report'].search(
                [('name', '=', self.barcode)])
            print('transfer', transfer_id)
            # _logger.info("transfer_id are--->>>>>: ",transfer_id)
            transfer_id.sudo().update({'rs_tag_sold': 'yes'
                                       })
        if self.rs_faulty_stag == 'yes':
            picking_id = self.env['stock.picking'].search(
                [('rs_destination_id', '=', self.product_assigned_to.id)])
            print('picking', picking_id)
            if picking_id:
                move_id = picking_id.move_ids_without_package
                for rec in move_id:
                    if rec.fatag_bracode == self.barcode:
                        rec.sudo().write({'rs_faulty_stag': 'yes'
                                          })
            transfer_id = self.env['all.transfer.report'].search(
                [('name', '=', self.barcode)])
            print('transfer', transfer_id)
            # _logger.info("transfer_id are--->>>>>: ",transfer_id)
            transfer_id.sudo().update({
                                       'rs_fault_tags':'yes'
                                       })


        if self.fastag_sold == 'no':
            picking_id = self.env['stock.picking'].search(
                [('rs_destination_id', '=', self.product_assigned_to.id)])
            if picking_id:
                move_id = picking_id.move_ids_without_package
                for rec in move_id:
                    if rec.fatag_bracode == self.barcode:
                        rec.sudo().update({'fastag_sold': 'no'
                                           })
            transfer_id = self.env['all.transfer.report'].search(
                [('name', '=', self.barcode)])
            # _logger.info("write--->>>transfer_id are--->>>>>: ",transfer_id)
            transfer_id.sudo().update({'rs_tag_sold': 'no'
                                       })

        if self.rs_faulty_stag == 'no':
            picking_id = self.env['stock.picking'].search(
                [('rs_destination_id', '=', self.product_assigned_to.id)])
            print('picking', picking_id)
            if picking_id:
                move_id = picking_id.move_ids_without_package
                for rec in move_id:
                    if rec.fatag_bracode == self.barcode:
                        rec.sudo().write({'rs_faulty_stag': 'no'
                                          })
            transfer_id = self.env['all.transfer.report'].search(
                [('name', '=', self.barcode)])
            print('transfer', transfer_id)
            # _logger.info("transfer_id are--->>>>>: ",transfer_id)
            transfer_id.sudo().update({
                'rs_fault_tags': 'no'
            })

        return True


class ProductProduct(models.Model):
    _inherit = "product.product"
    _order = "inword_date desc, id desc"

    apna_id = fields.Char(string="Apna ID")


    @api.model
    def create(self, vals):
        res = super(ProductProduct, self).create(vals)
        res.update({'circle_name': res.product_tmpl_id.circle_name.id})
        return res

    def name_get(self):
        result = []
        for rec in self:
            if rec.barcode:
                str = rec.barcode
                res_first = str[13:]
                result.append((rec.id, '%s - %s' % (rec.name, res_first)))
            else:
                result.append((rec.id, '%s - %s' % (rec.name, rec.barcode)))
        return result

class seequence_wizard(models.TransientModel):

    _name = 'seequence.wizard'

    sold = fields.Text(readonly=True)
    fault = fields.Text(readonly=True)
    unlink = fields.Text(readonly=True)


    def method(self):
        picking_id = self.env['stock.picking'].browse(self._context.get('active_ids'))
        return picking_id.wizard_action()

    def cancel(self):
        print('cancel')

class Productcategorye(models.Model):
    _inherit = "res.partner.category"

    product_id = fields.Many2one('product.template')

class barcode_wizard(models.TransientModel):
    _name = 'barcode.wizard'

    barcode = fields.Char()
    seequence_wizard_id = fields.Many2one('seequence.wizard')

