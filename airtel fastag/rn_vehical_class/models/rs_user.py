# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.osv import expression
from odoo.exceptions import ValidationError, Warning, UserError
from datetime import datetime, date
from odoo.addons.auth_signup.models.res_partner import SignupError, now


class Users(models.Model):
    _inherit = "res.users"

    rs_user_role = fields.Many2one('rs.user.role', string="Roles")
    rs_user_id = fields.Many2one('res.users', copy=False, tracking=True,
                                 string='Created By',
                                 default=lambda self: self.env.user)
    rs_employee_id = fields.Char(string="Employee ID")
    rs_email = fields.Char(string="Email Address")
    rs_designation = fields.Selection([('fastag_promoter', 'Fastag Promoter'),
                                       ('fastag_tl', 'Fastag Team Leader'),
                                       ('fastag_mg', 'Fastag-City Manager'),
                                       ('admin', 'Admin'),
                                       ('airter_cntr', 'Airtel Centre'), (
                                       'wh_support_executive',
                                       'Warehouse support/executive'),
                                       ('state_head', 'State Head'),
                                       ('em', 'Enterprise Manager')],
                                      string="Designation")
    # rs_sel_group = fields.Selection([('user', 'User'),('administrator', 'Administrator')], string="Inventory")
    rs_level = fields.Selection(
        [('l1', 'Level 1'), ('l2', 'Level 2'), ('l3', 'Level 3'),
         ('l4', 'Level 4')], string="Level")
    rs_office_addres = fields.Char(string="Office Address")
    rs_circle = fields.Many2one('rs.circle.name', string="Circle Name",options="{'no_create':True,'no_create_edit':True}")
    rs_circle_ids = fields.Many2many('rs.circle.name', string='Circle')
    rs_pin = fields.Char(string="Pincode")
    rs_access = fields.Boolean('Access', store=True)
    rs_employee = fields.Boolean('As a Employee')
    rs_promoter = fields.Boolean('As a Promoter')
    rs_lapu_no = fields.Char(string="Mobile Number")
    rs_toll_name = fields.Char(string="Toll Name")
    rs_project = fields.Char(string="Project")
    rs_work_city = fields.Char(string="Work City")
    rs_agency = fields.Char(string="Agency Name")
    rs_doj = fields.Date(string="DOJ")
    rs_partner_name = fields.Char(compute="_compute_partner")

    @api.constrains('rs_employee_id')
    def unique_name(self):
        product_id = self.search(
            [('rs_employee_id', '=', self.rs_employee_id), ('id', '!=', self.id)])
        if product_id:
            raise ValidationError(_("Employee ID must be unique"))

    # _name = "res.users"
    # _inherit = ['res.users','mail.thread','mail.activity.mixin']
    #
    # rs_user_role = fields.Many2one('rs.user.role',string="Roles")
    # rs_user_id = fields.Many2one('res.users', copy=False, tracking=True,
    #     string='Created By',
    #     default=lambda self: self.env.user)
    # rs_employee_id = fields.Char(string="Employee ID")
    # rs_email = fields.Char(string="Email Address")
    # rs_designation = fields.Selection([('fastag_promoter','Fastag Promoter'),('fastag_tl','Fastag Team Leader'),('fastag_mg','Fastag-City Manager'),('admin','Admin'),('airter_cntr','Airtel Centre'),('wh_support_executive','Warehouse support/executive'),('state_head','State Head'),('em','Enterprise Manager')],string="Designation")
    # # rs_sel_group = fields.Selection([('user', 'User'),('administrator', 'Administrator')], string="Inventory")
    # rs_level = fields.Selection([('l1','Level 1'),('l2','Level 2'),('l3','Level 3'),('l4','Level 4')],string="Level")
    # rs_office_addres = fields.Char(string="Office Address")
    # rs_circle = fields.Many2one('rs.circle.name',string="Circle Name",tracking=True)
    # rs_circle_ids = fields.Many2many('rs.circle.name', string='Circle')
    # rs_pin = fields.Char(string="Pincode")
    # rs_access = fields.Boolean('Access',store=True)
    # rs_employee = fields.Boolean('As a Employee')
    # rs_promoter = fields.Boolean('As a Promoter')
    # rs_lapu_no = fields.Char(string="Mobile Number")
    # rs_toll_name = fields.Char(string="Toll Name")
    # rs_project = fields.Char(string="Project")
    # rs_work_city = fields.Char(string="Work City")
    # rs_agency = fields.Char(string="Agency Name")
    # rs_doj = fields.Date(string="DOJ")

    rs_em = fields.Many2one('res.users',
        string='Enterprise Manager',
        domain="[('rs_designation','=','em')]",
                            options="{'no_create':True,'no_create_edit':True}")
    rs_cm = fields.Many2one('res.users',
        string='Circle Manager',
        domain="[('rs_designation','=','fastag_mg')]",options="{'no_create':True,'no_create_edit':True}")
    rs_tl = fields.Many2one('res.users',
        string='Team Leader',
        domain="[('rs_designation','=','fastag_tl')]",options="{'no_create':True,'no_create_edit':True}")
    #em_circle_custom = fields.Char(string='EM Circle', compute='_get_circle', store=True)

    def _compute_partner(self):
        if self.partner_id:
            self.rs_partner_name = self.partner_id.name
        else:
            self.rs_partner_name = ""

    @api.onchange('rs_circle')
    def _onchange_rs_circle(self):
        now = datetime.strftime(
            fields.Datetime.context_timestamp(self, datetime.now()),
            "%Y-%m-%d %H:%M:%S")
        self.env['log.details'].sudo().create(
            {'name': self.env.user.id,
             'date': now,
             'mobile_no': self.login,
             'change_to': self.rs_circle.name
             })

    @api.onchange('rs_employee_id')
    def _onchange_rs_employee_id(self):
        now = datetime.strftime(
            fields.Datetime.context_timestamp(self, datetime.now()),
            "%Y-%m-%d %H:%M:%S")
        self.env['log.details'].sudo().create(
            {'name': self.env.user.id,
             'date': now,
             'mobile_no': self.login,
             'change_to': self.rs_employee_id
             })

    @api.onchange('rs_lapu_no')
    def _onchange_rs_lapu_no(self):
        now = datetime.strftime(
            fields.Datetime.context_timestamp(self, datetime.now()),
            "%Y-%m-%d %H:%M:%S")
        self.env['log.details'].sudo().create(
            {'name': self.env.user.id,
             'date': now,
             'mobile_no': self.login,
             'change_to': self.rs_lapu_no
             })

    @api.onchange('rs_em')
    def _onchange_rs_em(self):
        now = datetime.strftime(
            fields.Datetime.context_timestamp(self, datetime.now()),
            "%Y-%m-%d %H:%M:%S")
        self.env['log.details'].sudo().create(
            {'name': self.env.user.id,
             'date': now,
             'mobile_no': self.login,
             'change_to': self.rs_em.name
             })

    @api.onchange('rs_cm')
    def _onchange_rs_cm(self):
        now = datetime.strftime(
            fields.Datetime.context_timestamp(self, datetime.now()),
            "%Y-%m-%d %H:%M:%S")
        self.env['log.details'].sudo().create(
            {'name': self.env.user.id,
             'date': now,
             'mobile_no': self.login,
             'change_to': self.rs_cm.name
             })

    @api.onchange('rs_tl')
    def _onchange_rs_tl(self):
        now = datetime.strftime(
            fields.Datetime.context_timestamp(self, datetime.now()),
            "%Y-%m-%d %H:%M:%S")
        self.env['log.details'].sudo().create(
            {'name': self.env.user.id,
             'date': now,
             'mobile_no': self.login,
             'change_to': self.rs_tl.name
             })

    def reset_password(self, login):
        print('pppppppppppppppppp')
        """ retrieve the user corresponding to login (login or email),
            and reset their password
        """
        users = self.search([('login', '=', login)])
        if not users:
            users = self.search([('rs_email', '=', login)])
            print("pppppppppppppppppppppppppppppp")
        if len(users) != 1:
            raise Exception(_('Reset password: invalid username or email'))
        return users.action_reset_password()

    def action_reset_password(self):
        """ create signup token for each user, and send their signup url by email """
        if self.env.context.get('install_mode', False):
            return
        if self.filtered(lambda user: not user.active):
            raise UserError(_("You cannot perform this action on an archived user."))
        # prepare reset password signup
        create_mode = bool(self.env.context.get('create_user'))

        # no time limit for initial invitation, only for reset password
        expiration = False if create_mode else now(days=+1)

        self.mapped('partner_id').signup_prepare(signup_type="reset", expiration=expiration)

        # send email to users with their signup url
        template = False
        if create_mode:
            try:
                template = self.env.ref('auth_signup.set_password_email', raise_if_not_found=False)
            except ValueError:
                pass
        if not template:
            template = self.env.ref('auth_signup.reset_password_email')
        assert template._name == 'mail.template'

        template_values = {
            'email_to': '${object.rs_email|safe}',
            'email_cc': False,
            'auto_delete': True,
            'partner_to': False,
            'scheduled_date': False,
        }
        template.write(template_values)

        for user in self:
            if not user.rs_email:
                raise UserError(_("Cannot send email: user %s has no email address.", user.name))
            # TDE FIXME: make this template technical (qweb)
            with self.env.cr.savepoint():
                force_send = not(self.env.context.get('import_file', False))
                template.send_mail(user.id, force_send=force_send, raise_exception=True)
           # _logger.info("Password reset email sent for user <%s> to <%s>", user.login, user.email)

    # @api.onchange('rs_employee','rs_promoter')
    # def _onchange_groupl(self):
    #     #group = self.env.ref('stock.group_stock_manager')
    #     if self.rs_promoter == True:
    #         print('grouppp')
    #         # group.write({
    #         #     'users': [(3,self.id)]
    #         # })

    # @api.model
    # @api.depends('rs_circle_ids')
    # def _get_circle(self):
    #     for rec in self:
    #         if rec.rs_circle_ids:
    #             circle_custom = ','.join([p.name for p in rec.rs_circle_ids])
    #             rec.em_circle_custom = circle_custom
    #         else:
    #             rec.em_circle_custom = ''

    @api.model
    def create(self, vals):
        res = super(Users, self).create(vals)
        for rec in res:
            rec.sudo().write({
                'rs_partner_name': vals['name']
            })
        return res


class RsUserRole(models.Model):
    _name = 'rs.user.role'
    _description = 'User Role'

    name = fields.Char(string="Role")
    rs_create_date = fields.Date(string="Created Date",default=datetime.today())
    rs_user_id = fields.Many2one('res.users', copy=False, tracking=True,
        string='Created By',
        default=lambda self: self.env.user)

class CircleName(models.Model):
    _name = 'rs.circle.name'
    _description = 'Circle Name'

    name = fields.Char(string="Circle Name")
    