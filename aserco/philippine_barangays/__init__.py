# -*- coding: utf-8 -*-
from . import models
from . import controllers
from . import wizard
from odoo import api, fields, tools


def add_philippines_state_city_barangay(cr, registry):
    tools.convert_file(cr, 'philippine_barangays', 'data/res.country.state.csv', None, mode='init', noupdate=True,
                       kind='init')
    tools.convert_file(cr, 'philippine_barangays', 'data/res.state.city.csv', None, mode='init', noupdate=True,
                       kind='init')
    tools.convert_file(cr, 'philippine_barangays', 'data/res.city.barangay.csv', None, mode='init', noupdate=True,
                       kind='init')
