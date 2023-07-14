from odoo import fields, models, api


class WebsiteCustomerTestimonials(models.Model):
    _name = 'website.customer.testimonials'
    _description = 'WebsiteCustomerTestimonials'

    name = fields.Char('Title')
    review_text = fields.Text('Review Text')
    reviewer_name = fields.Char('Reviewer Name')
    reviewer_title = fields.Char('Title / Designation')
    rating = fields.Selection(
        string='Rating',
        selection=[('0', '0'),
                   ('1', '1'),
                   ('2', '2'),
                   ('3', '3'),
                   ('4', '4'),
                   ('5', '5')],
        required=False, default="0")

    published = fields.Boolean('Is Published')

