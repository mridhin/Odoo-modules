odoo.define('awb_pos_service_charge.ProductsWidget', function (require) {
    'use strict';

    const { _t } = require('web.core');
    const ProductsWidget = require('point_of_sale.ProductsWidget');
    const Registries = require('point_of_sale.Registries');

    const ServiceProductsWidget = (ProductsWidget) =>
        class extends ProductsWidget {
        
            get productsToDisplay() {
                const list = super.productsToDisplay;
                if (list.length > 0) {
                	return list.filter(e => e.id != this.env.pos.config.service_product_id[0]);
               	
                }
                return list;
            }

        };

    Registries.Component.extend(ProductsWidget, ServiceProductsWidget);

    return ProductsWidget;
});
