from odoo import api, fields, models

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    journal_type_selection = fields.Selection(
        [('si', 'Sales Invoice'),
         ('bs', 'Billing Statement'), 
         ('or', 'Official Receipt'),
         ('cr', 'Collection Receipt')
         ],
    )

    journal_remarks = fields.Char(compute='_get_journal_remarks', readonly=True)

    @api.depends('journal_type_selection')
    def _get_journal_remarks(self):
        for record in self:
            if record.journal_type_selection == 'bs' or record.journal_type_selection == 'cr':
                record.journal_remarks = 'THIS DOCUMENT IS NOT VALID FOR CLAIM OF INPUT TAX'
            else:
                record.journal_remarks = ''