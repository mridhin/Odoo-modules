# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.addons.web.controllers.home import Home
from odoo.addons.web.controllers.session import Session


class restrict_user(Home):

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        response = super(restrict_user, self).web_login(redirect, **kw)
        values = request.params.copy()
        if request.params['login_success']:
            uid = request.session.authenticate(
                request.session.db, request.params['login'], request.params['password'])

            user_id = request.env['res.users'].sudo().search(
                [('id', '=', uid)])
            
            print('--------==>>> user_id', user_id)
            print('--------==>>> user_id.force_login', user_id.force_login)
            print('--------==>>> user_id.is_login', user_id.is_login)

            if user_id.force_login:
                user_id.force_logout_button(user_id)
                user_id.is_login = False
            if not user_id.is_login:
                user_id.is_login = True
                user_id.force_login = False
                return response
            else:
                user_id.force_login = True
                request.params['login_success'] = False
                values['error'] = _("You can't Login, Because you are already login from another resourse... \nKindly relogin for force login but you will logout from all other devices.")
                # request.session.logout(keep_db=True)
                _uid = request.env.ref('base.public_user').id
                request.update_env(user=_uid)
                response = request.render('web.login', values)
        return response


class logout_user(Session):

    @http.route('/web/session/logout', type='http', auth="none")
    def logout(self, redirect='/web'):
        uid, login = request.session['uid'], request.session['login']
        user_id = request.env['res.users'].sudo().search(
            [('id', '=', uid), ('active', '=', True), ('login', '=', login)])
        if user_id.is_login:
            user_id.is_login = False
        return super(logout_user, self).logout(redirect)
