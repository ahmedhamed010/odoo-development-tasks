from odoo import fields, models


class ShiftOnboardingTask(models.Model):
    _name = 'shift.onboarding.task'
    _description = 'Shift Onboarding Task'
    
    name = fields.Char(required=True)
    deadline = fields.Date()
    assignee_id = fields.Many2one('res.users' , string='Assignee')
    project_id = fields.Many2one('shift.onboarding.project' , string='Project' , required=True , ondelete='cascade')
    done = fields.Boolean()
