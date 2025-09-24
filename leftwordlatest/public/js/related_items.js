frappe.ui.form.on('Related Items', {
    onload: function (frm) {
        frm.fields_dict['items'].grid.get_field('item_code').get_query = function () {
            return {
                filters: {
                    has_variants: 0
                }
            };
        };
    }
});
