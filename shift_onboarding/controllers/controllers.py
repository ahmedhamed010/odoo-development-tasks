# from odoo import http


# class ShiftOnboarding(http.Controller):
#     @http.route('/shift_onboarding/shift_onboarding', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/shift_onboarding/shift_onboarding/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('shift_onboarding.listing', {
#             'root': '/shift_onboarding/shift_onboarding',
#             'objects': http.request.env['shift_onboarding.shift_onboarding'].search([]),
#         })

#     @http.route('/shift_onboarding/shift_onboarding/objects/<model("shift_onboarding.shift_onboarding"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('shift_onboarding.object', {
#             'object': obj
#         })

