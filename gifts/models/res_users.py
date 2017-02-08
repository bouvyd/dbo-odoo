from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = "res.users"

    list_ids = fields.One2many("gift.list", inverse_name="user_id", string="Gift Lists")
