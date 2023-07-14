# -*- coding: utf-8 -*-

{
  "name"                 :  "AWB POS RECEIPT",
  "summary"              :  """AWB POS RECEIPT""",
  "category"             :  "Localization",
  "version"              :  "ODOO15",
  "sequence"             :  10,
  "author"               :  "Achieve Without Borders",
  "license"              :  "LGPL-3",
  "website"              :  "https://www.achievewithoutborders.com",
  "description"          :  """ Extension Odoo Apps """, 
  "depends"              :  [
                                
                            ],
  "data"                 :  [
                                # 'views/receipt_pos.xml',
                            ],
  'assets': {
        'point_of_sale.assets': [
             
        ],
        'web.assets_qweb': [
            'awb_pos_receipt/static/src/xml/receipt.xml',
        ],
  "images"               :  [],
  "application"          :  True,
  "installable"          :  True,
  "currency"             :  "USD",
}
  }

