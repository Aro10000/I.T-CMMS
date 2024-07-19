/** @odoo-module **/

import tour from 'web_tour.tour';

const tecSharingSteps = [...tour.stepUtils.goToAppSteps("tec.menu_main_pm", 'Go to the Tec App.'), {
    trigger: '.oe_kanban_global_click :contains("Tec Sharing") button.o_dropdown_kanban',
    content: 'Open the tec dropdown.'
}, {
    trigger: '.o_kanban_record:contains("Tec Sharing") .dropdown-menu a:contains("Share")',
    content: 'Start editing the tec.',
}, {
    trigger: 'div.o_field_radio[name="access_mode"] div.o_radio_item > input[data-value="edit"]',
    content: 'Select "Edit" as Access mode in the "Share Tec" wizard.',
}, {
    trigger: '.o_field_many2many_tags_email[name=partner_ids]',
    content: 'Select the user portal as collaborator to the "Tec Sharing" tec.',
    run: function (actions) {
        actions.text('Georges', this.$anchor.find('input'));
    },
}, {
    trigger: '.ui-autocomplete a.dropdown-item:contains("Georges")',
    in_modal: false,
}, {
    trigger: 'footer > button[name="action_send_mail"]',
    content: 'Confirm the tec sharing with this portal user.',
}, {
    trigger: '.o_web_client',
    content: 'Go to tec portal view to select the "Tec Sharing" tec',
    run: function () {
        window.location.href = window.location.origin + '/my/tecs';
    },
}, {
    id: 'tec_sharing_feature',
    trigger: 'table > tbody > tr a:has(span:contains(Tec Sharing))',
    content: 'Select "Tec Sharing" tec to go to tec sharing feature for this tec.',
}, {
    trigger: '.o_tec_sharing',
    content: 'Wait the tec sharing feature be loaded',
    run: function () {},
}, {
    trigger: 'button.o-kanban-button-new',
    content: 'Click "Create" button',
    run: 'click',
}, {
    trigger: '.o_kanban_quick_create .o_field_widget[name="name"] input',
    content: 'Create Task',
    run: 'text Test Create Task',
}, {
    trigger: '.o_kanban_quick_create .o_kanban_edit',
    content: 'Go to the form view of this new task',
}, {
    trigger: 'div[name="stage_id"] div.o_statusbar_status button[aria-checked="false"]:contains(Done)',
    content: 'Change the stage of the task.',
}, {
    trigger: '.o_portal_chatter_composer_input .o_portal_chatter_composer_body textarea',
    content: 'Write a message in the chatter of the task',
    run: 'text I create a new task for testing purpose.',
}, {
    trigger: '.o_portal_chatter_composer_input .o_portal_chatter_composer_body button[name="send_message"]',
    content: 'Send the message',
}, {
    trigger: 'ol.breadcrumb > li.o_back_button > a:contains(Tec Sharing)',
    content: 'Go back to the kanban view',
}, {
    trigger: '.o_filter_menu > button',
    content: 'click on filter menu in the search view',
}, {
    trigger: '.o_filter_menu > .dropdown-menu > .dropdown-item:first-child',
    content: 'click on the first item in the filter menu',
}, {
    trigger: '.o_group_by_menu > button',
    content: 'click on group by menu in the search view',
}, {
    trigger: '.o_group_by_menu > .dropdown-menu > .dropdown-item:first-child',
    content: 'click on the first item in the group by menu',
}, {
    trigger: '.o_favorite_menu > button',
    content: 'click on the favorite menu in the search view',
}, {
    trigger: '.o_favorite_menu .o_add_favorite > button',
    content: 'click to "save current search" button in favorite menu',
}, {
    trigger: '.o_filter_menu > button',
    content: 'click on filter menu in the search view',
}, {
    trigger: '.o_filter_menu > .dropdown-menu > .dropdown-item:first-child',
    content: 'click on the first item in the filter menu',
}, {
    trigger: '.o_group_by_menu > button',
    content: 'click on group by menu in the search view',
}, {
    trigger: '.o_group_by_menu > .dropdown-menu > .dropdown-item:first-child',
    content: 'click on the first item in the group by menu',
}, {
    trigger: '.o_favorite_menu > button',
    content: 'click on the favorite menu in the search view',
}, {
    trigger: '.o_favorite_menu .o_add_favorite > button',
    content: 'click to "save current search" button in favorite menu',
}, {
    trigger: 'button.o_switch_view.o_list',
    content: 'Go to the list view',
}];

tour.register('tec_sharing_tour', {
    test: true,
    url: '/web',
}, tecSharingSteps);

// The begining of the tec sharing feature
const tecSharingStepIndex = tecSharingSteps.findIndex(s => s.id && s.id === 'tec_sharing_feature');
tour.register('portal_tec_sharing_tour', {
    test: true,
    url: '/my/tecs',
}, tecSharingSteps.slice(tecSharingStepIndex, tecSharingSteps.length));
