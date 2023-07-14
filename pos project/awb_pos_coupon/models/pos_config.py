from odoo import api, fields, models, _


class PosConfig(models.Model):
    _inherit = "pos.config"

    def use_coupon_code(self, code, creation_date, partner_id, reserved_program_ids, total_value_with_tax, total_value_without_tax):
        coupon_to_check = self.env["coupon.coupon"].search(
            [("code", "=", code), ("program_id", "in", self.program_ids.ids)]
        )
        # If not unique, we only check the first coupon.
        coupon_to_check = coupon_to_check[:1]
        if not coupon_to_check:
            return {
                "successful": False,
                "payload": {
                    "error_message": _("This coupon is invalid (%s).") % (code)
                },
            }
        message = coupon_to_check._check_coupon_code(
            fields.Date.from_string(creation_date[:11]),
            partner_id,
            reserved_program_ids=reserved_program_ids,
        )
        error_message = message.get("error", False)
        maximum_amt = coupon_to_check.program_id.rule_maximum_amount
        if error_message:
            return {
                "successful": False,
                "payload": {"error_message": error_message},
            }
        if maximum_amt > 0:
            if coupon_to_check.program_id.rule_maximum_amount_tax_inclusion == 'tax_included':
                if total_value_with_tax < 0:
                    return {
                        "successful": False,
                        "payload": {
                            "error_message": _("Please Select a Product first")
                        },
                    }
                elif total_value_with_tax > maximum_amt:
                    return{
                        "successful": False,
                        "payload": {
                            "error_message": _("This coupon is invalid for amount greater than (%s).") % (maximum_amt)
                        },
                    }
                else:
                    pass
            elif coupon_to_check.program_id.rule_maximum_amount_tax_inclusion == 'tax_excluded':
                if total_value_without_tax < 0:
                    return {
                        "successful": False,
                        "payload": {
                            "error_message": _("Please Select a Product first")
                        },
                    }
                elif total_value_without_tax > maximum_amt:
                    return{
                        "successful": False,
                        "payload": {
                            "error_message": _("This coupon is invalid for amount greater than (%s).") % (maximum_amt)
                        },
                    }
                else:
                    pass
            else:
                pass
        coupon_to_check.sudo().write({"state": "used"})
        return {
            "successful": True,
            "payload": {
                "program_id": coupon_to_check.program_id.id,
                "coupon_id": coupon_to_check.id,
            },
        }