from odoo import models, fields, api


class HotelReport(models.TransientModel):
    _name = 'hotel.report.wizard'

    check_in = fields.Date(string='From')
    check_out = fields.Date(string='To')
    partner_id = fields.Many2one('res.partner', string='Guest Name')
    room_ids = fields.Many2many('hotel.room', string='Room')
    check = fields.Datetime(string='Check', default=fields.Datetime.now())

    def accommodation_report(self):
        query = """SELECT * FROM hotel_booking """
       # domain = []
        guest = self.partner_id.id
        if guest:
            query = """SELECT * FROM hotel_booking
                                   WHERE  partner_id = %(guest)s """
            #domain += [('partner_id', '=', guest)]
        date_from = self.check_in
        if date_from:
            query = """SELECT * FROM hotel_booking WHERE 
                                    check_in >= %(date_from)s"""
            if guest:
                query = """SELECT * FROM hotel_booking
                                              WHERE partner_id = %(guest)s AND 
                                              check_in >= %(date_from)s"""


           # domain += [('check_in', '>=', date_from)]
        date_to = self.check_out
        if date_to:
            query = """SELECT * FROM hotel_booking WHERE 
                                                check_out <= %(date_to)s"""
            if date_from:
                query = """SELECT * FROM hotel_booking WHERE check_in >= %(date_from)s
                                                                AND check_out <= %(date_to)s"""
                if guest:
                    query = """SELECT * FROM hotel_booking
                                                WHERE partner_id = %(guest)s  
                                                AND check_in >= %(date_from)s
                                                AND check_out <= %(date_to)s"""
                if date_from == None:
                    query = """SELECT * FROM hotel_booking WHERE partner_id = %(guest)s  
                                                            AND check_out <= %(date_to)s"""


            ##domain += [('check_in', '<=', date_to)]
        room_list = []
        list = []
        room = self.room_ids
        for rec in room:
            room_list.append(rec.id)
            list.append(rec.name)
        if room_list:
            query = """SELECT * FROM hotel_booking WHERE 
                                                           room_id IN %(room)s"""
            if guest:
                query = """SELECT * FROM hotel_booking WHERE 
                                                        room_id IN %(room)s
                                                        AND partner_id = %(guest)s"""
                if date_from:
                    query = """SELECT * FROM hotel_booking WHERE room_id IN %(room)s
                                                        AND partner_id = %(guest)s
                                                        AND check_in >= %(date_from)s"""
                    if date_to:
                        query = """SELECT * FROM hotel_booking WHERE 
                                                        room_id IN %(room)s
                                                        AND partner_id = %(guest)s
                                                        AND check_in >= %(date_from)s
                                                        AND AND check_out <= %(date_to)s"""
                    elif date_from == None:
                        query = """SELECT * FROM hotel_booking WHERE room_id IN %(room)s
                                                                                AND partner_id = %(guest)s
                                                                                AND AND check_out <= %(date_to)s"""

            #domain += [('room_id', '=', room_list)]


        booking_list = []
        #booking = self.env['hotel.booking'].search(domain)

        #self.env.cr.execute(query,{'guest': self.partner_id.id,
         #                           'date_from':self.check_in,
         #                           })
        #booking = self.env.cr.fetchall()
        self.env.cr.execute(query, {'guest': self.partner_id.id,
                                    'date_from': self.check_in,
                                    'date_to': self.check_out,
                                    'room': tuple(room_list)})
        booking = self.env.cr.fetchall()
        data = {
            'wizard': self.read()[0],
            'booking': booking,
            'room_list': list
        }
        return self.env.ref('hotel__management.hotel_report_generate').report_action(self, data=data)

    def accommodation_report_xlsx(self):
        query = """SELECT * FROM hotel_booking """
        # domain = []
        guest = self.partner_id.id
        if guest:
            query = """SELECT * FROM hotel_booking
                                           WHERE  partner_id = %(guest)s """
            # domain += [('partner_id', '=', guest)]
        date_from = self.check_in
        if date_from:
            query = """SELECT * FROM hotel_booking WHERE 
                                            check_in >= %(date_from)s"""
            if guest:
                query = """SELECT * FROM hotel_booking
                                                      WHERE partner_id = %(guest)s AND 
                                                      check_in >= %(date_from)s"""

        # domain += [('check_in', '>=', date_from)]
        date_to = self.check_out
        if date_to:
            query = """SELECT * FROM hotel_booking WHERE 
                                                        check_out <= %(date_to)s"""
            if date_from:
                query = """SELECT * FROM hotel_booking WHERE check_in >= %(date_from)s
                                                                        AND check_out <= %(date_to)s"""
                if guest:
                    query = """SELECT * FROM hotel_booking
                                                        WHERE partner_id = %(guest)s  
                                                        AND check_in >= %(date_from)s
                                                        AND check_out <= %(date_to)s"""
                if date_from == None:
                    query = """SELECT * FROM hotel_booking WHERE partner_id = %(guest)s  
                                                                    AND check_out <= %(date_to)s"""

            ##domain += [('check_in', '<=', date_to)]
        room_list = []
        list = []
        room = self.room_ids
        for rec in room:
            room_list.append(rec.id)
            list.append(rec.name)
        if room_list:
            query = """SELECT * FROM hotel_booking WHERE 
                                                                   room_id IN %(room)s"""
            if guest:
                query = """SELECT * FROM hotel_booking WHERE 
                                                                room_id IN %(room)s
                                                                AND partner_id = %(guest)s"""
                if date_from:
                    query = """SELECT * FROM hotel_booking WHERE room_id IN %(room)s
                                                                AND partner_id = %(guest)s
                                                                AND check_in >= %(date_from)s"""
                    if date_to:
                        query = """SELECT * FROM hotel_booking WHERE 
                                                                room_id IN %(room)s
                                                                AND partner_id = %(guest)s
                                                                AND check_in >= %(date_from)s
                                                                AND AND check_out <= %(date_to)s"""
                    elif date_from == None:
                        query = """SELECT * FROM hotel_booking WHERE room_id IN %(room)s
                                                                                        AND partner_id = %(guest)s
                                                                                        AND AND check_out <= %(date_to)s"""

            # domain += [('room_id', '=', room_list)]

        booking_list = []
        # booking = self.env['hotel.booking'].search(domain)

        # self.env.cr.execute(query,{'guest': self.partner_id.id,
        #                           'date_from':self.check_in,
        #                           })
        # booking = self.env.cr.fetchall()
        self.env.cr.execute(query, {'guest': self.partner_id.id,
                                    'date_from': self.check_in,
                                    'date_to': self.check_out,
                                    'room': tuple(room_list)})
        booking = self.env.cr.fetchall()
        data = {
            'guest': self.partner_id.name,
            'booking': booking,
            'room': list
        }
        return self.env.ref('hotel__management.hotel_xlsx_report_generate').report_action(self, data=data)

