from odoo import fields, models, api


class ShiftOnboardingProject(models.Model):
    _name = 'shift.onboarding.project'
    _description = 'Shift Onboarding Project'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True, tracking=True)
    partner_id = fields.Many2one('res.partner' , string='Client' , required=True, tracking=True)
    user_id = fields.Many2one(
        'res.users', string='Responsible',
        default=lambda self: self.env.user, tracking=True,
    )
    date_start = fields.Date()
    deadline = fields.Date()
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('in_progress', 'In Progress'),
            ('done', 'Done'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft', tracking=True,
    )
    notes = fields.Text()
    task_ids = fields.One2many('shift.onboarding.task' , 'project_id' , string='Tasks')
    task_count = fields.Integer(compute='_compute_task_count')
    progress = fields.Float(compute='_compute_progress', store=True)


    # computes fields 
    @api.depends('task_ids')
    def _compute_task_count(self):
        for project in self:
            project.task_count = len(project.task_ids)

    # compute progress if all tasks are done set state to done
    @api.depends('task_ids.done')
    def _compute_progress(self):
        for project in self:
            total = len(project.task_ids)
            done = len(project.task_ids.filtered('done'))
            project.progress = (done / total * 100.0) if total else 0.0

    # 
    def action_view_tasks(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tasks',
            'res_model': 'shift.onboarding.task',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }