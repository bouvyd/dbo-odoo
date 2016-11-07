# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

from werkzeug.exceptions import NotFound, Unauthorized


class FacebookBotController(http.Controller):

    @http.route("/fb-bot/<string:bot_url>/webhook", auth="none", methods=["GET"])
    def webhook_authenticate(self, bot_url, **kw):
        bot = request.env['fb.bot'].sudo().search([('url', '=', bot_url)], limit=1)
        if not bot:
            raise NotFound()
        elif bot and not bot.verify_token == kw.get('hub.verify_token'):
            raise Unauthorized()
        else:
            return kw.get('hub.challenge')

    @http.route("/fb-bot/<string:bot_url>/webhook", auth="none", type="json")
    def webhook_listen(self, bot_url, **kw):
        bot = request.env['fb.bot'].sudo().search([('url', '=', bot_url)], limit=1)
        if not bot:
            raise NotFound()
        fb_update = request.jsonrequest
        for msg in fb_update['entry'][0]['messaging']:
            bot.process_message(msg)
