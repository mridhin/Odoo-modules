# -*- coding: utf-8 -*-
from odoo.addons.portal.controllers import portal


class CustomerPortal(portal.CustomerPortal):
    
    # Added domain to display the Proxy Booker SO in Customer Portal
    def _prepare_quotations_domain(self, partner):
        if (partner.x_studio_partner_store):
            return ['|','&',
                ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
                ('state', 'in', ['draft', 'sent', 'cancel']),
                '&',
                ('x_studio_partner_store_id', '=', partner.id),
                ('state', 'in', ['draft', 'sent', 'cancel'])
            ]
        else:
            return [
                ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
                ('state', 'in', ['draft', 'sent', 'cancel'])
            ]

    def _prepare_orders_domain(self, partner):
        if (partner.x_studio_partner_store):
            return ['|','&',
                ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
                ('state', 'in', ['sale', 'done']),
                '&',
                ('x_studio_partner_store_id', '=', partner.id),
                ('state', 'in', ['sale', 'done'])
            ]
        else:
            return [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['sale', 'done'])
        ]