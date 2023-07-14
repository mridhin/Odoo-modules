# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class GamificationChallenge(models.Model):
    """User having received a badge"""
    _inherit = 'gamification.challenge'
    
    
    # partner_ids = fields.Many2many('res.partner', string='Partners')
    sales_user_ids = fields.Many2many('res.users', 'gamification_challenge_sales_users_rel', 
        string="Salespersons", index=True, 
        tracking=2, default=lambda self: self.env.user, 
        domain=lambda self: "['|', ('groups_id', '=', {}), ('share', '=', True)]".format(
        self.env.ref("sales_team.group_sale_salesman").id
    ))
    
    def _recompute_challenge_users(self):
        """Recompute the domain to add new users and remove the one no longer matching the domain"""
        
        for challenge in self.filtered(lambda c: c.user_domain or c.sales_user_ids):
            if challenge.user_domain:
                current_users = challenge.user_ids
                new_users = self._get_challenger_users(challenge.user_domain)

                if current_users != new_users:
                    challenge.user_ids = new_users
            if challenge.sales_user_ids:
                challenge.user_ids = challenge.sales_user_ids
        return True
    
    # def accept_challenge(self):
    #     user = self.env.user
    #     sudoed = self.sudo()
    #     sudoed.message_post(body=_("%s has joined the challenge", user.name))
    #     sudoed.write({'invited_user_ids': [(3, user.id)], 'user_ids': [(4, user.id)]})
    #     return sudoed._generate_goals_from_challenge()

    # def discard_challenge(self):
    #     """The user discard the suggested challenge"""
    #     user = self.env.user
    #     sudoed = self.sudo()
    #     sudoed.message_post(body=_("%s has refused the challenge", user.name))
    #     return sudoed.write({'invited_user_ids': (3, user.id)})

    # sales_user_ids