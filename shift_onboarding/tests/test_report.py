from odoo.tests import TransactionCase


class TestProjectReport(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        partner = cls.env['res.partner'].create({'name': 'Report client'})
        cls.project = cls.env['shift.onboarding.project'].create({
            'name': 'Report project',
            'partner_id': partner.id,
        })
        Task = cls.env['shift.onboarding.task']
        Task.create({'name': 'Task A', 'project_id': cls.project.id, 'done': True})
        Task.create({'name': 'Task B', 'project_id': cls.project.id})

    def _html(self):
        html, _ = self.env['ir.actions.report']._render_qweb_html(
            'shift_onboarding.report_project_summary', self.project.ids
        )
        return html.decode() if isinstance(html, bytes) else html

    def test_report_shows_client_tasks_and_progress(self):
        html = self._html()
        self.assertIn('Report client', html)
        self.assertIn('Task A', html)
        self.assertIn('Task B', html)
        self.assertIn('50', html)