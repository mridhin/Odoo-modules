from odoo import _, api, fields, models
import math

class IrSequence(models.Model):
    _inherit = "ir.sequence"

    reset_counter = fields.Integer()

    def _check_if_max(self):
        max_number = self._get_highest_num(self.padding)
        if(max_number < self.number_next_actual):
            value = {
                'number_next': 1
            }
            self.write(value)
            self.reset_counter += 1

    def _get_highest_num(self, digits=0):
        return int(math.pow(10, digits) - 1)

    def _next(self, sequence_date=None):
        self._check_if_max() #call first before incrementing
        return super(IrSequence, self)._next(sequence_date)



    