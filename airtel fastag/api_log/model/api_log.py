from odoo import fields,models,api,_
import datetime

class ApiLog(models.Model):
      _name='api.log'
      _description='We Can see here all api log'
      _rec_name='id'

      #id =fields.Char('ID')
      api_name=fields.Char('Api Name', size=100)
      #api=fields.Char('Api ', size=100)
      method=fields.Char('Method',size=20)
      #api_data_key=fields.Char('Api Key',size=100)
      req_body=fields.Text('Request Body')
      params=fields.Text('Params')
      req_header=fields.Text('Request Header')
      response=fields.Text('Response')
      created_date=fields.Date('Created Date',default=fields.Datetime.now())
      # created=fields.Datetime('Created')
      # modified_id=fields.Datetime('Modified')
      # status=fields.Selection([('requested','Requested'),
      #                          ('success','Success'),
      #                          ('failed','Failed')],string='Status')
      result = fields.Char(string="Result")
      error_type=fields.Char('Error Type', size=200)
