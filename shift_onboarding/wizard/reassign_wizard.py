from odoo import api, fields, models
from odoo.exceptions import UserError


class ShiftOnboardingTaskReassignWizard(models.TransientModel):
    _name = 'shift.onboarding.task.reassign.wizard'
    _description = 'Reassign Onboarding Tasks'

    task_ids = fields.Many2many('shift.onboarding.task', string='Tasks')
    assignee_id = fields.Many2one(
        'res.users', string='New Assignee', required=True,
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self.env.context.get('active_model') == 'shift.onboarding.task':
            res['task_ids'] = [
                (6, 0, self.env.context.get('active_ids', []))
            ]
        return res

    def action_reassign(self):
        self.ensure_one()
        if not self.task_ids:
            raise UserError(self.env._("Select at least one task."))
        self.task_ids.write({'assignee_id': self.assignee_id.id})
        return {'type': 'ir.actions.act_window_close'}