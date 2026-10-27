from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestProgressEdgeCases(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Edge client'})
        cls.Project = cls.env['shift.onboarding.project']
        cls.Task = cls.env['shift.onboarding.task']
        cls.project = cls._project('Main')

    @classmethod
    def _project(cls, name):
        return cls.Project.create(
            {'name': name, 'partner_id': cls.partner.id}
        )

    def _task(self, name, project=None, done=False):
        return self.Task.create({
            'name': name,
            'project_id': (project or self.project).id,
            'done': done,
        })

    def test_progress_field_is_stored(self):
        self.assertTrue(self.Project._fields['progress'].store)

    def test_progress_is_the_share_of_done_tasks(self):
        self._task('A', done=True)
        self._task('B')
        self._task('C')
        self.assertAlmostEqual(self.project.progress, 100 / 3, places=2)

    def test_progress_is_100_when_every_task_is_done(self):
        self._task('A', done=True)
        self._task('B', done=True)
        self.assertEqual(self.project.progress, 100.0)

    def test_task_created_as_done_counts_immediately(self):
        self._task('A', done=True)
        self._task('B')
        self.assertEqual(self.project.progress, 50.0)

    def test_progress_is_not_shared_between_projects(self):
        other = self._project('Other')
        self._task('A', done=True)
        self._task('B', project=other)
        self.assertEqual(self.project.progress, 100.0)
        self.assertEqual(other.progress, 0.0)

    def test_moving_a_task_updates_both_projects(self):
        other = self._project('Other')
        done_task = self._task('A', done=True)
        self._task('B')
        self.assertEqual(self.project.progress, 50.0)
        done_task.project_id = other
        self.assertEqual(self.project.progress, 0.0)
        self.assertEqual(other.progress, 100.0)


class TestCannotFinishRule(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        partner = cls.env['res.partner'].create({'name': 'Rule client'})
        cls.Task = cls.env['shift.onboarding.task']
        cls.project = cls.env['shift.onboarding.project'].create(
            {'name': 'Rule project', 'partner_id': partner.id}
        )

    def _task(self, name, done=False):
        return self.Task.create(
            {'name': name, 'project_id': self.project.id, 'done': done}
        )

    def test_error_names_every_open_task(self):
        self._task('Open one')
        self._task('Open two')
        self.project.action_start()
        with self.assertRaisesRegex(ValidationError, 'Open one.*Open two'):
            self.project.action_done()

    def test_one_done_and_one_open_is_still_blocked(self):
        self._task('Finished', done=True)
        self._task('Still open')
        self.project.action_start()
        with self.assertRaises(ValidationError):
            self.project.action_done()
        self.assertEqual(self.project.state, 'in_progress')

    def test_writing_state_directly_is_also_blocked(self):
        self._task('Open')
        with self.assertRaises(ValidationError):
            self.project.write({'state': 'done'})

    def test_project_without_tasks_can_be_finished(self):
        self.project.action_start()
        self.project.action_done()
        self.assertEqual(self.project.state, 'done')

    def test_can_finish_after_the_last_task_is_ticked(self):
        task = self._task('Last')
        self.project.action_start()
        with self.assertRaises(ValidationError):
            self.project.action_done()
        task.done = True
        self.project.action_done()
        self.assertEqual(self.project.state, 'done')

    def test_cancel_is_allowed_with_open_tasks(self):
        self._task('Open')
        self.project.action_cancel()
        self.assertEqual(self.project.state, 'cancelled')