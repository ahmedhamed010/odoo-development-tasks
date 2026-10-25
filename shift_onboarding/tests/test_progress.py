from odoo.tests import TransactionCase


class TestProjectProgress(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Task = cls.env['shift.onboarding.task']
        cls.partner = cls.env['res.partner'].create({'name': 'Test client'})
        cls.project = cls.env['shift.onboarding.project'].create({
            'name': 'Test project',
            'partner_id': cls.partner.id,
        })

    def _task(self, name):
        return self.Task.create({'name': name, 'project_id': self.project.id})

    def test_progress_is_zero_without_tasks(self):
        self.assertEqual(self.project.progress, 0.0)

    def test_progress_follows_ticked_tasks(self):
        task_a = self._task('A')
        task_b = self._task('B')
        self.assertEqual(self.project.progress, 0.0)
        task_a.done = True
        self.assertEqual(self.project.progress, 50.0)
        task_b.done = True
        self.assertEqual(self.project.progress, 100.0)
        task_a.done = False
        self.assertEqual(self.project.progress, 50.0)

    def test_progress_after_deleting_a_task(self):
        task_a = self._task('A')
        task_b = self._task('B')
        task_b.done = True
        task_a.unlink()
        self.assertEqual(self.project.progress, 100.0)

    def test_task_count(self):
        self._task('A')
        self._task('B')
        self.assertEqual(self.project.task_count, 2)