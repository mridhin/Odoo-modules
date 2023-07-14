import base64

from datetime import datetime, timedelta
from odoo import _, api, fields, models
from odoo.osv.expression import AND

from odoo.exceptions import UserError

class PosConfig(models.Model):
    _inherit = "pos.config"


    z_reading_sequence_id = fields.Many2one('ir.sequence', string='Z Reading Sequence Id', readonly=True,
        copy=False, ondelete='restrict')
    # z_reading_reset_counter = fields.Integer(related='z_reading_sequence_id.reset_counter')
    z_reading_padding = fields.Integer(related='z_reading_sequence_id.padding', store=True, required=True)
    z_reading_next_number = fields.Integer(related='z_reading_sequence_id.number_next_actual')
    show_delete_z_reading = fields.Boolean(string='Show', compute="_compute_delete_zreading")

    def write(self, vals):
        if 'z_reading_padding' in vals:
            if(vals['z_reading_padding'] < 12):
                raise UserError('Sequence size should be a minimum of 12 digits.') 
            if(vals['z_reading_padding'] > 15):
                raise UserError('Sequence size should be a maximum of 15 digits.')

        return super(PosConfig, self).write(vals)

        
    def generate_sequence(self):
        """
            Call upon button pressed. Button is only available if z_reading_sequence_id is not set.
        """
        IrSequence = self.env['ir.sequence'].sudo()
        val = {
            'name': _('Z-Reading %s', self.name),
            'padding': 15, # adjust as needed. might have min and max of 12-15
            'prefix': "Z-%s/" % self.name,
            'code': "cc_z_reading.z_reading",
            'company_id': self.company_id.id,
        }
        # force sequence_id field to new pos.order sequence
        self.z_reading_sequence_id = IrSequence.create(val).id
        
    def _compute_delete_zreading(self):
        for config in self:
            zreading_report = config.get_z_reading()
            if len(zreading_report) > 0:
                config.show_delete_z_reading = True
            else:
                config.show_delete_z_reading = False
        
    def delete_z_reading(self):
            zreading_report = self.get_z_reading()
            if (zreading_report):
                zreading_report.unlink()
                
    def get_z_reading(self):
        zreading_report = self.env['cc_z_reading.z_reading']
        d = datetime.now().date()
        d1 = datetime.strftime(d, "%Y-%m-%d %H:%M:%S")
        d2 = datetime.strftime(d, "%Y-%m-%d 23:59:59")
        current_session = self.env['pos.session'].search([("stop_at",'>=',d1),("stop_at",'<=',d2),("config_id",'=',self.id)],order='stop_at desc', limit=1)
        if (current_session.id):
            zreading_report = self.env['cc_z_reading.z_reading'].search([('session_id','=',current_session.id),('is_z_reading','=',True)])
        return zreading_report

    @api.model
    def create(self, values):
        if(values['z_reading_padding'] < 12):
            raise UserError('Sequence size should be a minimum of 12 digits.') 
        if(values['z_reading_padding'] > 15):
            raise UserError('Sequence size should be a maximum of 15 digits.')

        IrSequence = self.env['ir.sequence'].sudo()
        val = {
            'name': _('Z-Reading %s', values['name']),
            'padding': values['z_reading_padding'], # adjust as needed. might have min and max of 12-15
            'prefix': "Z-%s/" % values['name'],
            'code': "cc_z_reading.z_reading",
            'company_id': values.get('company_id', False),
        }
        # force sequence_id field to new pos.order sequence
        values['z_reading_sequence_id'] = IrSequence.create(val).id

        return super(PosConfig, self).create(values)
    
    def open_session_cb(self, check_coa=True):
        zreading_report = self.get_z_reading()
        if (len(zreading_report) > 0):
                raise UserError(_("The last user generated Z Reading for today. You cannot re-open session today."))
        return super(PosConfig, self).open_session_cb()  
        