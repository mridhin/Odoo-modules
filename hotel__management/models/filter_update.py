def action_confirm(self):
    self.rs_state = "ackw"
    for move_id in self.move_ids_without_package:
        product_id = move_id.sudo().product_id.product_tmpl_id
        print('prod', product_id)
        query = """UPDATE product_template
                               SET warehouse_emp_no = %(number)s,
                                   assigned_to_mob = %(mobile)s,
                                   product_assigned_to = %(assign)s,
                                   internal_ref = %(internal)s,
                                   circle_name = %(circle)s
                                WHERE id = %(name)s """
        self.sudo().env.cr.execute(query, {'name': product_id.id,
                                           'number': self.sudo().rs_destination_id.rs_employee_id,
                                           'mobile': self.sudo().rs_destination_id.login,
                                           'assign': self.sudo().rs_destination_id.id,
                                           'internal': self.sudo().name,
                                           'circle': move_id.circle_name.id
                                           })
    res = super(team_leader, self).action_confirm()
    return res