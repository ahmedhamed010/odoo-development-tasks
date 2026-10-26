from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    requires_onboarding = fields.Boolean(string='Requires Onboarding')