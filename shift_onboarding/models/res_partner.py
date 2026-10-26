from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    onboarding_project_count = fields.Integer(
        compute='_compute_onboarding_project_count',
    )

    def _compute_onboarding_project_count(self):
        Project = self.env['shift.onboarding.project']
        for partner in self:
            partner.onboarding_project_count = Project.search_count(
                [('partner_id', '=', partner.id)]
            )

    def action_view_onboarding_projects(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Onboarding Projects',
            'res_model': 'shift.onboarding.project',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }