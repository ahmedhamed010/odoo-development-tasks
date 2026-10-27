from datetime import timedelta

from odoo import fields
from odoo.tests import TransactionCase


class TestOverdueCron(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        today = fields.Date.today()
        partner = cls.env['res.partner'].create({'name': 'Cron client'})
        project = cls.env['shift.onboarding.project'].create({
            'name': 'Cron project',
            'partner_id': partner.id,
        })
        Task = cls.env['shift.onboarding.task']
        base = {'project_id': project.id}
        cls.overdue_a = Task.create({
            **base, 'name': 'Overdue A',
            'deadline': today - timedelta(days=2),
            'assignee_id': cls.env.user.id,
        })
        cls.overdue_b = Task.create({
            **base, 'name': 'Overdue B',
            'deadline': today - timedelta(days=1),
            'assignee_id': cls.env.user.id,
        })
        cls.done_task = Task.create({
            **base, 'name': 'Done late', 'done': True,
            'deadline': today - timedelta(days=3),
            'assignee_id': cls.env.user.id,
        })
        cls.future_task = Task.create({
            **base, 'name': 'Future',
            'deadline': today + timedelta(days=5),
            'assignee_id': cls.env.user.id,
        })
        cls.unassigned = Task.create({
            **base, 'name': 'No assignee',
            'deadline': today - timedelta(days=4),
        })
        cls.all_tasks = (
            cls.overdue_a + cls.overdue_b + cls.done_task
            + cls.future_task + cls.unassigned
        )

    def _activities(self):
        return self.env['mail.activity'].search([
            ('res_model', '=', 'shift.onboarding.task'),
            ('res_id', 'in', self.all_tasks.ids),
        ])

    def test_one_activity_per_overdue_task(self):
        self.env['shift.onboarding.task']._cron_create_overdue_activities()
        activities = self._activities()
        self.assertEqual(len(activities), 2)
        self.assertEqual(
            set(activities.mapped('res_id')),
            {self.overdue_a.id, self.overdue_b.id},
        )

    def test_activity_goes_to_the_assignee(self):
        self.env['shift.onboarding.task']._cron_create_overdue_activities()
        for activity in self._activities():
            self.assertEqual(activity.user_id, self.env.user)

    def test_second_run_creates_no_duplicates(self):
        Task = self.env['shift.onboarding.task']
        Task._cron_create_overdue_activities()
        Task._cron_create_overdue_activities()
        self.assertEqual(len(self._activities()), 2)

    def test_done_future_and_unassigned_tasks_are_ignored(self):
        self.env['shift.onboarding.task']._cron_create_overdue_activities()
        flagged = set(self._activities().mapped('res_id'))
        for task in (self.done_task, self.future_task, self.unassigned):
            self.assertNotIn(task.id, flagged)