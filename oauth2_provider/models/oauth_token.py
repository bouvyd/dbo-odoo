# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from oauthlib.common import generate_token

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from const import DEFAULT_TOKEN_VALIDITY, DEFAULT_AUTH_CODE_VALIDITY


class AbstractToken(models.AbstractModel):
    _name = "oauth.abstract_token"
    _description = "OAuth2 Token-type meta-model"
    _order = "expiration_time desc, id desc"

    EXPIRATION_TIME = 0
    IR_PARAM_KEY = False

    @api.model
    def _default_token(self):
        return generate_token()

    @api.model
    def _default_expiration_time(self):
        expiration_delta = int(self.env['ir.config_parameter'].get_param(self.IR_PARAM_KEY, default=self.EXPIRATION_TIME))
        return fields.Datetime.to_string(datetime.now() + timedelta(minutes=expiration_delta))

    active = fields.Boolean(string="Active", compute="_compute_active", search="_search_active", inverse="_inverse_active")
    client_id = fields.Many2one("oauth.client", string="Client ID", required=True)
    user_id = fields.Many2one("res.users", string="User", required=True)
    scope_ids = fields.Many2many("oauth.scope", string="Scopes",
                                 help="Scopes available to the client. At least one should be set.")
    scopes = fields.Char(string="Scopes (text)", help="Textual representation of scopes for easier scope testing.",
                         compute="_compute_scope_text", inverse="_inverse_scope_text", store=True)
    expiration_time = fields.Datetime(string="Expiration Time", required=True, default=_default_expiration_time)

    @api.depends('scope_ids', 'scope_ids.name')
    def _compute_scope_text(self):
        """
        Seralize scopes into a string.

        Serializing scopes allows to adhere more closesly to the oauthlib spirit,
        makes code more readable.
        """
        for token in self:
            token.scopes = ' '.join(token.scope_ids.mapped('name'))

    def _inverse_scope_text(self):
        for client in self:
            scope_ids = self.env['oauth.scope'].search([('name', 'in', client.scopes.split())])
            if len(client.scopes.split()) != len(scope_ids):
                raise ValidationError('Invalid scopes')
            client.scope_ids = scope_ids

    @api.depends('expiration_time')
    def _compute_active(self):
        """
        Check if tokens is are active.

        A token is considered active if its expiration time is in the future.
        """
        for token in self:
            token.active = token.expiration_time > fields.Datetime.now()

    def _search_active(self, operator, value):
        """Search function for the active field."""
        operator = '>' if (operator, value) in [('=', True), ('!=', False)] else '<='
        return [('expiration_time', operator, fields.Datetime.now())]

    def _inverse_active(self):
        """Set the expiration time in the past/future on 'active' toggle."""
        for token in self:
            if token.active:
                token.expiration_time = self._default_expiration_time()
            if not token.active:
                token.revoke()

    def revoke(self):
        """
        Revoke tokens.

        Revoke tokens by setting their expiration time in the past, making
        their active field False by definition of its compute function.
        """
        close_past = datetime.now() - timedelta(minutes=1)
        return self.write({'expiration_time': fields.Datetime.to_string(close_past)})


class OauthToken(models.Model):
    _name = "oauth.token"
    _inherit = "oauth.abstract_token"
    _description = "OAuth2 Token"
    _rec_name = "access_token"

    EXPIRATION_TIME = DEFAULT_TOKEN_VALIDITY
    IR_PARAM_KEY = 'oauth2_provider.token_expiration_time'

    access_token = fields.Char(string="Access Token", default=lambda s: s._default_token(), required=True)
    refresh_token = fields.Char(string="Refresh Token", default=lambda s: s._default_token(), required=True)

    _sql_constraints = [
        ('uniq_access_token', 'unique(access_token)', 'Access Token must be unique.'),
        ('uniq_refresh_token', 'unique(refresh_token)', 'Refresh Token must be unique.')
    ]


class OauthAuthCode(models.Model):
    _name = "oauth.auth_code"
    _inherit = "oauth.abstract_token"
    _description = "OAuth2 Authorization Code"
    _rec_name = "authorization_code"

    EXPIRATION_TIME = DEFAULT_AUTH_CODE_VALIDITY
    IR_PARAM_KEY = 'oauth2_provider.auth_code_expiration_time'

    authorization_code = fields.Char(string="Authorization Code", default=lambda s: s._default_token(), required=True)
    redirect_uri = fields.Char(string="Redirect URI", required=True)

    _sql_constraints = [('uniq_authorization_code', 'unique(authorization_code)', 'Authorization Code must be unique.')]

    def redirect_uri_allowed(self, uri):
        self.ensure_one()
        return uri == self.redirect_uri
