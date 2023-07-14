from odoo import _, api, fields, models

class z_reading_report_template(models.AbstractModel):
    _name = 'report.cc_z_reading.z_reading_report_2'


    def _get_report_values(self, docids, data=None):
      att_ids = self.env['cc_z_reading.z_reading'].browse(data.get('ids'))
      docargs = {
                  'doc_ids': self.ids,
                  'data':data,
                  'docs':att_ids,
                  'company': self.env.company
      }

      return docargs