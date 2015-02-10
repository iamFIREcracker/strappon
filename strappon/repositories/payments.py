#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uuid
from math import fsum
from itertools import groupby

from sqlalchemy import or_
from strappon.models import Base
from strappon.models import Payment


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
    def detailed_balance(user_id):
        return detailed_balance(user_id)

    @staticmethod
    def balance(user_id):
        return balance(user_id)

    @staticmethod
    def bonus_balance(user_id):
        return bonus_balance(user_id)


def signed_credits(payment):
    credits = (payment.credits
               if payment.promo_code_id is None
               else payment.bonus_credits)
    credits = credits if payment.payee_user_id is not None else -credits
    return credits


def detailed_balance(user_id):
    query = list(Base.session.query(Payment).
                 filter(or_(Payment.payee_user_id == user_id,
                            Payment.payer_user_id == user_id)).
                 order_by(Payment.promo_code_id))
    return [(fsum(map(signed_credits, g)), k)
            for k, g in groupby(query, lambda p: p.promo_code_id)]


def balance(user_id):
    return fsum(map(lambda (credits, promo): credits,
                    filter(lambda (credits, promo): promo is None,
                           detailed_balance(user_id))))


def bonus_balance(user_id):
    return fsum(map(lambda (credits, promo): credits,
                    filter(lambda (credits, promo): promo is not None,
                           detailed_balance(user_id))))
