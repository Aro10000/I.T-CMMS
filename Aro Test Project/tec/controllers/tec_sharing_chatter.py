# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from werkzeug.exceptions import Forbidden

from odoo.http import request, route

from odoo.addons.portal.controllers.mail import PortalChatter
from .portal import TecCustomerPortal


class TecSharingChatter(PortalChatter):
    def _check_tec_access_and_get_token(self, tec_id, res_model, res_id, token):
        """ Check if the chatter in tec sharing can be accessed

            If the portal user is in the tec sharing, then we do not have the access token of the task
            but we can have the one of the tec (if the user accessed to the tec sharing views via the shared link).
            So, we need to check if the chatter is for a task and if the res_id is a task
            in the tec shared. Then, if we had the tec token and this one is the one in the tec
            then we return the token of the task to continue the portal chatter process.
            If we do not have any token, then we need to check if the portal user is a follower of the tec shared.
            If it is the case, then we give the access token of the task.
        """
        tec_sudo = TecCustomerPortal._document_check_access(self, 'tec.tec', tec_id, token)
        can_access = tec_sudo and res_model == 'tec.task' and tec_sudo.with_user(request.env.user)._check_tec_sharing_access()
        task = None
        if can_access:
            task = request.env['tec.task'].sudo().search([('id', '=', res_id), ('tec_id', '=', tec_sudo.id)])
        if not can_access or not task:
            raise Forbidden()
        return task[task._mail_post_token_field]

    # ============================================================ #
    # Note concerning the methods portal_chatter_(init/post/fetch)
    # ============================================================ #
    #
    # When the tec is shared to a portal user with the edit rights,
    # he has the read/write access to the related tasks. So it could be
    # possible to call directly the message_post method on a task.
    #
    # This change is considered as safe, as we only willingly expose
    # records, for some assumed fields only, and this feature is
    # optional and opt-in. (like the public employee model for example).
    # It doesn't allow portal users to access other models, like
    # a timesheet or an invoice.
    #
    # It could seem odd to use those routes, and converting the tec
    # access token into the task access token, as the user has actually
    # access to the records.
    #
    # However, it has been decided that it was the less hacky way to
    # achieve this, as:
    #
    # - We're reusing the existing routes, that convert all the data
    #   into valid arguments for the methods we use (message_post, ...).
    #   That way, we don't have to reinvent the wheel, duplicating code
    #   from mail/portal that surely will lead too desynchronization
    #   and inconsistencies over the time.
    #
    # - We don't define new routes, to do the exact same things than portal,
    #   considering that the portal user can use message_post for example
    #   because he has access to the record.
    #   Let's suppose that we remove this in a future development, those
    #   new routes won't be valid anymore.
    #
    # - We could have reused the mail widgets, as we already reuse the
    #   form/list/kanban views, etc. However, we only want to display
    #   the messages and allow to post. We don't need the next activities
    #   the followers system, etc. This required to override most of the
    #   mail.thread basic methods, without being sure that this would
    #   work with other installed applications or customizations

    @route()
    def portal_chatter_init(self, res_model, res_id, domain=False, limit=False, **kwargs):
        tec_sharing_id = kwargs.get('tec_sharing_id')
        if tec_sharing_id:
            # if there is a token in `kwargs` then it should be the access_token of the tec shared
            token = self._check_tec_access_and_get_token(tec_sharing_id, res_model, res_id, kwargs.get('token'))
            if token:
                del kwargs['tec_sharing_id']
                kwargs['token'] = token
        return super().portal_chatter_init(res_model, res_id, domain=domain, limit=limit, **kwargs)

    @route()
    def portal_chatter_post(self, res_model, res_id, message, attachment_ids=None, attachment_tokens=None, **kw):
        tec_sharing_id = kw.get('tec_sharing_id')
        if tec_sharing_id:
            token = self._check_tec_access_and_get_token(tec_sharing_id, res_model, res_id, kw.get('token'))
            if token:
                del kw['tec_sharing_id']
                kw['token'] = token
        return super().portal_chatter_post(res_model, res_id, message, attachment_ids=attachment_ids, attachment_tokens=attachment_tokens, **kw)

    @route()
    def portal_message_fetch(self, res_model, res_id, domain=False, limit=10, offset=0, **kw):
        tec_sharing_id = kw.get('tec_sharing_id')
        if tec_sharing_id:
            token = self._check_tec_access_and_get_token(tec_sharing_id, res_model, res_id, kw.get('token'))
            if token is not None:
                kw['token'] = token # Update token (either string which contains token value or False)
        return super().portal_message_fetch(res_model, res_id, domain=domain, limit=limit, offset=offset, **kw)
