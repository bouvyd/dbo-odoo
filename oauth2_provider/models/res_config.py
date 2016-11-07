# -*- coding: utf-8 -*-
from odoo import api, fields, models

from const import DEFAULT_TOKEN_VALIDITY, DEFAULT_AUTH_CODE_VALIDITY


class OauthConfiguration(models.TransientModel):
    _name = 'oauth.config.settings'
    _inherit = 'res.config.settings'

    token_expiration = fields.Integer(string="Token expiration time", default=60)
    auth_code_expiration = fields.Integer(string="Authorization Code expiration time", default=10)
    module_website_oauth2 = fields.Boolean(string="Allow Client creation request")

    @api.model
    def get_default_token_expiration(self, fields):
        token_expiration = int(self.env["ir.config_parameter"].get_param("oauth2_provider.token_expiration_time", default=DEFAULT_TOKEN_VALIDITY))
        return {'token_expiration': token_expiration}

    @api.multi
    def set_token_expiration(self):
        for record in self:
            self.env['ir.config_parameter'].set_param("oauth2_provider.token_expiration_time", record.token_expiration or DEFAULT_TOKEN_VALIDITY)

    @api.model
    def get_default_auth_code_expiration(self, fields):
        auth_code_expiration = int(self.env["ir.config_parameter"].get_param("oauth2_provider.auth_code_expiration_time", default=DEFAULT_AUTH_CODE_VALIDITY))
        return {'auth_code_expiration': auth_code_expiration}

    @api.multi
    def set_auth_code_expiration(self):
        for record in self:
            self.env['ir.config_parameter'].set_param("oauth2_provider.auth_code_expiration_time", record.auth_code_expiration or DEFAULT_AUTH_CODE_VALIDITY)
