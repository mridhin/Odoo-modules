# -*- coding: utf-8 -*-
import odoo
from odoo import models, fields, api, http
import re
import os


class Users(models.Model):
    _inherit = 'res.users'

    is_login = fields.Boolean(string="Is Login", default=False)
    force_login = fields.Boolean(string="Force Login", default=False)

    @api.model
    def find_login_user(self):
        for sname in os.listdir(odoo.tools.config.session_dir):
            name = re.split('_|\\.', sname)
            session_store = http.root.session_store
            if len(name) > 1:
                get_session = session_store.get(name[1])
            else:
                get_session = session_store.get(name[0])
            if get_session.db and get_session.uid:
                find_user = self.env['res.users'].search([('id', '=', get_session.uid)])
                if find_user:
                    find_user.is_login = True

    def force_logout_button(self, user):
        # user_id = self.env['res.users'].browse(self._context.get('active_id'))
        for fname in os.listdir(odoo.tools.config.session_dir):
            path = os.path.join(odoo.tools.config.session_dir, fname)
            name = re.split('_|\\.', fname)
            session_store = http.root.session_store
            # print('--------==>>> session_store, name', session_store, name)
            if len(name) > 1:
                get_session = session_store.get(name[1])
            else:
                get_session = session_store.get(name[0])  
            # if get_session.db and get_session.uid == user_id.id:
            print('--------==>>> get_session', get_session)
            print('--------==>>> get_session.db', get_session.db)
            print('--------==>>> get_session.uid', get_session.uid)
            print('--------==>>> get_session.id', get_session.id)
            if get_session.db and get_session.uid == user.id:
                os.unlink(path)
                get_session.logout(keep_db=True)
                # user_id.is_login = False
                user.is_login = False


class ForceLogoutWizard(models.TransientModel):
    _name = "force.logout.wizard"
    _description = "Force Logout Wizard"

    def force_logout_button(self):
        user_id = self.env['res.users'].browse(self._context.get('active_id'))
        for fname in os.listdir(odoo.tools.config.session_dir):
            path = os.path.join(odoo.tools.config.session_dir, fname)
            name = re.split('_|\\.', fname)
            session_store = http.root.session_store
            print('--------==>>> session_store, name', session_store, name)
            if len(name) > 1:
                get_session = session_store.get(name[1])
            else:
                get_session = session_store.get(name[0])
            print('--------==>>> get_session', get_session)
            print('--------==>>> get_session.db', get_session.db)
            print('--------==>>> get_session.uid', get_session.uid)
            print('--------==>>> get_session.id', get_session.id)
            if get_session.db and get_session.uid == user_id.id:
                os.unlink(path)
                get_session.logout(keep_db=True)
                user_id.is_login = False

        return {'type': 'ir.actions.act_window_close'}
