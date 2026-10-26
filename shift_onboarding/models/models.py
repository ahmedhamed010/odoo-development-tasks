from odoo import fields, models, api
from odoo.exceptions import ValidationError


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
    date_start = fields.Date(tracking=True)
    deadline = fields.Date(tracking=True)
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
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', copy=False,)

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

    # view tasks method with stat button 
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

    # state change methods
    def action_start(self):
        for project in self:
            project.state = 'in_progress'

    def action_done(self):
        for project in self:
            project.state = 'done'

    def action_cancel(self):
        for project in self:
            project.state = 'cancelled'


# constraints methods
    # check if deadline is after start date
    @api.constrains('date_start' , 'deadline')
    def _check_dates(self):
        for project in self:
            if (project.date_start and project.deadline 
            and project.deadline <= project.date_start):
                raise ValidationError(
                    self.env._("The deadline must come after the start date."))
            
    
    # check if all tasks are done when state is done
    @api.constrains('state')
    def _check_open_tasks_when_done(self):
        for project in self.filtered(lambda p: p.state == 'done'):
            open_tasks = project.task_ids.filtered(lambda t: not t.done)
            if open_tasks:
                raise ValidationError(
                    self.env._(
                        "You cannot mark the project as done while tasks "
                        "are still open: %s"
                    ) % ', '.join(open_tasks.mapped('name'))
                )
            
            