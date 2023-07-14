odoo.define('awb_pos_service_charge.ServicechargeButton', function(require) {
'use strict';
   const { Gui } = require('point_of_sale.Gui');
   const PosComponent = require('point_of_sale.PosComponent');
   const { posbus } = require('point_of_sale.utils');
   const ProductScreen = require('point_of_sale.ProductScreen');
   const { useListener } = require('web.custom_hooks');
   const Registries = require('point_of_sale.Registries');
   const PaymentScreen = require('point_of_sale.PaymentScreen');

   class ServicechargeButton extends PosComponent {
        constructor() {
        	super(...arguments);
        }
        //Generate popup
      servicecharge_popup() {
         var core = require('web.core');
         var _t = core._t;
         Gui.showPopup("ServicechargePopup", {
            title : _t("Service Charge"),
            confirmText: _t("Exit")
         });
      }

   }

   ServicechargeButton.template = 'ServicechargeButton';
   ProductScreen.addControlButton({
        component: ServicechargeButton,
        condition: function() {
        return this.env.pos;
        },

   });

Registries.Component.add(ServicechargeButton);
   return ServicechargeButton;
});