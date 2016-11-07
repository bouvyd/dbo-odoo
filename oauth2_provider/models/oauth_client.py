# -*- coding: utf-8 -*-
import logging
from uuid import uuid4

from odoo import api, fields, models, tools
from odoo.modules.module import get_module_resource

_logger = logging.getLogger(__name__)

try:
    import pagan  # random avatar library that I want
    import base64
    try:
        import cStringIO as StringIO
    except ImportError:
        import StringIO
except ImportError:
    pagan = None
    _logger.warning("Pagan library not found, no random avatar for clients :'-(")


class OauthClient(models.Model):
    _name = "oauth.client"
    _description = "OAuth2 Client"

    AUTH_TYPES = [('auth', 'Authorization'),
                  ('implicit', 'Implicit'),
                  ('password', 'Resource Owner Password Credentials'),
                  ('client', 'Client Credentials')]

    @api.model
    def _default_scopes(self):
        return self.env['oauth.scope'].search([('default', '=', True)])

    @api.model
    def _default_image(self):
        if pagan:
            avatar = pagan.Avatar('%s-%s' % (self, fields.Datetime.now()))
            buffer = StringIO.StringIO()
            avatar.img.save(buffer, format="PNG")
            return base64.b64encode(buffer.getvalue())
        image_path = get_module_resource('oauth2_provider', 'static/src/img', 'default_client_image.png')
        return tools.image_resize_image_big(open(image_path, 'rb').read().encode('base64'))

    name = fields.Char(required=True, help="The Client's name will be displayed in the authorization "
                       "request.")
    active = fields.Boolean()
    client_id = fields.Char(string="Client ID", required=True, index=True, default=lambda s: uuid4(),
                            help="Unique client ID used in the OAuth authorization process.")
    user_id = fields.Many2one("res.users", string="User", required=True,
                              help="User responsible for this client.")
    grant_type = fields.Selection(AUTH_TYPES, string="Grant Type", help="Grant Type given to user of this client:\n"
                                  "- Authorization: for clients who can hide a secret (web server)\n"
                                  "- Implicit: for use in web/mobile clients\n"
                                  "- Resource Owner Password Credentials: for internal/trusted clients\n"
                                  "- Client Credentials: for clients themselves\n")
    scope_ids = fields.Many2many("oauth.scope", "oauth_client_scope_rel", "client_id", "scope_id",
                                 string="Scopes", default=_default_scopes,
                                 help="Scopes available to the client. At least one should be set.")
    scopes = fields.Char(string="Scopes (text)", help="Textual representation of scopes for easier scope testing.",
                         compute="_compute_scope_text", store=True, readonly=True)
    redirect_uris = fields.Text(string="Redirect URIs", help="Authorized redirect URIs for this client.")
    default_redirect_uri = fields.Char(string="Default Redirect URI", help="Default redirect URI for this client,"
                                       " will be used if none is provided in the initial request.")
    token_ids = fields.One2many("oauth.token", "client_id", string="Tokens")
    auth_code_ids = fields.One2many("oauth.auth_code", "client_id", string="Authorization Codes")
    # image: all image fields are base64 encoded and PIL-supported
    image = fields.Binary(default=_default_image, attachment=True, help="Image displayd in authorization dialog, "
                          "limited to 1024x1024px.")
    image_medium = fields.Binary("Medium-sized photo", attachment=True, help="Image resized to 128x128px.")
    image_small = fields.Binary("Small-sized photo", attachment=True, help="Image resized to 64x64px.")

    _sql_constraints = [("uniq_client_id", "unique(client_id)", "Client ID must be unique.")]

    @api.depends('scope_ids', 'scope_ids.name')
    def _compute_scope_text(self):
        for client in self:
            client.scopes = ' '.join(client.scope_ids.mapped('name'))

    @api.multi
    def write(self, vals):
        res = super(OauthClient, self).write(vals)
        if 'active' in vals and not vals.get('active'):
            # revoking a client expires all its currently active tokens and authorization codes
            self.token_ids.revoke()
            self.auth_code_ids.revoke()
        return res

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        return super(OauthClient, self).create(vals)


class OauthScope(models.Model):
    _name = "oauth.scope"
    _description = "OAuth2 Scope"

    name = fields.Char(required=True)
    default = fields.Boolean(help="Default scopes will be automatically included in authorization requests.")
    description = fields.Text(help="Short textual description of the scope, will be "
                              "displayed in the authorization request to the resource owner.")
    color = fields.Integer()

    _sql_constraints = [("single_word_name", "CHECK (name ~ '^[a-z]+$')", "Scope name must only contain lowercase characters in [a-z] (single word).")]
