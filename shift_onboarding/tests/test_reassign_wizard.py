from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class TestReassignWizard(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        partner = cls.env['res.partner'].create({'name': 'Wizard client'})
        project = cls.env['shift.onboarding.project'].create({
            'name': 'Wizard project',
            'partner_id': partner.id,
        })
        cls.old_user = cls.env['res.users'].create(
            {'name': 'Old assignee', 'login': 'wizard_old'}
        )
        cls.new_user = cls.env['res.users'].create(
            {'name': 'New assignee', 'login': 'wizard_new'}
        )
        Task = cls.env['shift.onboarding.task']
        cls.selected = Task.create([
            {'name': f'Task {i}', 'project_id': project.id,
             'assignee_id': cls.old_user.id}
            for i in range(3)
        ])
        cls.untouched = Task.create({
            'name': 'Not selected', 'project_id': project.id,
            'assignee_id': cls.old_user.id,
        })

    def _wizard(self, tasks):
        Wizard = self.env['shift.onboarding.task.reassign.wizard']
        if tasks:
            Wizard = Wizard.with_context(
                active_model='shift.onboarding.task',
                active_ids=tasks.ids,
            )
        return Wizard.create({'assignee_id': self.new_user.id})

    def test_wizard_picks_the_selected_tasks(self):
        self.assertEqual(self._wizard(self.selected).task_ids, self.selected)

    def test_reassigns_all_selected_tasks(self):
        self._wizard(self.selected).action_reassign()
        for task in self.selected:
            self.assertEqual(task.assignee_id, self.new_user)

    def test_unselected_task_is_untouched(self):
        self._wizard(self.selected).action_reassign()
        self.assertEqual(self.untouched.assignee_id, self.old_user)

    def test_empty_selection_raises(self):
        with self.assertRaises(UserError):
            self._wizard(self.env['shift.onboarding.task']).action_reassign()