odoo.define('gifts.cart', function (require) {
    "use strict";

    var base = require('web_editor.base');
    var core = require('web.core');
    var ajax = require('web.ajax');
    var _t = core._t;

    if(!$('.oe_gifts').length) {
        return $.Deferred().reject("DOM doesn't contain '.oe_gifts'");
    }

    // UI shake effect
    function shake(div){
        $(div).css('position','relative');
        for(var iter=0;iter<(3);iter++){
            $(div).animate({
                left:((iter%2==0 ? 10 : -10))
                },100);
        }
        $(div).animate({ left: 0},100);
    }

    ajax.loadXML('/gifts/static/src/xml/gift_templates.xml', core.qweb);
    var update_gift_counter = function(cart) {
        var list_count = _.reduce(_.values(cart), function(a,b){ return a + b; }, 0);
        $(".oe_gift_cart_count").html(list_count)
    };


    // cart popup display
    var cart = $('ul#top_menu li a[href$="/gifts/cart"]');
    var cart_counter;
    cart.popover({
        trigger: 'manual',
        animation: true,
        html: true,
        container: 'body',
        placement: 'bottom',
        template: '<div class="popover cart-popover" role="tooltip"><div class="arrow"></div><h3 class="popover-title"></h3><div class="popover-content"></div></div>',
    }).on("mouseenter",function (ev) {
        var self = this;
        clearTimeout(cart_counter);
        cart.not(self).popover('hide');
        cart_counter = setTimeout(function(){
            if($(self).is(':hover') && !$(".cart-popover:visible").length)
            {
                $.get("/gifts/cart", {'cart_type':'popover'})
                    .then(function (data) {
                        $(self).data("bs.popover").options.content =  data;
                        $(self).popover("show");
                        $(".popover").on("mouseleave", function () {
                            $(self).trigger('mouseleave');
                        });
                    });
            }
        }, 100);
        ajax.jsonRpc('/gifts/get/cart', 'call', {}).then(function (result) {
            update_gift_counter(result);
        });
    }).on("mouseleave", function () {
        var self = this;
        setTimeout(function () {
            if (!$(".popover:hover").length) {
                if(!$(self).is(':hover'))
                {
                   $(self).popover('hide');
                }
            }
        }, 1000);
    });

    // add to cart buttons & animations
    var animate_add_to_cart = function(e) {
        var btn = $(e.target)
        var imgtodrag = btn.parents('.product').find('.product-image').find('img');
        e.preventDefault();
        btn.attr('disabled', true);
        var btn_content = btn.html();
        btn.html('<i class="fa fa-circle-o-notch fa-spin"></i>')
        var product_id = btn.data('product-id');
        var data = {"product_id": product_id};
        ajax.jsonRpc('/gifts/add', 'call', data).then(function (result) {
            var new_btn_content = $(core.qweb.render('gift.add_btn', result))
            // re-bind event explicitly for newly rendered content
            new_btn_content.find('.oe_gift_add').on('click', {}, animate_add_to_cart);
            btn.parents('.product-btns').html(new_btn_content);
            if (imgtodrag) {
                var target = cart.is(':visible') ? cart:$('.navbar-toggle');
                var imgclone = imgtodrag.clone()
                    .offset({
                    top: imgtodrag.offset().top,
                    left: imgtodrag.offset().left
                    })
                    .css({
                        'opacity': '0.5',
                        'position': 'absolute',
                        'height': '150px',
                        'width': '150px',
                        'z-index': '100'
                    })
                    .appendTo($('body'))
                    .animate({
                        'top': target.offset().top + 10,
                        'left': target.offset().left + 100,
                        'width': 0,
                        'height': 0
                    }, 1000, 'easeInOutExpo');
                setTimeout(function () {
                    shake(target);
                }, 1000);
            }
            update_gift_counter(result.cart);
        });
    };
    $('.oe_gift_add').on('click', {}, animate_add_to_cart);

});