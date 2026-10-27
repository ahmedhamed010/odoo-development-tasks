from odoo import fields, models, api


class ShiftOnboardingTask(models.Model):
    _name = 'shift.onboarding.task'
    _description = 'Shift Onboarding Task'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(required=True)
    deadline = fields.Date()
    assignee_id = fields.Many2one('res.users' , string='Assignee')
    project_id = fields.Many2one('shift.onboarding.project' , string='Project' , required=True , ondelete='cascade')
    done = fields.Boolean()



    @api.model
    def _cron_create_overdue_activities(self):
        today = fields.Date.context_today(self)
        overdue_tasks = self.search([
            ('done', '=', False),
            ('deadline', '<', today),
            ('assignee_id', '!=', False),
        ])
        for task in overdue_tasks:
            already_flagged = task.activity_ids.filtered(
                lambda a: a.summary == 'Overdue task'
            )
            if already_flagged:
                continue
            task.activity_schedule(
                'mail.mail_activity_data_todo',
                date_deadline=today,
                summary='Overdue task',
                note=self.env._(
                    "The task '%s' passed its deadline and is not done yet."
                ) % task.name,
                user_id=task.assignee_id.id,
            )
