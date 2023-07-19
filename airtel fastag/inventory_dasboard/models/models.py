from odoo import models, fields, api
from odoo.osv import expression


class Inventoryenu(models.Model):
    _name = "inventory.dashboard"
    _description = "dashboard Menu"
    _rec_name = "name"

    name = fields.Char(string="Name")
    menu_id = fields.Many2one('ir.ui.menu', string="Menu")
    client_action = fields.Many2one('ir.actions.client')

    @api.model
    def create(self, vals):
        """This code is to create menu"""
        values = {
            'name': vals['name'],
            'tag': 'inventory_dashboard',
        }
        action_id = self.env['ir.actions.client'].create(values)
        vals['client_action'] = action_id.id
        menu_id = self.env['ir.ui.menu'].create({
            'name': vals['name'],
            'parent_id': vals['menu_id'],
            'action': 'ir.actions.client,%d' % (action_id.id,)
        })
        return super(Inventoryenu, self).create(vals)

class HrEmployee(models.Model):
    _inherit = "stock.picking"

    @api.model
    def get_transfer_list(self):
        transfer_count_list = []
        transfer_id = self.env['stock.picking'].search_count([])
        transfer_assign_id = self.env['stock.picking'].search_count(
            [('rs_state','=','assign')])
        transfer_ackw_id = self.env['stock.picking'].search_count(
            [('rs_state', '=', 'ackw')])
        transfer_cancel_id = self.env['stock.picking'].search_count(
            [('rs_state', '=', 'declined')])
        transfer_decline_id = self.env['stock.picking'].search_count(
            [('rs_state', '=', 'cancel')])
        transfer_count_list .append(transfer_id)
        transfer_count_list .append(transfer_assign_id)
        transfer_count_list .append(transfer_ackw_id)
        transfer_count_list .append(transfer_cancel_id)
        transfer_count_list .append(transfer_decline_id)

        return  transfer_count_list

    @api.model
    def show_transfer_lists(self):
        all_transfer_list = []
        all_transfer = self.env['stock.picking'].search([])
        for rec in all_transfer:
            all_transfer_list.append(rec.id)
        return  all_transfer_list

    @api.model
    def show_assign_transfer(self):
        assign_transfer_list = []
        assigne_transfer = self.env['stock.picking'].search(
            [('rs_state', '=', 'assign')])
        for assign in assigne_transfer:
            assign_transfer_list.append(assign.id)
        return assign_transfer_list

    @api.model
    def show_ackw_transfer(self):
        assign_transfer_list = []
        assigne_transfer = self.env['stock.picking'].search(
            [('rs_state', '=', 'ackw')])
        for assign in assigne_transfer:
            assign_transfer_list.append(assign.id)
        return assign_transfer_list

    @api.model
    def show_cancel_transfer(self):
        assign_transfer_list = []
        assigne_transfer = self.env['stock.picking'].search(
            [('rs_state', '=', 'cancel')])
        for assign in assigne_transfer:
            assign_transfer_list.append(assign.id)
        return assign_transfer_list

    @api.model
    def show_declined_transfer(self):
        assign_transfer_list = []
        assigne_transfer = self.env['stock.picking'].search(
            [('rs_state', '=', 'declined')])
        for assign in assigne_transfer:
            assign_transfer_list.append(assign.id)
        return assign_transfer_list


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def get_product_list(self):
        product_count_list = []
        product_id = self.env['product.template'].search_count([])
        sold_id = self.env['product.template'].search_count(
            [('fastag_sold','=','yes')])
        faulty_id = self.env['product.template'].search_count(
            [('rs_faulty_stag', '=', 'yes')])
        unlink_id = self.env['product.template'].search_count(
            [('unlink_fastag', '=', True)])
        avail_id = self.env['product.template'].search_count(
            [('unlink_fastag', '=', False),('fastag_sold','=','no'),('rs_faulty_stag', '=', 'no')])
        product_count_list.append(product_id)
        product_count_list.append(sold_id)
        product_count_list.append(faulty_id)
        product_count_list.append(unlink_id)
        product_count_list.append(avail_id)
        return product_count_list

class TransferRepport(models.Model):
    _inherit = "all.transfer.report"

    @api.model
    def get_report_list(self):
        report_count_list = []
        report_id = self.env['all.transfer.report'].search_count([])
        report_sold_id = self.env['all.transfer.report'].search_count([('rs_tag_sold','=','yes')])
        report_faulty_id = self.env['all.transfer.report'].search_count([('rs_fault_tags','=','yes')])
        report_unlink_id = self.env['all.transfer.report'].search_count([('rs_unlinked', '=', True)])
        report_count_list.append(report_id)
        report_count_list.append(report_sold_id)
        report_count_list.append(report_faulty_id)
        report_count_list.append(report_unlink_id)

        return report_count_list