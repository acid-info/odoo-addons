from odoo import http
from odoo.http import route, request
from odoo.addons.mass_mailing.controllers import main

class ExtendWebsiteMassMailingApi(http.Controller):
    @route('/website_mass_mailing/subscribe2', type='json', website=True, auth='public')
    def subscribe2(self, list_id, name, value, **post):
        if not request.env['ir.http']._verify_request_recaptcha_token('website_mass_mailing_subscribe'):
            return {
                'message': _("Suspicious activity detected by Google reCaptcha."),
            }

        ContactSubscription = request.env['mailing.contact.subscription'].sudo()
        Contacts = request.env['mailing.contact'].sudo()

        subscription = ContactSubscription.search(
            [('list_id', '=', int(list_id)), (f'contact_id.email', '=', value)], limit=1)

        if subscription and not subscription.opt_out:
            return {
              'message': "Already subscribed!"
            }
        
        if not subscription:
            # inline add_to_list as we've already called half of it
            contact_id = Contacts.search([('email', '=', value)], limit=1)
            if not contact_id:
                contact_id = Contacts.create({'name': name, 'email': value})
            ContactSubscription.create({'contact_id': contact_id.id, 'list_id': int(list_id)})
        elif subscription.opt_out:
            subscription.opt_out = False
        # add email to session
        request.session[f'mass_mailing_email'] = value

        return {
          'message': "Thanks for subscribing!"
        }
