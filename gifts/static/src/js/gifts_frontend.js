odoo.define('gifts.cart', function (require) {
"use strict";

var base = require('web_editor.base');
var core = require('web.core');
var ajax = require('web.ajax');
var _t = core._t;

var update_mail_type = function() {
    var address = $("div[class~='address']");
    if ($("input[name='snail_mail']").is(':checked')) {
        address.removeClass('hidden');
    } else {
        address.addClass('hidden');
    }
};
$("input[name='snail_mail']").on("click", update_mail_type);
update_mail_type();

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
});