from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super().action_confirm()
        Project = self.env['shift.onboarding.project']
        for order in self:
            needs_onboarding = any(
                line.product_id.requires_onboarding
                for line in order.order_line
            )
            already_created = Project.search_count(
                [('sale_order_id', '=', order.id)]
            )
            if needs_onboarding and not already_created:
                Project.create({
                    'name': order.name,
                    'partner_id': order.partner_id.id,
                    'sale_order_id': order.id,
                })
        return res