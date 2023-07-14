import base64
from email.policy import default
import logging
import re
from datetime import timedelta, datetime
from functools import partial
from itertools import groupby
from xml.etree.ElementTree import tostring

import psycopg2
import pytz
from odoo import _, api, fields, models
from odoo.osv.expression import AND

from odoo.exceptions import UserError

class ZReading(models.Model):
	_name = 'cc_z_reading.z_reading'
	_description = 'Model for Z-Reading'

	def _default_start_date(self):
		"""
		Find the last end date of the last z-reading
		Set as default start date

		arrange domain by date (desc)
		limit to 5 (should we limit? what if there are multiple records?)

		"""
		arrange_z_reading_ids = self.search([], order='end_date desc')
		if arrange_z_reading_ids:
			return arrange_z_reading_ids[0].end_date

		else:
			return datetime.now()

	"""
		Added the fields below for the separationg of Z-Reading and
			POS Report.
	"""

	reference = fields.Char(string='Reference', compute="_compute_reference", store=True)
	is_z_reading = fields.Boolean(default=False)

	start_date = fields.Datetime(required=True, default=_default_start_date)
	end_date = fields.Datetime(required=True, default=fields.Datetime.now)
	pos_config_ids = fields.Many2many('pos.config', 'z_reading_configs',
										default=lambda s: s.env['pos.config'].search([]))
	total_sales = fields.Float(default=0, compute="_fetch_total_sales", store=True)
	# total_sales_ids = fields.Many2many('pos.session')
	# renamed total_returns to total_voids
	total_voids = fields.Float(default=0, compute="_fetch_total_voids", store=True)
	# total_returns_ids = fields.Many2many('pos.order')
	# total_voids = fields.Float(default=0, compute="_fetch_total_voids", store=True)
	total_discounts = fields.Float(default=0, compute="_fetch_total_discounts", store=True)
	subtotal = fields.Float(default=0, compute="_compute_subtotal", store=True)

	vatable_sales = fields.Float(default=0, compute="_fetch_vatable_sales", store=True)
	vat_12 = fields.Float(default=0, compute="_fetch_vat_12", store=True)
	vat_exempt_sales = fields.Float(default=0, compute="_fetch_vat_exempt_sales", store=True)
	zero_rated_sales = fields.Float(default=0, compute="_fetch_zero_rated_sales", store=True)
	register_total = fields.Float(default=0, compute="_compute_register_total", store=True)

	beginning_reading = fields.Float(default=0, compute="_compute_reading", store=True)
	ending_reading = fields.Float(default=0, compute="_compute_reading", store=True)
	payments_ids = fields.Many2many('pos.payment', 'z_reading_payments')

	crm_team_id = fields.Many2one('crm.team')
	company_id = fields.Many2one(related='crm_team_id.company_id')
	session_ids = fields.Many2many('pos.session', 'z_reading_sessions')

	session_id = fields.Many2one('pos.session')
	config_id = fields.Many2one('pos.config')
	taxpayer_min = fields.Char(related='session_id.taxpayer_min')
	taxpayer_machine_serial_number = fields.Char(related='session_id.taxpayer_machine_serial_number')
	awb_pos_provider_ptu = fields.Char(related='session_id.awb_pos_provider_ptu')

	cashier_ids = fields.Many2many('res.users', compute="_get_cashier_ids")
	# PLEASE UPDATE THE FIELD BELOW, ONCE THE MODULE FOR PWD AND SC DISCOUNTS ARE COMPLETED
	# PLEASE ADD NEW FIELDS FOR FETCHING THE CORRESPONDING DISCOUNTS:
	# # # * SC/PWD 5%
	# # # * SC 20%
	# # # * PWD 20%
	regular_discount = fields.Float(
		default=0, compute="_fetch_promo_coupon_discount", store=True)
	pricelist_amount = fields.Float(
		default=0, compute="_fetch_pricelist_amount", store=True)
	sc_pwd_vat_in = fields.Float(
		default=0, compute="_fetch_sc_pwd_vat_in", store=True)
	sc_vat_ex = fields.Float(
		default=0, compute="_fetch_sc_vat_ex", store=True)
	pwd_vat_ex = fields.Float(
		default=0, compute="_fetch_pwd_vat_ex", store=True)
	# promo_coupon_discount = fields.Float(
	# 	default=0, compute="_fetch_promo_coupon_discount", store=True)

	@api.model
	def create(self, vals):

		if vals['start_date'] and vals['end_date'] and vals['crm_team_id']:
			domain = [
					('start_date','=', vals['start_date']),
					('end_date','=', vals['end_date']),
					('crm_team_id.id','=', vals['crm_team_id'])
				]
			existing_record = self.env['cc_z_reading.z_reading'].search(domain)
						
			if existing_record:
				"""
					If the record with the same start_date, end_date, and
						crm_team_id already exists, return that record.
				"""
				return self.browse(existing_record[0].id)

			else:
				"""
					Else, create a new record.
				"""
				return super(ZReading, self).create(vals)
				
	#@api.depends('session_id', 'session_ids')
	def _get_cashier_ids(self):
		for r in self:
			temp_cashier_ids = []
			for session in r.session_ids:
				# make sure the ids are unique
				user_id = session.user_id.id
				if user_id not in temp_cashier_ids:
					temp_cashier_ids.append(user_id)
			r._compute_reading()
			r.cashier_ids = temp_cashier_ids
				
	@api.depends('is_z_reading')
	def _compute_reference(self):
		for r in self:
			temp_is_z_reading = r.is_z_reading

			if not r.reference:
				if(temp_is_z_reading):
					if(r.crm_team_id.awb_pos_provider_is_training_mode):
						r.reference = 'ZTEST/00000000'
					else:
						z_reading_sequence = r.session_id.config_id.z_reading_sequence_id
						r.reference = z_reading_sequence._next()
						## generates the next z-reading sequence based on the z_reading_sequence_id in pos.config
						# the z-reading sequence is now unique on every terminal/pos session.

				else:
					r.reference = r.env['ir.sequence'].next_by_code('cc_z_reading.pos.report')

	def is_available(self, date_start, date_stop, crm_team_id, order=None):
		if self.env.context.get('pos_close_report', False):
			#TODO: separate z-reading from pos report wherein:
			# z-reading >>> from pos session/ pos config
			# pos report >>> sales team

			"""
				This condition will only be triggered when generating a Z-Reading (pos_close_report).
				Since we are saving the session_ids when generating the report,
					there is no need to search for sessions with the domain commented below.
				This is also to bypass an issue wherein the search is returning blank or incomplete
					because of the condition for `state` wherein the state of the sessions might be different
					with each other.
			"""
			if self.session_ids:
				return self.session_ids
