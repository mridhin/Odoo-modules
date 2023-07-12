from odoo import models, fields, api, _
from odoo.osv import expression
from odoo.exceptions import ValidationError, Warning, UserError
from datetime import datetime, date


class AllTaransferReport(models.Model):
    _name = 'all.transfer.report'
    _description = 'All Transfer Report'
    _order = "id desc"

    name = fields.Char(string="Barcode No")
    rs_assigned_id = fields.Many2one('res.users', copy=False, tracking=True, string='Assigned To')
    rs_emp_name = fields.Char(string="Employee Name")
    rs_designation = fields.Char(string="Designation")
    rs_emp_no = fields.Char(string="From EMP I+D")
    rs_to_emp_no = fields.Char(string="To EMP ID")
    rs_circle = fields.Many2one('rs.circle.name', string="Circle Name")
    rs_assi_date = fields.Char(string="Assigned Date")
    rs_tag_transfer = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Tag Transfer/Tag Issued")
    rs_tag_sold = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Tag Sold")
    rs_fault_tags = fields.Selection([('yes', 'Yes'), ('no', 'No')],string="Faulty Tags")
    rs_unlinked = fields.Boolean(string="Unlinked Tags")
    rs_balance_stock = fields.Integer(string="Balance Stock", compute="_compute_total_stock_bal",store="True")
    rs_name = fields.Char(string="Transfer Ref")
    product_amount = fields.Integer(string='Amount')
    tag_class = fields.Many2one('product.category', string='Tag Class')

    def unlinked_tag(self):
        product_id = self.env['product.product'].search([('unlink_fastag', '=', True)])
        for rec in product_id:
            query = """UPDATE all_transfer_report SET rs_unlinked = %(unlink)s WHERE name = %(bar)s """
            self.env.cr.execute(query, {'unlink': True,
                                        'bar': rec.barcode})

    def update_tagclass(self):
        report_id = self.search([('tag_class', '=', False)])
        for rec in report_id:
            query = """UPDATE all_transfer_report
                                                SET tag_class = (SELECT categ_id  FROM product_template WHERE id = (SELECT product_tmpl_id FROM product_product
                                                WHERE barcode = (SELECT name FROM all_transfer_report WHERE id = %(id)s)))
                                                 WHERE id = %(id)s """
            self.env.cr.execute(query, {'id':rec.id})

    @api.depends('rs_assigned_id','rs_tag_sold')
    def _compute_total_stock_bal(self):
        for t in self:
            if t.name:
                t.rs_balance_stock = t.mapped('rs_assigned_id.id').count(t.rs_assigned_id.id)
            if t.rs_tag_sold == 'yes' or t.rs_fault_tags == 'yes' or t.rs_unlinked == 'yes'  :
                t.rs_balance_stock -= 1



    # @api.depends('name', 'rs_tag_sold')
    # def _compute_total_stock_bal(self):
    #     for t in self:
    #         if t.name:
    #             t.rs_balance_stock = t.mapped('name').count(t.name)
    #         if t.rs_tag_sold == 'yes':
    #             t.rs_balance_stock -= 1
                