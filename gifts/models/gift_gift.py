# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import image_resize_images
from odoo.addons.website.models.website import slug


class GiftProduct(models.Model):
    _name = 'gift.product'
    _description = 'Gift Product'
    _inherit = ['mail.thread', 'website.published.mixin']
    _order = "sequence asc"

    name = fields.Char(string="Name")
    price = fields.Float()
    gift_price = fields.Float(string="Price per gift", compute="_compute_qty")
    allow_split = fields.Boolean(string="Allow Splitting")
    unlimited = fields.Boolean(string="Unlimited", help="If checked, this product can be offered an unlimited number of times. Useful for giftcards, for example.")
    split_number = fields.Integer(string="Number of gifts initially available for this product", default=1)
    qty_available = fields.Integer(string="Quantity available", compute="_compute_qty")
    gift_ids = fields.One2many('gift.gift', string="Gifts", inverse_name='product_id')
    list_id = fields.Many2one('gift.list', string="List")
    description_html = fields.Html(string="Online Description")
    state = fields.Selection([('new', 'New'), ('partial', 'Partially Offered'), ('done', 'Offered'), ('ongoing', 'Ongoing')], compute='_compute_state', store=True, track_visibility='onchange')
    image = fields.Binary("Image", attachment=True, help="Limited to 1024x1024px",)
    image_medium = fields.Binary("Medium-sized image", attachment=True)
    image_small = fields.Binary("Small-sized image", attachment=True)
    sequence = fields.Integer(string="Sequence order", default=10)

    @api.multi
    def _website_url(self, name, arg):
        res = super(GiftProduct, self)._website_url(name, arg)
        res.update({(p.id, '/gifts/product/%s' % slug(p)) for p in self})
        return res

    @api.multi
    def open_website_url(self):
        return {
            'type': 'ir.actions.act_url',
            'url': self.website_url,
            'target': 'self',
        }

    @api.onchange('split_number', 'allow_split', 'price')
    def onchange_split_number(self):
        if self.state != 'new':
            raise UserError('You cannot change the number of portions once the gift has been (partially) offered.')
        else:
            if not self.allow_split:
                self.split_number = 1
            self.update({'gift_ids': [(0, False, {'price': self.price / self.split_number}) for x in range(0, self.split_number)]})

    @api.multi
    @api.depends('gift_ids', 'gift_ids.gifter_id', 'split_number', 'price')
    def _compute_qty(self):
        for product in self:
            product.qty_available = -1 if product.unlimited else len(product.gift_ids.filtered(lambda r: not r.gifter_id))
            product.gift_price = product.price if product.unlimited else product.price / product.split_number

    @api.multi
    @api.depends('gift_ids.gifter_id')
    def _compute_state(self):
        for product in self:
            if product.unlimited and product.gift_ids:
                product.state = 'ongoing'
                continue
            if product.gift_ids and all([g.gifter_id for g in product.gift_ids]):
                product.state = 'done'
                continue
            if product.gift_ids and any([g.gifter_id for g in product.gift_ids]):
                product.state = 'partial'
            else:
                product.state = 'new'

    @api.multi
    def write(self, vals):
        image_resize_images(vals)
        return super(GiftProduct, self).write(vals)

    @api.multi
    def unlink(self):
        if any(map(lambda s: s != 'new', self.mapped('state'))):
            raise UserError('You cannot delete a gift which has been (partially) offered.')
        return super(GiftProduct, self).unlink()

    @api.model
    def create(self, vals):
        image_resize_images(vals)
        product = super(GiftProduct, self).create(vals)
        product.onchange_split_number()
        return product


class GiftGift(models.Model):
    _name = 'gift.gift'
    _description = 'Gift'

    name = fields.Char(related="product_id.name", readonly=True)
    product_id = fields.Many2one('gift.product', string="Product", required=True, ondelete="cascade")
    gifter_id = fields.Many2one('res.partner', string="From")
    price = fields.Float(string="Value", readonly=True)

    @api.multi
    def action_view_followup(self):
        self.ensure_one()
        action = self.env.ref('gifts.gift_followup_action')
        followup = self.env['gift.followup'].search([('gift_ids', 'in', self.id)])

        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [(False, 'form')],
            'res_id': followup.id,
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
