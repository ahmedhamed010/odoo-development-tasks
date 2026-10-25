from odoo import fields, models


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