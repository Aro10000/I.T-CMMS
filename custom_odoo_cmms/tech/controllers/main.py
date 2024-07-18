# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import odoo.http as http

from odoo.http import request
from odoo.tools.misc import get_lang


class TechController(http.Controller):

    # YTI Note: Keep id and kwargs only for retrocompatibility purpose
    @http.route('/tech/meeting/accept', type='http', auth="tech")
    def accept_meeting(self, token, id, **kwargs):
        attendee = request.env['tech.attendee'].sudo().search([
            ('access_token', '=', token),
            ('state', '!=', 'accepted')])
        attendee.do_accept()
        return self.view_meeting(token, id)

    @http.route('/tech/recurrence/accept', type='http', auth="tech")
    def accept_recurrence(self, token, id, **kwargs):
        attendee = request.env['tech.attendee'].sudo().search([
            ('access_token', '=', token),
            ('state', '!=', 'accepted')])
        if attendee:
            attendees = request.env['tech.attendee'].sudo().search([
                ('event_id', 'in', attendee.event_id.recurrence_id.tech_event_ids.ids),
                ('partner_id', '=', attendee.partner_id.id),
                ('state', '!=', 'accepted'),
            ])
            attendees.do_accept()
        return self.view_meeting(token, id)

    @http.route('/tech/meeting/decline', type='http', auth="tech")
    def decline_meeting(self, token, id, **kwargs):
        attendee = request.env['tech.attendee'].sudo().search([
            ('access_token', '=', token),
            ('state', '!=', 'declined')])
        attendee.do_decline()
        return self.view_meeting(token, id)

    @http.route('/tech/recurrence/decline', type='http', auth="tech")
    def decline_recurrence(self, token, id, **kwargs):
        attendee = request.env['tech.attendee'].sudo().search([
            ('access_token', '=', token),
            ('state', '!=', 'declined')])
        if attendee:
            attendees = request.env['tech.attendee'].sudo().search([
                ('event_id', 'in', attendee.event_id.recurrence_id.tech_event_ids.ids),
                ('partner_id', '=', attendee.partner_id.id),
                ('state', '!=', 'declined'),
            ])
            attendees.do_decline()
        return self.view_meeting(token, id)

    @http.route('/tech/meeting/view', type='http', auth="tech")
    def view_meeting(self, token, id, **kwargs):
        attendee = request.env['tech.attendee'].sudo().search([
            ('access_token', '=', token),
            ('event_id', '=', int(id))])
        if not attendee:
            return request.not_found()
        timezone = attendee.partner_id.tz
        lang = attendee.partner_id.lang or get_lang(request.env).code
        event = request.env['tech.event'].with_context(tz=timezone, lang=lang).sudo().browse(int(id))
        company = event.user_id and event.user_id.company_id or event.create_uid.company_id

        # If user is internal and logged, redirect to form view of event
        # otherwise, display the simplifyed web page with event informations
        if request.session.uid and request.env['res.users'].browse(request.session.uid).user_has_groups('base.group_user'):
            return request.redirect('/web?db=%s#id=%s&view_type=form&model=tech.event' % (request.env.cr.dbname, id))

        # NOTE : we don't use request.render() since:
        # - we need a template rendering which is not lazy, to render before cursor closing
        # - we need to display the template in the language of the user (not possible with
        #   request.render())
        response_content = request.env['ir.ui.view'].with_context(lang=lang)._render_template(
            'tech.invitation_page_anonymous', {
                'company': company,
                'event': event,
                'attendee': attendee,
            })
        return request.make_response(response_content, headers=[('Content-Type', 'text/html')])

    @http.route('/tech/meeting/join', type='http', auth="user", website=True)
    def tech_join_meeting(self, token, **kwargs):
        event = request.env['tech.event'].sudo().search([
            ('access_token', '=', token)])
        if not event:
            return request.not_found()
        event.action_join_meeting(request.env.user.partner_id.id)
        attendee = request.env['tech.attendee'].sudo().search([('partner_id', '=', request.env.user.partner_id.id), ('event_id', '=', event.id)])
        return request.redirect('/tech/meeting/view?token=%s&id=%s' % (attendee.access_token, event.id))

    # Function used, in RPC to check every 5 minutes, if notification to do for an event or not
    @http.route('/tech/notify', type='json', auth="user")
    def notify(self):
        return request.env['tech.alarm_manager'].get_next_notif()

    @http.route('/tech/notify_ack', type='json', auth="user")
    def notify_ack(self):
        return request.env['res.partner'].sudo()._set_tech_last_notif_ack()

    @http.route('/tech/join_videocall/<string:access_token>', type='http', auth='public')
    def tech_join_videocall(self, access_token):
        event = request.env['tech.event'].sudo().search([('access_token', '=', access_token)])
        if not event:
            return request.not_found()

        # if channel doesn't exist
        if not event.videocall_channel_id:
            event._create_videocall_channel()

        return request.redirect(event.videocall_channel_id.invitation_url)
