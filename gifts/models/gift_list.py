from odoo import models, fields, api


class GiftList(models.Model):
    _name = "gift.list"

    name = fields.Char(string="Name", required=True)
    user_id = fields.Many2one("res.users", string="User", required=True, default=lambda s: s.env.user)
    product_ids = fields.One2many("gift.product", inverse_name="list_id", string="Products")
    website_visible = fields.Boolean('Listed on website', default=False)
