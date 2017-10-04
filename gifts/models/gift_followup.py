# -*- coding: utf-8 -*-
from odoo import api, fields, models


class GiftFollowup(models.Model):
    _name = 'gift.followup'
    _description = 'Gift Followup'
    _inherit = ['mail.thread']

    def _default_account(self):
        return self.env['gift.account'].search([], limit=1, order="sequence asc")

    gifter_id = fields.Many2one('res.partner', string="From")
    gift_ids = fields.Many2many('gift.gift', string="Gifts")
    price = fields.Float(string="Total")
    gift_date = fields.Date('Gift Date', default=fields.Date.today)
    date = fields.Date('Send Date')
    state = fields.Selection([('todo', 'To Do'), ('sent', 'Sent'), ('paid', 'Paid'), ('thanks', 'Thanked')], default="todo", track_visibility='onchange')
    account_id = fields.Many2one('gift.account', string='Bank Account', default=_default_account)
    message = fields.Text(string="Gift message")
    baby_name = fields.Char(string="Name proposal")
    baby_date = fields.Date(string="Birth date proposal")
    new_field = fields.Boolean('Hello There')

    @api.multi
    def force_send_followup(self):
        template = self.env.ref('gifts.mail_template_followup')
        for followup in self:
            followup.message_post_with_template(template_id=template.id)
            followup.state = 'sent'

    @api.multi
    def set_paid(self):
        self.write({'state': 'paid'})

    @api.multi
    def set_thanks(self):
        self.write({'state': 'thanks'})

    @api.multi
    def name_get(self):
        result = []
        for followup in self:
            result.append((followup.id, followup.gifter_id.name))
        return result


class GiftAccount(models.Model):
    _name = 'gift.account'
    _description = 'Gift Bank Account'

    name = fields.Char()
    payment_msg = fields.Html('Payment Message')
    sequence = fields.Integer()
