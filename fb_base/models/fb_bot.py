# -*- coding: utf-8 -*-
from odoo import api, fields, models

from odoo.tools import ustr

import json
from slugify import slugify
import urllib2


class FacebookBot(models.Model):
    _name = "fb.bot"
    _description = "Facebook Messenger Bot"

    name = fields.Char(required=True)
    url = fields.Char(readonly=True, compute="_compute_url", store=True)
    verify_token = fields.Char("Verify Token", required=True, groups="base.group_system")
    greeting_text = fields.Text("Greeting Text", help="The Greeting Text is only rendered "
                                "the first time the user interacts with a the Page on Messenger. "
                                "This can be used to communicate your bot's functionality. If the "
                                "greeting text is not set, the page description will be shown in the welcome screen.")
    user_link = fields.Boolean("Allow log in", help="If set, this option will allow users of the bot "
                               "to log into the Odoo database for a more personnalized experience.")
    page_token = fields.Char("Page Access Token", required=True)

    _sql_constraints = [('name_uniq', 'unique(name)', 'Bot name must be unique.')]

    @api.depends('name')
    def _compute_url(self):
        for bot in self:
            bot.url = slugify(ustr(bot.name))

    def process_message(self, msg):
        """Process a facebook message.

        Process a facebook messenger message according to its type. Trigger responses
        when necessary according to existing overrides. Always returns True.

        param: msg dict: received message as detailed in
            https://developers.facebook.com/docs/messenger-platform/webhook-reference/message
        :rtype: bool
        return: True
        """
        msg_vals = {
            'sender_id': msg['sender']['id'],
            'recipient_id': msg['recipient']['id'],
            'text': msg['message'].get('text'),
            'attachment_ids': [(0, False, {'attach_type': a['type'], 'url': a['payload']['url']}) for a in msg['message'].get('attachments', [])],
            'msg_id': msg['message']['mid'],
        }
        msg = self.env['fb.message'].create(msg_vals)
        reply = msg.repeat()
        self.post_facebook_message(reply)
        return True

    def post_facebook_message(self, message):
        post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s' % self.page_token
        response_msg = json.dumps(message._to_fb_msg())
        urequest = urllib2.Request(post_message_url, response_msg, {'content-type': 'application/json'})
        uopen = urllib2.urlopen(urequest)
        resp = json.loads(uopen.read())
        if 'message_id' in resp:
            message.msg_id = resp['message_id']
            return True
        else:
            return False
