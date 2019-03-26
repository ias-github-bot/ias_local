odoo.define('hr_attendance_import.tree_view_buttons', function (require) {
    "use strict";

    var ListController = require('web.ListController');
    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;


    ListController.include({
        renderButtons: function () {
            this._super.apply(this, arguments);
            if (!this.$buttons) {
                return;
            }
            this.$buttons.on('click', '.or_tree_view_button',
                this.open_view_wizard.bind(this));
        },

        open_view_wizard: function () {
            var action = {
                name: _t("Import Attendances"),
                type: 'ir.actions.act_window',
                res_model: 'wizard.import.attendance.xls',
                view_mode: 'form',
                view_type: 'form',
                view_id: 'hr_attendance_import.wizard_wizard_import_attendance_xls',
                views: [[false, 'form']],
                target: 'new',
                context: {},
            };
            this.do_action(action);
        },
    });
});
