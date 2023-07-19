# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError, ValidationError
from datetime import datetime

import logging

_logger = logging.getLogger(__name__)


class DriversReport(models.Model):
    _name = "drivers.report"
    _description = ""
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "awb_sequence, id"

    active = fields.Boolean(default=True)
    name = fields.Char("Name")

    def _default_stages(self):
        return self.env['report.stages'].search([('awb_sequence', '=', '10')], limit=1).id

    awb_stage_id = fields.Many2one("report.stages", string="Status", default=_default_stages, required=True, group_expand='_display_states', tracking=True)
    stage_code = fields.Char(related="awb_stage_id.code")
    # state = fields.Selection([('draft', 'TO BE DISPATCHED'), ('in-transit', 'IN TRANSIT'), ('arrived', 'ARRIVED TO YARD'), ('pending', 'PENDING'),
    #                           ('approved', 'APPROVED'), ('rejected', 'REJECTED')], default='draft', tracking=True)
    stage_seq = fields.Integer(related="awb_stage_id.awb_sequence", string="Stage seq")
    kanban_state = fields.Selection([('normal', 'In Progress'), ('done', 'Ready'), ('blocked', 'Blocked')])
    name = fields.Char("Drivers Report No.")
    drivers_class = fields.Selection(
        [('megacem', 'Megacem'), ('megaman_powertrade', 'Megaman Powertrade'),
         ('ventures_constructions', 'Megaman Ventures and Construction, Inc.'), ('transport', 'Mega Transport')],
        required=True)
    customer = fields.Many2one("res.partner", string="Customer Name", domain="[('partner_share', '=', True)]", tracking=True)
    load_no = fields.Char("Load No.", tracking=True)
    dor_no = fields.Char("DOR No.", tracking=True)
    type_of_operation = fields.Selection([('cargo', 'Cargo Trucks'), ('contractedCargo', 'Contracted Hauling Cargo'),
                                            ('contractedTrailer', 'Contracted Hauling Trailer'), ('trailer', 'Trailer Truck'),
                                            ('spotTrailer', 'Spot Hauling Trailer'), ('bulk', 'Bulk Carrier'),
                                            ('holcim', 'TC Holcim'), ('dumpTruck', 'Dump Truck')], string="Type Of Operation (Deprecated)")
    type_of_operation_id = fields.Many2one("type.of.operation", string="Type Of Operation", tracking=True)
    type_of_delivery = fields.Selection(
        [('pickup', 'Pick Up (Cement)'), ('hauling_cement', 'Hauling (Cement)'), ('hauling_flour', 'Hauling (Flour)'),
         ('hauling_aggregates', 'Hauling Aggregates'), ('others', 'Others')], string="Type of Delivery (deprecated)")
    type_of_delivery_id = fields.Many2one("type.of.delivery", string="Type Of Delivery", required=1, tracking=True)
    tod_specify = fields.Char("Please Specify")
    pcv_no = fields.Char("PCV No.")
    starting_location = fields.Selection([('m1', 'M1'), ('m2', 'M2'), ('m3', 'M3'), ('m_yard', 'M Yard'), ('others', 'Others')],
                                         required=True)
    please_specify = fields.Char("Please Specify")
    plant_site = fields.Selection(
        [('batangas', 'Batangas'), ('bulacan', 'Bulacan'), ('cavite', 'Cavite'), ('laguna', 'Laguna'),
         ('metro_manila', 'Metro Manila'), ('pampanga', 'Pampanga'),
         ('rizal', 'Rizal'), ('zambales', 'Zambales'), ('bulacan_norzagaray', 'Bulacan Norzagaray'),
         ('rizal_teresa', 'Rizal Teresa'), ('others', 'Others')],
        string="Plant Site:")
    plant_please_specify = fields.Char("Please Specify")

    # Dispatcher Information
    created_by = fields.Many2one("hr.employee", string="Created By", copy=False)
    created_by_2 = fields.Many2one("res.users", string="Created By", default=lambda self: self.env.user, tracking=True, copy=False, ondelete="restrict")
    created_on = fields.Datetime(copy=False)
    fulfilled_by = fields.Many2one("hr.employee", string="Fulfilled By", copy=False)
    fulfilled_by_2 = fields.Many2one("res.users", string="Fulfilled By", copy=False, ondelete="restrict")
    submitted_on = fields.Datetime(copy=False)
    date_delivered = fields.Datetime(copy=False)
    remarks = fields.Char(string="Remarks", tracking=True)
    approved_by_2 = fields.Many2one("res.users", string="Approved By", tracking=True, copy=False, ondelete="restrict")
    approved_by = fields.Many2one("hr.employee",
                                  string="Approved By", copy=False)
    approved_on = fields.Datetime(copy=False)

    responsible = fields.Many2one("res.users", string="Responsible", ondelete="restrict")
    priority = fields.Boolean("High Priority")
    awb_sequence = fields.Integer("Sequence")

    # Yard Details 
    date_and_time_dispatched = fields.Datetime()
    yard_arrival = fields.Datetime()
    dispatched_by = fields.Many2one("hr.employee", string="Dispatched by:", tracking=True, ondelete="restrict")

    # Delivery Site Details
    customer_name = fields.Many2one("res.partner", string="Customer Name:", compute="_compute_customer_name_delivery")
    delivery_site = fields.Many2one("drivers.report.destinations", string="Delivery site:")
    date_and_time_of_arrival = fields.Datetime(string="Date & Time of Arrival")
    date_and_time_of_departure_from_delivery_site = fields.Datetime(
        string="Date & Time of Departure from Delivery Site:")
    start_of_unload = fields.Datetime(string="Start of Unload:")
    end_of_unload = fields.Datetime(string="End of Unload:")

    delivery_site_2 = fields.Many2one("drivers.report.destinations", string="Delivery Site 2:")
    date_and_time_of_arrival_2 = fields.Datetime(string="Date & Time of Arrival 2:")
    date_and_time_of_departure_2 = fields.Datetime(string="Date & Time of Departure 2:")

    delivery_site_3 = fields.Many2one("drivers.report.destinations", string="Delivery Site 3:")
    date_and_time_of_arrival_3 = fields.Datetime(string="Date & Time of Arrival 3:")
    date_and_time_of_departure_3 = fields.Datetime(string="Date & Time of Departure 3:")

    unit_of_measure = fields.Many2one("uom.uom", string="Unit of Measure:")
    quantity_delivered = fields.Float(string="Quantity Delivered:")
    quantity_received = fields.Float(string="Quantity Recieved:")
    discrepancy = fields.Float(string="Discrepancy:", compute='_compute_discrepancy')

    unit_of_measure_2 = fields.Many2one("uom.uom", string="Unit of Measure 2:")
    quantity_delivered_2 = fields.Float(string="Quantity Delivered 2:")

    unit_of_measure_3 = fields.Many2one("uom.uom", string="Unit of Measure 3:")

    # Hubreading Details
    hubreading_starting_location = fields.Float(string="Hubreading Starting Location")
    hubreading_plant_site = fields.Float(string="Hubreading Plant Site:")
    hubreading_delivery_site = fields.Float(string="Hubreading Delivery Site:")
    hubreading_ending_location = fields.Float(string="Hubreading Ending Location:")
    total_kilometers_travelled = fields.Float(string="Total Kilometers Travelled:",
                                              compute='_compute_total_kilometers_travelled', readonly=True)

    # Expenses Details
    travel_allowance = fields.Float(string="Travel Allowance", required=True,  tracking=True)
    travel_vale = fields.Float(string="Travel Vale:", compute="_compute_travel_vale")
    total_travel_allowance = fields.Float(string="Total Travel Allowance:", compute='_compute_total_travel_allowance',
                                          readonly=True)
    expenses_remarks = fields.Char(string="Remarks")

    passway = fields.Boolean(string="Passway:")
    passway_fee_amount = fields.Float(string="Passway Fee Amount:", tracking=True)

    toll_fee = fields.Boolean(string="Toll Fee:")
    toll_fee_amount = fields.Float(string="Toll Fee Amount:", tracking=True)

    diesel = fields.Boolean(string="Diesel:")
    diesel_amount = fields.Float(string="Diesel Amount:", tracking=True)

    extra_helper = fields.Boolean(string="Extra Helper:")
    extra_helper_amount = fields.Float(string="Extra Helper Amount:", tracking=True)

    return_money = fields.Boolean(string="Return Money:")
    return_money_amount = fields.Float(string="Return Money Amount:", tracking=True)

    sop = fields.Boolean(string="S.O.P")
    sop_amount = fields.Float(string="S.O.P Amount:", tracking=True)

    others = fields.Boolean(string="Others")
    expenses_please_specify = fields.Char(string="Please Specify:")
    amount = fields.Float(string="Amount:")

    remaining = fields.Float(string="Remaining:", compute='_compute_remaining', readonly=True)

    total_expenses = fields.Float(string="Total Expenses:", compute='_compute_total_expenses', readonly=True)

    # Fuel Details
    date_and_time_issued = fields.Datetime(string="Date & Time Issued:")
    location = fields.Char(string="Location:")

    pondo_before_trips = fields.Float(string="Pondo (Before Trips):", tracking=True)
    issued = fields.Float(string="Issued:", tracking=True)
    total_pondo = fields.Float(string="Total Pondo:", compute='_compute_total', readonly="True")
    pondo_after_trips = fields.Float(string="Pondo (After Trips):", tracking=True)
    total_fuel_usage = fields.Float(string="Total Fuel Usage:", compute='_compute_total_fuel', readonly="True")
    average_fuel_consumption = fields.Float(string="Average Fuel Consumption:", readonly="True",
                                            compute='_compute_average_fuel_consumption')

    # Plant Details
    date_and_time_of_plant_arrival = fields.Datetime(string="Date & of Plant Arrival:")
    date_and_time_of_plant_departure = fields.Datetime(string="Date & of Plant Departure:")
    plant_remarks = fields.Char(string="Remarks")

    # Truck Details
    th_number = fields.Many2one("th.number", string="Th Number:")

    driver_1_name = fields.Many2one("hr.employee", string="Driver 1 Name:")
    employee_id_dr1 = fields.Char(string="Employee ID (DR1):", related='driver_1_name.barcode', ondelete="restrict")

    driver_2_name = fields.Many2one("hr.employee", string="Driver 2 Name:", ondelete="restrict")
    employee_id_dr2 = fields.Char(string="Employee ID (DR2):", related='driver_2_name.barcode', ondelete="restrict")

    helper_1_name = fields.Many2one("hr.employee", string="Helper 1 Name:", ondelete="restrict")
    employee_id_h1 = fields.Char(string="Employee ID (H1):", related='helper_1_name.barcode', ondelete="restrict")

    helper_2_name = fields.Many2one("hr.employee", string="Helper 2 Name:", ondelete="restrict")
    employee_id_h2 = fields.Char(string="Employee ID (H2):", related='helper_2_name.barcode', ondelete="restrict")

    helper_3_name = fields.Many2one("hr.employee", string="Helper 3 Name:", ondelete="restrict")
    employee_id_h3 = fields.Char(string="Employee ID (H3):", related='helper_3_name.barcode', ondelete="restrict")

    no_field = fields.Char("No.")
    bulk_no_id = fields.Many2one("bulk.number", string="No.")

    vale_d1 = fields.Float(string="Vale (D1):", required="True")
    rate_d1 = fields.Float(string="Rate (D1):", required="True")

    vale_d2 = fields.Float(string="Vale (D2):")
    rate_d2 = fields.Float(string="Rate (D2):")

    vale_h1 = fields.Float(string="Vale (H1):", required="True")
    rate_h1 = fields.Float(string="Rate (H1):", required="True")

    vale_h2 = fields.Float(string="Vale (H2):")
    rate_h2 = fields.Float(string="Rate (H2):")

    vale_h3 = fields.Float(string="Vale (H3):")
    rate_h3 = fields.Float(string="Rate (H3):")

    is_logistics_supervisor = fields.Boolean(default=False, compute='is_logistics_supervisor_function')
    is_accounting_department = fields.Boolean(default=False, compute='is_accounting_department_function')
    
    billing_status = fields.Selection([('billed', 'Billed'),('unbilled', 'Unbilled'),
                                    ], string='Billing Status', default="unbilled")
    shipment_no = fields.Integer(string="Shipment No")
    hauling_rate = fields.Float(string="Hauling Rate")
    soa_journal_report = fields.Many2one('account.move', string="SOA Journal Entry")

    def action_rejected(self):
        stage = self.env['report.stages'].search([('code', '=', 'rejected')])
        self.awb_stage_id = stage

    def action_approved(self):
        for rec in self:
            stage = self.env['report.stages'].search([('code', '=', 'approved')])
            self.awb_stage_id = stage
            rec.approved_by_2 = self.env.user
            rec.approved_on = datetime.today()

    def action_arrived(self):
        stage = self.env['report.stages'].search([('code', '=', 'arrived')])
        self.awb_stage_id = stage



    def action_for_review(self):
        stage = self.env['report.stages'].search([('code', '=', 'pending')])
        for rec in self:
            rec.awb_stage_id = stage
            rec.fulfilled_by_2 = self.env.user
            rec.submitted_on = datetime.today()

    def action_return_to_pending(self):
        stage = self.env['report.stages'].search([('code', '=', 'pending')])
        for rec in self:
            rec.awb_stage_id = stage
            rec.approved_by_2 = False
            rec.approved_on = False

    @api.depends('is_logistics_supervisor')
    def is_logistics_supervisor_function(self):
        for rec in self:
            ret_has_group = self.env.user.has_group('awb_megacem_drivers_report.group_logistic_supervisor')

            _logger.debug(f'############ RETURN : {ret_has_group}')

            if ret_has_group:
                rec.is_logistics_supervisor = True
            else:
                rec.is_logistics_supervisor = False

    @api.depends('is_accounting_department')
    def is_accounting_department_function(self):
        for rec in self:
            ret_has_group = self.env.user.has_group('awb_megacem_drivers_report.group_accounting_department')

            _logger.debug(f'############ RETURN : {ret_has_group}')

            if ret_has_group:
                rec.is_accounting_department = True
            else:
                rec.is_accounting_department = False

    @api.depends('vale_d1','vale_d2','vale_h1','vale_h2','vale_h3')
    def _compute_travel_vale(self):
        for rec in self:
            rec.travel_vale = rec.vale_d1 + rec.vale_d2 + rec.vale_h1 + rec.vale_h2 + rec.vale_h3

    # @api.onchange('driver_1_name')
    # def set_employee_id_dr1(self):
    #     for rec in self:
    #         if rec.driver_1_name:
    #             rec.employee_id_dr1 = rec.driver_1_name.barcode
    #
    # @api.onchange('helper_1_name')
    # def set_employee_id_h1(self):
    #     for rec in self:
    #         if rec.helper_1_name:
    #             rec.employee_id_h1 = rec.helper_1_name.barcode
    #
    # @api.onchange('helper_2_name')
    # def set_employee_id_h2(self):
    #     for rec in self:
    #         if rec.helper_2_name:
    #             rec.employee_id_h2 = rec.helper_2_name.barcode
    #
    # @api.onchange('helper_3_name')
    # def set_employee_id_h3(self):
    #     for rec in self:
    #         if rec.helper_3_name:
    #             rec.employee_id_h3 = rec.helper_3_name.barcode

    @api.depends('pondo_before_trips', 'issued', 'total_pondo')
    def _compute_total(self):
        for rec in self:
            rec.total_pondo = rec.pondo_before_trips + rec.issued

    @api.depends('total_pondo', 'pondo_after_trips', 'total_fuel_usage')
    def _compute_total_fuel(self):
        for rec in self:
            rec.total_fuel_usage = rec.total_pondo - rec.pondo_after_trips

    @api.depends('quantity_received', 'quantity_delivered', 'discrepancy')
    def _compute_discrepancy(self):
        for rec in self:
            rec.discrepancy = rec.quantity_received - rec.quantity_delivered

    @api.depends('hubreading_ending_location', 'hubreading_starting_location', 'total_kilometers_travelled')
    def _compute_total_kilometers_travelled(self):
        for rec in self:
            rec.total_kilometers_travelled = rec.hubreading_ending_location - rec.hubreading_starting_location

    @api.depends('travel_allowance', 'travel_vale', 'total_travel_allowance')
    def _compute_total_travel_allowance(self):
        for rec in self:
            rec.total_travel_allowance = rec.travel_allowance - rec.travel_vale

    @api.depends('total_travel_allowance', 'total_expenses', 'remaining')
    def _compute_remaining(self):
        for rec in self:
            rec.remaining = rec.total_travel_allowance - rec.total_expenses
            
    ''' Billed and Unbilled button action'''       
    def action_billed_report(self):
        for rec in self:
            rec.billing_status = 'billed'
        
    def action_unbilled_report(self):
        for rec in self:
            rec.billing_status = 'unbilled'
            
    ''' Server Action To create Journal Entries'''
    def action_create_dr_expense_entry(self):
        driver_journal =  self.env['ir.model.data'].get_object_reference('awb_megacem_drivers_report','megacem_driver_report_journal')[1]
        journal_id = {'state': 'draft', 'move_type': 'entry', 'ref': self.name, 'is_driver_report': True, 'driver_report_id': self.id, 'journal_id': driver_journal}
        line_ids = []
        # Debit Amount
        if self.passway:
            line_ids += [(0, 0, {'account_id': self.x_studio_passway_account.id, 'debit': self.passway_fee_amount
                })
                ]
        if self.diesel:
            line_ids += [(0, 0, {'account_id': self.x_studio_diesel_account.id, 'debit': self.diesel_amount
                    })]
        if self.toll_fee:
            line_ids += [(0, 0, {'account_id': self.x_studio_toll_fee_account.id, 'debit': self.toll_fee_amount
                    })]

        if self.extra_helper:
            line_ids += [(0, 0, {'account_id': self.x_studio_extra_helper_account.id, 'debit': self.extra_helper_amount
                    })]
        if self.return_money:
            line_ids += [(0, 0, {'account_id': self.x_studio_return_money_account.id, 'debit': self.return_money_amount
                    })]
        if self.sop:
            line_ids += [(0, 0, {'account_id': self.x_studio_sop_account.id, 'debit': self.sop_amount
                    })]
        if self.others:
            line_ids += [(0, 0, {'account_id': self.x_studio_others_account.id, 'debit': self.amount
                    })]
        # Credit Amount
        line_ids +=[(0, 0, {'account_id': self.x_studio_petty_cash_account.id, 'credit': self.total_expenses,
                    })]
        # End
        journal_id.update({'line_ids': line_ids})
        move_id = self.env['account.move'].create(journal_id)
        self.x_studio_journal_entry_id = move_id.id

    @api.depends('passway', 'diesel', 'toll_fee', 'extra_helper', 'return_money', 'sop', 'others', 'passway_fee_amount', 'toll_fee_amount', 'diesel_amount', 'extra_helper_amount', 'return_money_amount',
                 'sop_amount', 'amount', 'total_expenses')
    def _compute_total_expenses(self):
        for rec in self:
            passway_fee_amount = rec.passway_fee_amount if rec.passway else False
            diesel_amount = rec.diesel_amount if rec.diesel else False
            toll_fee_amount = rec.toll_fee_amount if rec.toll_fee else False
            extra_helper_amount = rec.extra_helper_amount if rec.extra_helper else False
            return_money_amount = rec.return_money_amount if rec.return_money else False
            sop_amount = rec.sop_amount if rec.sop else False
            amount = rec.amount if rec.others else False
            rec.total_expenses = passway_fee_amount + toll_fee_amount + diesel_amount + extra_helper_amount + return_money_amount + sop_amount + amount

    @api.depends('total_kilometers_travelled','total_fuel_usage')
    def _compute_average_fuel_consumption(self):
        for rec in self:
            rec.average_fuel_consumption = 0
            if rec.total_fuel_usage > 0:
                rec.average_fuel_consumption = rec.total_kilometers_travelled/rec.total_fuel_usage

    # copmuted field that fills the customer name in the Delivery Site tab
    @api.depends('customer')
    def _compute_customer_name_delivery(self):
        for rec in self:
            rec.customer_name = rec.customer

    # override create() function
    @api.model
    def create(self, vals):
        # this ff code automatically sequence the drivers_report_no base on the given conditions
        # the condition checks the value of <drivers_class> before assigning the right type of sequence
        if vals.get('drivers_class') == 'megacem' or vals.get('drivers_class') == 'megaman_powertrade':
            sequence = self.env['ir.sequence'].next_by_code('mpi.drivers.report.sequence')
            vals['name'] = sequence

        elif vals.get('drivers_class') == 'ventures_constructions' or vals.get('drivers_class') == 'transport':
            sequence = self.env['ir.sequence'].next_by_code('mti.drivers.report.sequence')
            vals['name'] = sequence

        stage = self.env['report.stages'].search([('name', '=', 'In Transit')]).id

        if stage:
            vals['awb_stage_id'] = stage

        vals['created_on'] = datetime.today()

        return super(DriversReport, self).create(vals)

    def write(self, vals):

        # validation
        _logger.debug(f'test {self.quantity_received}')
        _logger.debug(f'test {self.quantity_delivered}')
        if self.quantity_received <= 0:
            _logger.debug(f'')
            if vals.get('quantity_received') and vals.get('quantity_received') <= 0:
                raise UserError(_("'Quantity Received' value should be greater than zero"))

        if self.quantity_delivered <= 0:
            if vals.get('quantity_delivered') and vals.get('quantity_delivered') <= 0:
                raise UserError(_("'Quantity Delivered' value should be greater than zero"))

        # if float(vals.get('hubreading_plant_site')) <= float(vals.get('hubreading_starting_location')):
        #     raise UserError(
        #         _("'Hubreading Plant Site' value should not be less than or equal to 'Hubreading Starting Location'"))
        #
        # if float(vals.get('hubreading_delivery_site')) <= float(vals.get('hubreading_plant_site')):
        #     raise UserError(
        #         _("'Hubreading Delivery Site' value should not be less than or equal to 'Hubreading Plant Site'"))
        #
        # if float(vals.get('hubreading_ending_location')) <= float(vals.get('hubreading_delivery_site')):
        #     raise UserError(
        #         _("'Hubreading Ending Location' value should not be less than or equal to 'Hubreading Delivery Site'"))
        #
        # if float(vals.get('travel_allowance')) <= 0:
        #     raise UserError(_('Travel Allowance should be greater than zero'))
        #
        # if float(vals.get('pondo_before_trips')) <= 0:
        #     raise UserError(_("Pondo (Before Trips)' should be greater than zero"))
        #
        # if float(vals.get('pondo_after_trips')) <= 0:
        #     raise UserError(_("Pondo (After Trips)' should be greater than zero"))
        #
        # if float(vals.get('vale_d1')) <= 0:
        #     raise UserError(_("'Vale (D1)' value should be greater than zero"))
        # if float(vals.get('rate_d1')) <= 0:
        #     raise UserError(_("'Rate (D1)' value should be greater than zero"))
        # if float(vals.get('vale_h1')) <= 0:
        #     raise UserError(_("'Vale (H1)' value should be greater than zero"))
        # if float(vals.get('rate_h1')) <= 0:
        #     raise UserError(_("'Rate (H1)' value should be greater than zero"))



        if 'is_master' in vals and vals['is_master']:
            master = self.with_context(active_test=False).group_id.record_ids.filtered('is_master')
            master.write({'is_master': False})

        return super(DriversReport, self).write(vals)


    # will be used to show empty columns in kanban
    # returns the records from report.stages
    def _display_states(self, states, domain, order):
        stage_ids = self.env['report.stages'].search([])
        return stage_ids

    #This function sets the approved by field to the current user and approved on field to the current date
    @api.onchange('awb_stage_id')
    def _set_approved_fields(self):
        _logger.debug(f'################# HITTTTT')
        user_id = self.env.user
        _logger.debug(f'################# HITTTTT: {user_id}')
        _logger.debug(f'################# HITTTTT: {user_id.id}')
        for rec in self:
            if rec.stage_seq == 14:
                if rec.is_logistics_supervisor:
                    rec.approved_by_2 = self.env.user.id
                    rec.approved_on = datetime.today()
                else:
                    rec.awb_stage_id = self.env['report.stages'].search([('awb_sequence', '=', '13')], limit=1).id
