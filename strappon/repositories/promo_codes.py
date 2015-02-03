#!/usr/bin/env python
# -*- coding: utf-8 -*-


import uuid
from datetime import datetime as dt

from weblib.db import expunged
from strappon.models import PromoCode
from strappon.models import UserPromoCode


class PromoCodesRepository(object):

    @staticmethod
    def add(name, eligible_till, active_for, credits):
        promo_code = PromoCode(id=unicode(uuid.uuid4()),
                               name=name,
                               eligible_till=eligible_till,
                               active_for=active_for,
                               credits=credits)
        return promo_code

    @staticmethod
    def activate_promo_code(user_id, promo_code_id):
        return UserPromoCode(id=unicode(uuid.uuid4()),
                             user_id=user_id,
                             promo_code_id=promo_code_id)

    @staticmethod
    def get_promo_code_by_name(name):
        return get_promo_code_by_name(name)

    @staticmethod
    def get_user_promo_code_by_user_and_promo_code(user_id, promo_code_id):
        return get_user_promo_code_by_user_and_promo_code(user_id,
                                                          promo_code_id)


def get_promo_code_by_name(name):
    return expunged(PromoCode.query.
                    filter(PromoCode.name == name).
                    filter(PromoCode.eligible_till >= dt.utcnow()).
                    first(),
                    PromoCode.session)


def get_user_promo_code_by_user_and_promo_code(user_id, promo_code_id):
    return expunged(UserPromoCode.query.
                    filter(UserPromoCode.user_id == user_id).
                    filter(UserPromoCode.promo_code_id == promo_code_id).
                    first(),
                    UserPromoCode.session)
