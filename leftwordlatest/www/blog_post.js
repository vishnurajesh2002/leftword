frappe.ui.form.on('Blog Post', {
    custom_show_in_dashboard: function(frm) {
        if (frm.doc.custom_show_in_dashboard) {
            frappe.call({
                method: "frappe.db.count",
                args: {
                    doctype: "Blog Post",
                    filters: {
                        custom_show_in_dashboard: 1
                    }
                },
                callback: function(r) {
                    if (r.message >= 2) {
                        frappe.msgprint({
                            title: __('Alert'),
                            indicator: 'red',
                            message: __('Only 2 blogs can be shown in the dashboard. Please uncheck this option for other blogs.')
                        });
                        frm.set_value("custom_show_in_dashboard", 0); 
                    }
                }
            });
        }
    }
});
