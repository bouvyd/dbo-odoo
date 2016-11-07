# -*- coding: utf-8 -*-
from odoo import fields, models


class FacebookMessage(models.Model):
    _name = "fb.message"
    _description = "Facebook Messenger Message"

    sender_id = fields.Char('Sender', index=True, required=True)
    recipient_id = fields.Char('Recipient', index=True, required=True)
    msg_id = fields.Char('Remote ID')
    text = fields.Text()
    attachment_ids = fields.One2many('fb.attachment', 'fb_message_id', string='Attachments')

    def _to_fb_msg(self):
        self.ensure_one()
        msg_dict = {
            'recipient': {
                'id': self.recipient_id,
            },
        }
        if self.text:
            msg_dict['message'] = {
                'text': self.text,
            }
        elif self.attachment_ids:
            msg_dict['message'] = {
                'attachment': self.attachment_ids._to_fb_attachment()[0]
            }
        return msg_dict

    def repeat(self):
        """Return a message to its sender.

        Copy a message and inverse to sender and recipient. Attachments get
        copied as well.

        :returns: new record
        """
        new_vals = {
            'sender_id': self.recipient_id,
            'recipient_id': self.sender_id,
            'text': self.text,
            'attachment_ids': [(0, False, {'attach_type': a.attach_type, 'url': a.url}) for a in self.attachment_ids]
        }
        return self.create(new_vals)

    class FacebookAttachment(models.Model):
        _name = "fb.attachment"
        _description = 'Facebook Messenger Attachment'

        attach_type = fields.Selection(selection=[('audio', 'Audio'), ('video', 'Video'), ('image', 'Image'), ('file', 'File')], string='Attachment Type')
        url = fields.Char()
        fb_message_id = fields.Many2one('fb.message', required=True)

        def _to_fb_attachment(self):
            res = []
            for attach in self:
                res.append({
                    "type": attach.attach_type,
                    "payload": {
                        "url": attach.url,
                    }
                })
            return res