class HotelExcelReport(models.AbstractModel):
    _name = 'report.hotel__management.accommodation_xlsx_report_generate'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, booking):
        sheet = workbook.add_worksheet('Accommodations')
        bold = workbook.add_format({'bold': True})
        title = workbook.add_format({'bold': True, 'align': 'center'})
        sheet.merge_range('A1:G1', 'Accommodation Report', title)
        sheet.set_column('A:A', 15)
        sheet.set_column('B:B', 15)
        sheet.set_column('C:C', 20)
        sheet.set_column('E:E', 10)
        sheet.set_column('F:F', 10)
        sheet.set_column('G:G', 10)
        row = 3
        col = 0
        sheet.write(1, 0, 'Guest Name', bold)
        sheet.write(2, 0, 'Rooms', bold)
        sheet.write(row, col, 'Si No', bold)
        sheet.write(row, col + 1, 'Booking Ref', bold)
        sheet.write(row, col + 2, 'Guest Name', bold)
        sheet.write(row, col + 3, 'Room', bold)
        sheet.write(row, col + 4, 'Check In', bold)
        sheet.write(row, col + 5, 'Check Out', bold)
        sheet.write(row, col + 6, 'Order Ref', bold)
        c = 0
        for booking in data['booking']:
            c += 1
            row += 1
            sheet.write(row, col, c)
            sheet.write(row, col+1, booking[7])
            sheet.write(row, col+2, booking[15])
            sheet.write(row, col + 3, booking[16])
            sheet.write(row, col + 4, booking[2])
            sheet.write(row, col + 5, booking[3])
            sheet.write(row, col + 6, booking[14])
        print(data['room'])
        sheet.write(1, 1, data['guest'])
        col = 1
        for rec in data['room']:
            sheet.write(2, col, rec)
            col += 1








