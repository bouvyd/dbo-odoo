# -*- coding: utf-8 -*-
from oauthlib.oauth2 import RequestValidator
from odoo.http import request as oe_request


class MyRequestValidator(RequestValidator):

    def confirm_redirect_uri(client_id, code, redirect_uri, client, *args, **kwargs):
        auth_code_id = oe_request.env['oauth.auth_code'].sudo().search([('client_id', '=', client_id), ('code', '=', code)])
        return auth_code_id.redirect_uri_allowed(redirect_uri)

    def get_default_redirect_uri(self, client_id, request, *args, **kwargs):
        return oe_request.env['oauth.client'].sudo().search([('id', '=', client_id)], limit=1).default_redirect_uri

    def get_default_scopes(self, client_id, request, *args, **kwargs):
        return oe_request.env['oauth.client'].sudo().search([('id', '=', client_id)], limit=1).scopes

    def get_original_scopes(self, refresh_token, request, *args, **kwargs):
        return oe_request.env['oauth.token'].sudo().search([('refresh_token', '=', refresh_token)]).scopes

    def is_within_original_scope(self, request_scopes, refresh_token, request, *args, **kwargs):
        token_scopes = oe_request.env['oauth.token'].sudo().search([('refresh_token', '=', refresh_token)]).scopes
        return set(request_scopes.split()) == set(token_scopes.split())

    def invalidate_authorization_code(self, client_id, code, request, *args, **kwargs):
        oe_request.env['oauth.auth_code'].sudo().search([('client_id', '=', client_id), ('code', '=', code)]).revoke()

    def revoke_token(self, token, token_type_hint, request, *args, **kwargs):
        oe_request.env['oauth.token'].sudo().search([(token_type_hint, '=', token)]).revoke()

    def save_authorization_code(self, client_id, code, request, *args, **kwargs):
        oe_request.env['oauth.auth_code'].sudo().create({
            'client_id': client_id,
            'user_id': request.user.id,
            'authorization_code': code['code'],
            'state': code.get('state'),
            'redirect_uri': request.redirect_uri,
            'scopes': ' '.join(request.scopes),
        })

    def save_bearer_token(self, token, request, *args, **kwargs):
        # TODO: this is probably all wrong.
        oe_request.env['oauth.token'].sudo().create({
            'client_id': request.client,
            'user_id': request.user,
            'access_token': token.get('access_token'),
            'refresh_token': token.get('refresh_token'),
            'state': token.get('state'),
            'redirect_uri': request.redirect_uri,
            'scopes': ' '.join(token.get('scope', '')),
        })

    def validate_client_id(self, client_id, request):
        return bool(oe_request.env['oauth.client'].sudo().search([('id', '=', client_id)], limit=1))
