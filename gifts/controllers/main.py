# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class GiftController(http.Controller):

    @http.route(['/list/<model("gift.list"):gift_list>'], type='http', auth="public", website=True)
    def gifts(self, gift_list, **kw):
        products = request.env['gift.product'].search([('list_id', '=', gift_list.id)])
        cart = request.session.get('gifts_cart', dict())
        cart_products = [{'product': p, 'qty': cart.get(p.id)} for p in request.env['gift.product'].browse(cart.keys())]
        return request.render('gifts.gifts', {'cart_products': cart_products, 'products': products})

    @http.route(['/gifts/product/<model("gift.product"):product>'], type='http', auth="public", website=True)
    def product_details(self, product, **kw):
        return request.render('gifts.product_details_page', {'product': product})

    @http.route(['/gifts/add/<model("gift.product"):product>'], type='http', auth="public", website=True)
    def add(self, product, **kw):
        cart = request.session.get('gifts_cart', dict())
        cur_qty = cart.get(product.id, 0)
        new_qty = cur_qty + 1 if product.unlimited else min(product.qty_available, cur_qty + 1)
        cart.update({product.id: new_qty})
        request.session['gifts_cart'] = cart
        return request.redirect('/gifts')

    @http.route(['/gifts/add/'], type='json', auth="public", website=True)
    def add_json(self, product_id, **kw):
        product = request.env['gift.product'].browse(product_id)
        self.add(product, **kw)
        cart = self.get_cart()
        product_data = product.read(['id', 'unlimited', 'qty_available'])
        return {'cart': cart, 'product': product_data and product_data[0]}

    @http.route(['/gifts/get/cart'], type="json", auth="public", website=True)
    def get_cart(self, **kw):
        return request.session.get('gifts_cart', dict())

    @http.route(['/gifts/cart'], type='http', auth="public", website=True)
    def cart(self, cart_type='page', **kw):
        cart = request.session.get('gifts_cart', dict())
        cart_products = [{'product': p, 'qty': cart.get(p.id)} for p in request.env['gift.product'].browse(cart.keys())]
        countries = request.env['res.country'].search_read(domain=[], fields=['id', 'name'], order="name asc")
        if cart_type == 'popover':
            return request.render('gifts.cart_popover', {'cart_products': cart_products})
        else:
            if kw.get('email'):
                Partner = request.env['res.partner']
                Gift = request.env['gift.gift']
                Product = request.env['gift.product']
                Followups = request.env['gift.followup']
                mandatory_fields = set(['name', 'email'])
                if request.env['ir.config_parameter'].sudo().get_param('gifts.address_mandatory'):
                    mandatory_fields |= set(['street', 'zip_code', 'city'])
                gifts = Gift.browse()
                gift_conflict = {}
                gift_unltd = []
                for (product_id, qty) in cart.iteritems():
                    product = Product.sudo().browse(product_id)
                    qty_available = product.qty_available
                    if not product.unlimited:
                        if qty_available < qty:
                            gift_conflict[product_id] = qty_available
                        gifts |= Gift.search([('product_id', '=', product_id), ('gifter_id', '=', False)], limit=min(qty_available, qty))
                    else:
                        gift_unltd.append((qty, {'product_id': product_id, 'price': product.price}))
                errors = {
                    'missing': filter(None, [not kw.get(field) and field for field in mandatory_fields]),
                    'mail_invalid': kw.get('email') and '@' not in kw.get('email', ''),
                    'gift_conflict': gift_conflict
                }
                if any([error for (key, error) in errors.iteritems()]):
                    if errors.get('gift_conflict'):
                        cart.update(gift_conflict)
                        cart = {k: v for k, v in cart.items() if v}
                        cart_products = [{'product': p, 'qty': cart.get(p.id)} for p in request.env['gift.product'].browse(cart.keys())]
                        request.session['gifts_cart'] = cart
                    return request.render('gifts.cart', {'cart_products': cart_products, 'errors': errors, 'values': kw, 'countries': countries})
                partner_id = Partner.sudo().search([('email', '=', kw.get('email'))], limit=1)
                if not partner_id:
                    partner_vals = {
                        'name': kw.get('name'),
                        'email': kw.get('email'),
                        'street': kw.get('street'),
                        'street2': kw.get('street2'),
                        'zip': kw.get('zip_code'),
                        'city': kw.get('city'),
                        'country_id': kw.get('country_id') and int(kw.get('country_id')),
                    }
                    partner_id = Partner.sudo().create(partner_vals)
                partner_id.category_id |= request.env.ref('gifts.gift_category')
                if gift_unltd:
                    for qty, gift_vals in gift_unltd:
                        for iter in range(0, qty):
                            gifts |= Gift.sudo().create(gift_vals)
                gifts.sudo().write({'gifter_id': partner_id.id})
                followup_vals = {
                    'gifter_id': partner_id.id,
                    'gift_ids': [(4, gift.id, False) for gift in gifts],
                    'price': sum([p['product'].gift_price * p['qty'] for p in cart_products]),
                    'message': kw.get('message'),
                    'baby_date': kw.get('date') or False,
                    'baby_name': kw.get('baby_name'),
                }
                followup = Followups.sudo().create(followup_vals)
                followup.force_send_followup()
                request.session['gifts_cart'] = {}
                request.session['thanks_cart'] = cart
                request.session['account_id'] = followup.account_id.id
                return request.redirect('/gifts/thanks')
            return request.render('gifts.cart', {'cart_products': cart_products, 'errors': dict(), 'values': dict(), 'countries': countries})

    @http.route(['/gifts/cart/empty'], type='http', auth="public", website=True)
    def empty_cart(self, **kw):
        request.session['gifts_cart'] = {}
        return request.redirect('/gifts')

    @http.route(['/gifts/thanks'], type='http', auth="public", website=True)
    def thanks(self, **kw):
        active_cart = request.session.get('gifts_cart')
        if active_cart:
            return request.redirect('/gifts/cart')
        cart = request.session.get('thanks_cart')
        cart_products = [{'product': p, 'qty': cart.get(p.id)} for p in request.env['gift.product'].browse(cart.keys())]
        payment_msg = request.env['gift.account'].browse(request.session.get('account_id')).payment_msg
        return request.render('gifts.thanks', {'payment_msg': payment_msg, 'cart_products': cart_products})
