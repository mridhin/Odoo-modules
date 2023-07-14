# -*- coding: utf-8 -*-

{
  "name"                 :  "AWB Purchase Custom",
  "summary"              :  """AWB Purchase Custom""",
  "category"             :  "Purchase",
  "version"              :  "ODOO15",
  "sequence"             :  10,
  "author"               :  "Achieve Without Borders",
  "license"              :  "LGPL-3",
  "website"              :  "https://www.achievewithoutborders.com",
  "description"          :  """ Extension Odoo Apps """, 
  "depends"              :  [
                                "purchase",
                            ],
  "data"                 :  [
                                'views/cron.xml',
                                'views/purchase_views.xml',
                            ],
  "images"               :  [],
  "application"          :  True,
  "installable"          :  True,
  "currency"             :  "USD",
  }

