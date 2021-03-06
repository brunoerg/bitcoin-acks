from datetime import datetime
from operator import or_
from uuid import uuid4

from flask import request
from flask_login import current_user
from sqlalchemy import func
from sqlalchemy.sql.functions import coalesce

from bitcoin_acks.database import session_scope
from bitcoin_acks.logging import log
from bitcoin_acks.models import Bounties, PullRequests
from bitcoin_acks.webapp.formatters import humanize_date_formatter, \
    pr_link_formatter, payable_satoshi_formatter, invoices_formatter
from bitcoin_acks.webapp.views.authenticated_model_view import \
    AuthenticatedModelView


class BountiesPayableModelView(AuthenticatedModelView):
    def __init__(self, model, session, *args, **kwargs):
        super(BountiesPayableModelView, self).__init__(model, session, *args,
                                                    **kwargs)
        self.static_folder = 'static'
        self.endpoint = 'bounties-payable'
        self.name = 'Bounties Payable'

    form_columns = ['amount', 'pull_request']

    def get_query(self):
        return (
            self.session
                .query(self.model)
                .filter(self.model.payer_user_id == current_user.id)
        )

    def get_count_query(self):
        return (
            self.session
                .query(func.count('*'))
                .filter(self.model.payer_user_id == current_user.id)
        )

    def create_form(self, **kwargs):
        form = super().create_form()
        if 'pull_request_number' in request.args.keys():
            pull_request = self.session.query(PullRequests).filter(PullRequests.number == request.args['pull_request_number']).one()
            form.pull_request.data = pull_request
        # form.amount.data = 1000
        return form

    def on_model_change(self, form, model: Bounties, is_created: bool):
        model.id = uuid4().hex
        model.published_at = datetime.utcnow()
        model.payer_user_id = current_user.id
        model.recipient_user_id = model.pull_request.author_id

        with session_scope() as session:
            total_bounty_amount = (
                session
                    .query(coalesce(func.sum(Bounties.amount), 0))
                    .filter(Bounties.pull_request_id == model.pull_request.id)
                    .one()
            )[0]
            log.debug('total_satoshis', total_bounty_amount=total_bounty_amount)
            model.pull_request.total_bounty_amount = total_bounty_amount + model.amount

    can_create = True

    named_filter_urls = True

    column_list = [
        'pull_request.number',
        'amount',
        'published_at',
        'invoices'
    ]
    column_labels = {
        'pull_request.number': 'Pull Request',
        'amount': 'satoshis'
    }
    column_formatters = {
        'pull_request.number': pr_link_formatter,
        'published_at': humanize_date_formatter,
        'amount': payable_satoshi_formatter,
        'invoices': invoices_formatter
    }

    form_ajax_refs = {
        'pull_request': {
            'fields': ['number', 'title'],
            'page_size': 10,
            'minimum_input_length': 0,  # show suggestions, even before any user input
            'placeholder': 'Please select',
        }
    }