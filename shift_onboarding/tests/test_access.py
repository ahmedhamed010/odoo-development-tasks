from odoo import Command
from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestProjectAccess(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Users = cls.env['res.users'].with_context(no_reset_password=True)
        cls.user_a = Users.create({'name': 'A', 'login': 'sob_a', 'email': 'a@test.com'})
        cls.user_b = Users.create({'name': 'B', 'login': 'sob_b', 'email': 'b@test.com'})
        cls.manager = Users.create({'name': 'M', 'login': 'sob_m', 'email': 'm@test.com'})
        cls.env.ref('shift_onboarding.group_shift_onboarding_user').write(
            {'user_ids': [Command.link(cls.user_a.id), Command.link(cls.user_b.id)]})
        cls.env.ref('shift_onboarding.group_shift_onboarding_manager').write(
            {'user_ids': [Command.link(cls.manager.id)]})

        partner = cls.env['res.partner'].create({'name': 'Client'})
        Project = cls.env['shift.onboarding.project']
        cls.p_a = Project.create({'name': 'PA', 'partner_id': partner.id, 'user_id': cls.user_a.id})
        cls.p_b = Project.create({'name': 'PB', 'partner_id': partner.id, 'user_id': cls.user_b.id})
        Task = cls.env['shift.onboarding.task']
        cls.t_a = Task.create({'name': 'TA', 'project_id': cls.p_a.id})
        cls.t_b = Task.create({'name': 'TB', 'project_id': cls.p_b.id})

    def _search(self, model, user):
        ids = (self.p_a | self.p_b).ids if model == 'shift.onboarding.project' \
            else (self.t_a | self.t_b).ids
        return self.env[model].with_user(user).search([('id', 'in', ids)])

    def test_user_sees_only_own_projects(self):
        self.assertEqual(self._search('shift.onboarding.project', self.user_a), self.p_a)

    def test_user_cannot_read_or_write_others_project(self):
        with self.assertRaises(AccessError):
            self.p_b.with_user(self.user_a).read(['name'])
        with self.assertRaises(AccessError):
            self.p_b.with_user(self.user_a).write({'name': 'hacked'})

    def test_user_sees_only_own_project_tasks(self):
        self.assertEqual(self._search('shift.onboarding.task', self.user_a), self.t_a)

    def test_manager_sees_everything(self):
        self.assertEqual(
            self._search('shift.onboarding.project', self.manager), self.p_a | self.p_b)
        self.assertEqual(
            self._search('shift.onboarding.task', self.manager), self.t_a | self.t_b)