#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uuid

from strappon.models import Base
from strappon.models import Payment
from weblib.db import func


class PaymentsRepository(object):
    @staticmethod
    def add(drive_request_id, payer_user_id, payee_user_id, credits,
            bonus_credits, promo_code_id):
        return Payment(id=unicode(uuid.uuid4()),
                       drive_request_id=drive_request_id,
                       payer_user_id=payer_user_id,
                       payee_user_id=payee_user_id,
                       credits=credits,
                       bonus_credits=bonus_credits,
                       promo_code_id=promo_code_id)

    @staticmethod
    def balance(user_id):
        return PaymentsRepository.income(user_id) -\
            PaymentsRepository.outcome(user_id)

    @staticmethod
    def income(user_id):
        return Base.session.query(func.coalesce(func.sum(Payment.credits),
                                                0.0)).\
            filter(Payment.payee_user_id == user_id).first()[0]

    @staticmethod
    def outcome(user_id):
        return Base.session.query(func.coalesce(func.sum(Payment.credits),
                                                0.0)).\
            filter(Payment.payer_user_id == user_id).first()[0]

    @staticmethod
    def bonus_balance(user_id):
        return PaymentsRepository.bonus_income(user_id) -\
            PaymentsRepository.bonus_outcome(user_id)

    @staticmethod
    def bonus_income(user_id):
        return Base.session.\
            query(func.coalesce(func.sum(Payment.bonus_credits), 0.0)).\
            filter(Payment.payee_user_id == user_id).first()[0]

    @staticmethod
    def bonus_outcome(user_id):
        return Base.session.\
            query(func.coalesce(func.sum(Payment.bonus_credits), 0.0)).\
            filter(Payment.payer_user_id == user_id).first()[0]
