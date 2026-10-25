from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestProjectWorkflow(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Task = cls.env['shift.onboarding.task']
        cls.partner = cls.env['res.partner'].create({'name': 'Test client'})
        cls.project = cls.env['shift.onboarding.project'].create({
            'name': 'Test project',
            'partner_id': cls.partner.id,
        })

    def test_deadline_before_start_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.project.write(
                {'date_start': '2026-11-10', 'deadline': '2026-11-01'}
            )

    def test_deadline_equal_to_start_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.project.write(
                {'date_start': '2026-11-10', 'deadline': '2026-11-10'}
            )

    def test_valid_dates_are_accepted(self):
        self.project.write(
            {'date_start': '2026-11-01', 'deadline': '2026-11-10'}
        )
        self.assertEqual(str(self.project.deadline), '2026-11-10')

    def test_start_button(self):
        self.project.action_start()
        self.assertEqual(self.project.state, 'in_progress')

    def test_cancel_button(self):
        self.project.action_cancel()
        self.assertEqual(self.project.state, 'cancelled')

    def test_done_is_blocked_with_open_task(self):
        self.Task.create({'name': 'Open task', 'project_id': self.project.id})
        self.project.action_start()
        with self.assertRaises(ValidationError):
            self.project.action_done()
        self.assertEqual(self.project.state, 'in_progress')

    def test_done_is_allowed_when_all_tasks_are_done(self):
        self.Task.create(
            {'name': 'Task', 'project_id': self.project.id, 'done': True}
        )
        self.project.action_start()
        self.project.action_done()
        self.assertEqual(self.project.state, 'done')