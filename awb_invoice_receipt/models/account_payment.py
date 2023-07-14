from odoo import api, fields, models

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    """
        Added new field to keep track of how many times the report is generated.    
    """

    print_increment = fields.Integer(default=0)

    def _print_increment(self):
        """
            This function is called everytime the report is being generated.
        """
        self.print_increment += 1
        print('print_increment >>> ', self.print_increment)

class ReportAccountPaymentReceipt(models.AbstractModel):
    """
        Created this abstract model since it does not exist in base.
            It is just used to call the _print_increment() function in account.payment
            to keep track of how many times the report is generated.
        
        If print_increment > 1, report is now considered a REPRINT.
        _get_report_values() is called everytime the print button is pressed and a report is
            being generated.
    """

    _name = 'report.account.report_payment_receipt'
    _description = 'Account report for payment receipt'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.payment'].browse(docids)
        
        docs._print_increment()

        return {
            'doc_ids': docids,
            'doc_model': 'account.payment',
            'docs': docs,
        }