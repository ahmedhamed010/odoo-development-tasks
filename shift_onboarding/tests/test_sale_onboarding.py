from odoo.tests import TransactionCase


class TestSaleOnboarding(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Project = cls.env['shift.onboarding.project']
        cls.partner = cls.env['res.partner'].create({'name': 'Test client'})
        cls.onboarding_product = cls.env['product.template'].create({
            'name': 'Onboarding service',
            'requires_onboarding': True,
        }).product_variant_id
        cls.plain_product = cls.env['product.template'].create({
            'name': 'Plain product',
        }).product_variant_id

    def _order(self, product):
        return self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': product.id,
                'product_uom_qty': 1,
            })],
        })

    def test_confirm_with_required_product_creates_project(self):
        order = self._order(self.onboarding_product)
        order.action_confirm()
        project = self.Project.search([('sale_order_id', '=', order.id)])
        self.assertEqual(len(project), 1)
        self.assertEqual(project.partner_id, self.partner)

    def test_confirm_without_required_product_creates_nothing(self):
        order = self._order(self.plain_product)
        order.action_confirm()
        self.assertFalse(
            self.Project.search([('sale_order_id', '=', order.id)])
        )

    def test_reconfirming_after_cancel_does_not_duplicate(self):
        order = self._order(self.onboarding_product)
        order.action_confirm()
        order._action_cancel()
        order.action_draft()
        order.action_confirm()
        self.assertEqual(
            self.Project.search_count([('sale_order_id', '=', order.id)]), 1
        )

    def test_partner_project_count(self):
        self._order(self.onboarding_product).action_confirm()
        self._order(self.onboarding_product).action_confirm()
        self.partner.invalidate_recordset()
        self.assertEqual(self.partner.onboarding_project_count, 2)