#			print('pos_close_report >>>> TRUE')
			#domain = ["&", ["start_at", ">=", fields.Datetime.to_string(date_start)],
					  #["stop_at", "<=", fields.Datetime.to_string(date_stop)],  # add 1 second
					  #["state", "=", "closed"],
					  #['crm_team_id.name', '=', crm_team_id[0].name],
					  #["crm_team_id.awb_pos_provider_is_training_mode","=",False]
					  #]		
		#	domain = ["&", ["start_at", "=", fields.Datetime.to_string(date_start)],
					  #["state", "=", "opened"],
					  #['crm_team_id.name', '=', crm_team_id[0].name],
					  #["crm_team_id.awb_pos_provider_is_training_mode","=",False]
					  #]
#			sessions = self.env['pos.session'].search(domain, order=order)
			#print('sessions >>> ', sessions)
			#breakpoint()
			#if sessions:
				#self.session_ids = sessions
				#return sessions
		
		elif crm_team_id:
			domain = ["&", ["start_at", ">=", fields.Datetime.to_string(date_start)],
					  ["stop_at", "<=", fields.Datetime.to_string(date_stop)],  # add 1 second
					  ["state", "=", "closed"],
					  ['crm_team_id.name', '=', crm_team_id[0].name],
					  ["crm_team_id.awb_pos_provider_is_training_mode","=",False]
					  ]
			sessions = self.env['pos.session'].search(domain, order=order)
			if sessions:
				self.session_ids = sessions
				return sessions

	def get_payments(self, date_start=False, date_stop=False):
		"""
			get sessions in between start and end dates
			get order ids from sessions
			get payment ids from order ids
			if true > execute sql
			else, set payments to empty

			return payments

		"""
		sessions = self.is_available(date_start, date_stop, self.crm_team_id)
		if sessions:
			orders = sessions.order_ids
			# consider state = voided
			payment_ids = self.env["pos.payment"].search(
				[('pos_order_id', 'in', orders.ids)]).ids
			if payment_ids:
				self.env.cr.execute("""
					SELECT method.name, sum(amount) total
					FROM pos_payment AS payment,
						pos_payment_method AS method
					WHERE payment.payment_method_id = method.id
						AND payment.id IN %s
					GROUP BY method.name
				""", (tuple(payment_ids),))
				payments = self.env.cr.dictfetchall()
				self.payments_ids = payment_ids

				# print("Payments > ", payments)
			else:
				payments = []
				# print("Payments > ", payments)
			return {
				'payments': payments
			}

		else:
			payments = []
			# print("Payments > ", payments)
			return {
				'payments': payments
			}

	@api.depends('start_date', 'end_date', 'crm_team_id')
	def _compute_reading(self):
		for r in self:
			order = "start_at asc"
			sessions = r.is_available(r.start_date, r.end_date, r.crm_team_id, order)

			"""
			Add domain to session per calculations; so that the orders that will be computed
			will be pertaining to sessions that are closed and fits the start and end date
			of the z-reading.

			Add start balance to total payments amount to get the end balance.

			Check if sessions are in order - where the oldest date is first
			"""

			# print('--------==>>> sessions', sessions)
			if sessions:
				"""
					check if the first session in sessions (the oldest session),
					is the first record. if it is true, set beginning reading as 0.

					if false, sum up the total payments of the previous sessions
					as the beginning reading.

					maybe optimize this later.
				"""
				session_id = self.env['pos.session'].search([], limit=1, order='id asc')
				if session_id in sessions:
					beginning_reading = 0.00
					order_ids = self.env['pos.order'].search([('session_id', 'in', sessions.ids)])
					order_ids = order_ids.filtered(lambda x : (x.account_move.move_type == 'out_invoice' or not x.account_move) and (x.amount_total >= 0.0))
					ending_reading = sum(order_ids.mapped('amount_total'))
					ending_reading = round(ending_reading + r.beginning_reading, 2)
				else:
					config_id = sessions.mapped('config_id')
					# print('--------==>>> config_id', config_id, self)
					previous_z_reading_id = self.env['cc_z_reading.z_reading'].search([('id','!=',self.id),('id','<',self.id),('config_id','in',config_id.ids)], limit=1, order='id desc')
					# print('--------==>>> previous_z_reading_id', previous_z_reading_id)	
					amount_total = previous_z_reading_id.ending_reading
					beginning_reading = round(amount_total, 2)
					order_ids = self.env['pos.order'].search([('session_id', 'in', sessions.ids)])
					order_ids = order_ids.filtered(lambda x : (x.account_move.move_type == 'out_invoice' or not x.account_move) and (x.amount_total >= 0.0))
					# print('--------==>>> order_ids', order_ids)
					ending_reading = sum(order_ids.mapped('amount_total'))
					ending_reading = round(ending_reading + beginning_reading, 2)
					# print("Starting Balance > ", beginning_reading)
					# print("Ending Balance > ", ending_reading)
			else:
				beginning_reading = 0
				ending_reading = 0
				# print("There are no sessions.")
			r.update({
				'beginning_reading' : beginning_reading,
				'ending_reading' : ending_reading,
			})

	@api.onchange('start_date')
	def _onchange_start_date(self):
		if self.start_date and self.end_date and self.end_date < self.start_date:
			self.end_date = self.start_date

	@api.onchange('end_date')
	def _onchange_end_date(self):
		if self.end_date and self.end_date < self.start_date:
			self.start_date = self.end_date

	@api.depends('start_date', 'end_date', 'crm_team_id')
	def _fetch_total_voids(self):
		for r in self:

			sessions = r.is_available(r.start_date, r.end_date, r.crm_team_id)
			# consider state = voided
			amount_total = 0
			# total_returns_ids = []
			if sessions:
				for session in sessions:
					for order in session.order_ids:
						if order.amount_total:
							if order.amount_total < 0:
								# total_returns_ids.append(order.id)
								# print("Return Orders > ", order.id)
								amount_total += abs(order.amount_total)

			# self.total_returns_ids = total_returns_ids
			r.total_voids = round(amount_total, 2)

	@api.depends('start_date', 'end_date', 'total_voids', 'total_discounts', 'crm_team_id')
	def _fetch_total_sales(self):
		for r in self:
			"""
				Removed because it is causing issues regarding total_sales
				wherein r.payments_ids is triggered if a previous z-reading
				was generated. Therefore, turning total_sales = to previous
				payment
			"""

			# if r.payments_ids:
			# 	print('r.payements_ids triggered')
			# 	r.total_sales = sum(r.payments_ids.mapped('amount'))
			
			sessions = r.is_available(r.start_date, r.end_date, r.crm_team_id)
			amount_total = 0
			if sessions:
				for session in sessions:
					for order in session.order_ids:
						amount_total += order.amount_total

			amount_total += r.total_voids + r.total_discounts
			r.total_sales = round(amount_total, 2)
		
		# amount_total = is taxed, is discounted, if - (refunded)
		# should be taxed, should not be discounted, should included refundable, should include voided

	@api.depends('start_date', 'end_date', 'crm_team_id')
	def _fetch_total_discounts(self):
		for r in self:
			# consider state = voided
			sessions = r.is_available(r.start_date, r.end_date, r.crm_team_id)
			amount_total = 0
			if sessions:
				for session in sessions:
					for order in session.order_ids:
						for line in order.lines:
							if(line.price_unit < 0 and line.program_id.active == True): #if its a promo
								amount_total += abs(line.price_subtotal_incl)
							else:
								amount_total += (line.qty * line.price_unit) * (line.discount / 100)
			r.total_discounts = round(amount_total, 2)

	@api.depends('total_sales', 'total_voids', 'total_discounts')
	def _compute_subtotal(self):
		for r in self:
			r.subtotal = round(
				(r.total_sales - (r.total_voids + r.total_discounts)), 2)

	@api.depends('start_date', 'end_date', 'crm_team_id')
	def _fetch_vatable_sales(self):
		for r in self:
			sessions = r.is_available(r.start_date, r.end_date, r.crm_team_id)
			amount_total = 0
			# consider state = voided
			if sessions:
				domain_orders = ["&",
								 ["lines.tax_ids.tax_type", "=", "vatable"],
								 ["session_id", "in", sessions.ids]
								 ]
				orders = self.env['pos.order'].search(domain_orders)

				domain_lines = ["&",
								["tax_ids.tax_type", "=", "vatable"],
								["order_id", "in", orders.ids]
								]

				lines = self.env['pos.order.line'].search(domain_lines)

				for line in lines:
					amount_total += line.price_subtotal

			r.vatable_sales = round(amount_total, 2)

	@api.depends('start_date', 'end_date', 'crm_team_id')
	def _fetch_vat_12(self):
		for r in self:
			sessions = r.is_available(r.start_date, r.end_date, r.crm_team_id)
			amount_total = 0
			# consider state = voided
			if sessions:
				domain = ["&",
						  ["lines.tax_ids.tax_type", "=", "vatable"],
						  ["session_id", "in", sessions.ids]
						  ]
				orders = self.env['pos.order'].search(domain)
				for order in orders:
					amount_total += order.amount_tax

			r.vat_12 = round(amount_total, 2)

	@api.depends('start_date', 'end_date', 'crm_team_id')
	def _fetch_vat_exempt_sales(self):
		for r in self:
			sessions = r.is_available(r.start_date, r.end_date, r.crm_team_id)
			amount_total = 0
			# consider state = voided
			if sessions:
				domain_orders = ["&",
								 ["lines.tax_ids.tax_type", "=", "vat_exempt"],
								 ["session_id", "in", sessions.ids]
								 ]
				orders = self.env['pos.order'].search(domain_orders)

				domain_lines = ["&",
								["tax_ids.tax_type", "=", "vat_exempt"],
								["order_id", "in", orders.ids]
								]

				lines = self.env['pos.order.line'].search(domain_lines)

				for line in lines:
					amount_total += line.price_subtotal

			r.vat_exempt_sales = round(amount_total, 2)

	@api.depends('start_date', 'end_date', 'crm_team_id')
	def _fetch_zero_rated_sales(self):
		for r in self:
			sessions = r.is_available(r.start_date, r.end_date, r.crm_team_id)
			amount_total = 0
			# consider state = voided
			if sessions:
				domain_orders = ["&",
								 ["lines.tax_ids.tax_type", "=", "zero_rated"],
								 ["session_id", "in", sessions.ids]
								 ]
				orders = self.env['pos.order'].search(domain_orders)

				domain_lines = ["&",
								["tax_ids.tax_type", "=", "zero_rated"],
								["order_id", "in", orders.ids]
								]

				lines = self.env['pos.order.line'].search(domain_lines)

				for line in lines:
					amount_total += line.price_subtotal

			r.zero_rated_sales = round(amount_total, 2)

	@api.depends('vatable_sales', 'vat_12', 'vat_exempt_sales', 'zero_rated_sales')
	def _compute_register_total(self):
		for r in self:
			r.register_total = round(
				r.vatable_sales + r.vat_12 + r.vat_exempt_sales + r.zero_rated_sales, 2)

	# PLEASE FIX THE METHOD BELOW, ONCE THE MODULE FOR PWD AND SC DISCOUNTS ARE COMPLETED
	# PLEASE ADD NEW FIELDS FOR FETCHING THE CORRESPONDING DISCOUNTS:
	# # # * SC/PWD 5%
	# # # * SC 20%
	# # # * PWD 20%

	# @api.depends('total_discounts')
	# def _fetch_regular_discount(self):
	# 	for r in self:
	# 		r.regular_discount = r.total_discounts

	@api.depends('start_date', 'end_date', 'crm_team_id')
	def _fetch_pricelist_amount(self):
		for r in self:
			sessions = r.is_available(r.start_date, r.end_date, r.crm_team_id)
			amount_total = 0
			# consider state = voided
			if sessions:
				domain_orders = ["&",
								["pricelist_id","!=",False],
								["session_id", "in", sessions.ids]
								]
				orders = self.env['pos.order'].search(domain_orders)

				domain_lines = ["&",
								["pricelist_discount_amount","!=",0],
								["order_id", "in", orders.ids]
								]

				lines = self.env['pos.order.line'].search(domain_lines)
				
				for line in lines:
					amount_total += line.pricelist_discount_amount

			r.pricelist_amount =  round(amount_total, 2)

	@api.depends('start_date', 'end_date', 'crm_team_id')
	def _fetch_sc_pwd_vat_in(self):
		for r in self:
			sessions = r.is_available(r.start_date, r.end_date, r.crm_team_id)
			amount_total = 0
			# consider state = voided
			if sessions:
				domain_orders = [
								# "&",
								["session_id", "in", sessions.ids],
								]
				orders = self.env['pos.order'].search(domain_orders)

				domain_lines = [
								"&", "&",
								["order_id", "in", orders.ids],
								"|",
								["sc_discount","=",5],
								["pwd_discount","=",5],
								"|",
								["sc_discount_amount","!=",0],
								["pwd_discount_amount","!=",0]
								]

				lines = self.env['pos.order.line'].search(domain_lines)
				
				for line in lines:
					amount_total += line.sc_discount_amount + line.pwd_discount_amount

			r.sc_pwd_vat_in =  round(amount_total, 2)

	@api.depends('start_date', 'end_date', 'crm_team_id')
	def _fetch_sc_vat_ex(self):
		for r in self:
			sessions = r.is_available(r.start_date, r.end_date, r.crm_team_id)
			amount_total = 0
			# consider state = voided
			if sessions:
				domain_orders = [
								# "&",
								["session_id", "in", sessions.ids],
								]
				orders = self.env['pos.order'].search(domain_orders)

				domain_lines = [
								"&", "&",
								["order_id", "in", orders.ids],
								["sc_discount","=",20],
								["sc_discount_amount","!=",0]
								]

				lines = self.env['pos.order.line'].search(domain_lines)
				
				for line in lines:
					amount_total += line.sc_discount_amount

			r.sc_vat_ex =  round(amount_total, 2)

	@api.depends('start_date', 'end_date', 'crm_team_id')
	def _fetch_pwd_vat_ex(self):
		for r in self:
			sessions = r.is_available(r.start_date, r.end_date, r.crm_team_id)
			amount_total = 0
			# consider state = voided
			if sessions:
				domain_orders = [
								# "&",
								["session_id", "in", sessions.ids],
								]
				orders = self.env['pos.order'].search(domain_orders)

				domain_lines = [
								"&", "&",
								["order_id", "in", orders.ids],
								["pwd_discount","=",20],
								["pwd_discount_amount","!=",0]
								]

				lines = self.env['pos.order.line'].search(domain_lines)
				
				for line in lines:
					amount_total += line.pwd_discount_amount

			r.pwd_vat_ex =  round(amount_total, 2)

	@api.depends('start_date', 'end_date', 'crm_team_id')
	def _fetch_promo_coupon_discount(self):
		for r in self:
			sessions = r.is_available(r.start_date, r.end_date, r.crm_team_id)
			amount_total = 0
			# consider state = voided
			if sessions:
				domain_orders = [
								["session_id", "in", sessions.ids],
								]
				orders = self.env['pos.order'].search(domain_orders)

				domain_lines = [
								"&",
								["order_id", "in", orders.ids],
								["program_id.active","=",True]
								]

				lines = self.env['pos.order.line'].search(domain_lines)
				
				for line in lines:
					amount_total += abs(line.price_subtotal_incl)

			r.regular_discount =  round(amount_total, 2)

	def generate_report(self):
		data = {
			'cashier_ids': self.cashier_ids,
			'is_z_reading': self.is_z_reading,
			'reference': self.reference,
			'taxpayer_min': self.taxpayer_min,
			'taxpayer_machine_serial_number': self.taxpayer_machine_serial_number,
			'awb_pos_provider_ptu': self.awb_pos_provider_ptu,
			'awb_pos_provider_remarks': self.crm_team_id.awb_pos_provider_remarks,
			'date_start': self.start_date,
			'date_stop': self.end_date,
			'company_name': self.env.company.name,
			'total_sales': self.total_sales,
			# 'total_returns': self.total_returns,
			'total_voids': self.total_voids,
			'total_discounts': self.total_discounts,
			'subtotal': self.subtotal,
			'vatable_sales': self.vatable_sales,
			'vat_12': self.vat_12,
			'vat_exempt_sales': self.vat_exempt_sales,
			'zero_rated_sales': self.zero_rated_sales,
			'register_total': self.register_total,
			'beginning_reading': self.beginning_reading,
			'ending_reading': self.ending_reading,
			'regular_discount': self.regular_discount,
			'pricelist_amount': self.pricelist_amount,
			'sc_pwd_vat_in': self.sc_pwd_vat_in,
			'sc_vat_ex': self.sc_vat_ex,
			'pwd_vat_ex': self.pwd_vat_ex,
			'begin_or_no':self.begin_or_no,
			'end_or_no':self.end_or_no,
			'acc_beginning': self.acc_beginning,
			'acc_end': self.acc_end,
			'acc_beginning_no': self.acc_beginning_no,
			'acc_end_no': self.acc_end_no,
		}
		data.update(self.get_payments(
			data['date_start'], data['date_stop']))
		
		"""
			Saved the report_action as action and added the parameter 
				close_on_report_download set to True. This will close
				the form when printing of the report is done. This is
				to refresh the generation of the report and prevent it
				from pointing to the same recent record.
		"""
		z_reading_ids = self.search([('start_date','<=',self.start_date),('end_date','>=',self.end_date)])
		"""
			Saved the report_action as action and added the parameter 
				close_on_report_download set to True. This will close
				the form when printing of the report is done. This is
				to refresh the generation of the report and prevent it
				from pointing to the same recent record.
		"""
		datas = {
			'ids': z_reading_ids.ids,
			'model': self._name,
			'form': data
		}
		#print('z_reading_ids >>>', z_reading_ids)
		action = self.env.ref('cc_z_reading.action_z_reading_report_3').report_action(z_reading_ids, data=datas)
		#action = self.env.ref('cc_z_reading.action_z_reading_report').report_action(self, data=data)
		action.update({'close_on_report_download': True})
		return action

	"""
		below are for the z-reading views;
	"""
	def action_view_voids(self):
		# sessions = self.is_available(
		# 	self.start_date, self.end_date, self.crm_team_id)
		# changed to self.session_ids since this is being saved
		# so no need to call self.is_available
		sessions = self.session_ids
		# print("sessions from is_available >", sessions)
		if sessions:
			#changed filter to refunded_orderline_id != False
			#this field stores if an orderline is refunded
			domain = ['&', ["lines.refunded_orderline_id","!=",False],
				['session_id', '=', sessions.ids]]
			# print("sessions found.")
		else:
			# print("no sessions found.")
			domain = []
		return {
			'name': _('Voids'),
			'res_model': 'pos.order',
			'view_mode': 'tree',
			'views': [
				(self.env.ref('cc_z_reading.z_reading_view_returns_tree').id, 'tree'),
				],
			'type': 'ir.actions.act_window',
			'target': 'new',
			'domain': domain,
		}

	def action_view_sales(self):
		# sessions = self.is_available(self.start_date,self.end_date,self.crm_team_id)
		sessions = self.session_ids
		if sessions:
			domain = [['session_id', 'in', sessions.ids]]
		else:
			domain = []
		return {
			'name': _('Sales'),
			'res_model': 'pos.order',
			'view_mode': 'tree,form',
			'views': [
				(self.env.ref('cc_z_reading.z_reading_view_sales_tree').id, 'tree'),
				(self.env.ref('point_of_sale.view_pos_pos_form').id, 'form'),
				],
			'type': 'ir.actions.act_window',
			'domain': domain,
		}

	"""
		for now this is commented out;
		once the void module is added, add this in the view;
	"""

	# def action_view_voids(self):
	# 	sessions = self.is_available(self.start_date,self.end_date,self.crm_team_id)
	# 	# print("Session Id type > ", type(sessions.ids))
	# 	if sessions:
	# 		domain = ['&',['session_id', 'in', sessions.ids],
	# 		['state', '=', 'voided']]
	# 	else:
	# 		domain = []
	# 	return {
	# 		'name': _('Voids'),
	# 		'res_model': 'pos.order',
	# 		'view_mode': 'tree',
	# 		'views': [
	# 			(self.env.ref('cc_z_reading.z_reading_view_void_tree').id, 'tree'),
	# 			],
	# 		'type': 'ir.actions.act_window',
	# 		'target': 'new',
	# 		'domain': domain,
	# 	}

	def action_view_discounts(self):
		# sessions = self.is_available(self.start_date,self.end_date,self.crm_team_id)
		sessions = self.session_ids

		if sessions:
			domain = [['session_id', 'in', sessions.ids]]
			orders = self.env['pos.order'].search(domain)
			domain = ["&", ["order_id", 'in', orders.ids], ["discount", "!=", 0]]
		else:
			domain = []
		return {
			'name': _('Discounts'),
			'res_model': 'pos.order.line',
			'view_mode': 'tree',
			'views': [
				(self.env.ref('cc_z_reading.z_reading_view_discounts_tree').id, 'tree'),
			],
			'type': 'ir.actions.act_window',
			'target': 'new',
			'domain': domain,
		}

	def action_view_vat_sales(self):
		sessions = self.is_available(self.start_date, self.end_date, self.crm_team_id)

		if sessions:
			domain = [['session_id', 'in', sessions.ids]]
			orders = self.env['pos.order'].search(domain)
			domain = ["&", ["order_id", 'in', orders.ids], ["tax_ids.tax_type", "=", "vatable"]]
		else:
			domain = []
		return {
			'name': _('Vatable sales'),
			'res_model': 'pos.order.line',
			'view_mode': 'tree',
			'views': [
				(self.env.ref('cc_z_reading.z_reading_view_vat_sales_tree').id, 'tree'),
			],
			'type': 'ir.actions.act_window',
			'target': 'new',
			'domain': domain,
		}

	def action_view_vat_12(self):
		sessions = self.is_available(self.start_date, self.end_date, self.crm_team_id)

		if sessions:
			domain = ["&", ['session_id', 'in', sessions.ids], ["lines.tax_ids.tax_type", "=", "vatable"]]

		else:
			domain = []
		return {
			'name': _('12% VAT'),
			'res_model': 'pos.order',
			'view_mode': 'tree',
			'views': [
				(self.env.ref('cc_z_reading.z_reading_view_vat_12_tree').id, 'tree'),
			],
			'type': 'ir.actions.act_window',
			'target': 'new',
			'domain': domain,
		}

	def action_view_vat_exempt(self):
		sessions = self.is_available(self.start_date, self.end_date, self.crm_team_id)

		if sessions:
			domain = ["&", ['session_id', 'in', sessions.ids], ["lines.tax_ids.tax_type", "=", "vat_exempt"]]

		else:
			domain = []
		return {
			'name': _('VAT Exempt Sales'),
			'res_model': 'pos.order',
			'view_mode': 'tree',
			'views': [
				(self.env.ref('cc_z_reading.z_reading_view_vat_exempt_tree').id, 'tree'),
			],
			'type': 'ir.actions.act_window',
			'target': 'new',
			'domain': domain,
		}

	def action_view_zero_rated(self):
		sessions = self.is_available(self.start_date, self.end_date, self.crm_team_id)

		if sessions:
			domain = ["&", ['session_id', 'in', sessions.ids], ["lines.tax_ids.tax_type", "=", "zero_rated"]]

		else:
			domain = []
		return {
			'name': _('VAT Exempt Sales'),
			'res_model': 'pos.order',
			'view_mode': 'tree',
			'views': [
				(self.env.ref('cc_z_reading.z_reading_view_zero_rated_tree').id, 'tree'),
			],
			'type': 'ir.actions.act_window',
			'target': 'new',
			'domain': domain,
		}
