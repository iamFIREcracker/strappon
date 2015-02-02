#!/usr/bin/env python
# -*- coding: utf-8 -*-


import uuid
from datetime import datetime as dt

from weblib.db import expunged
from strappon.models import Promo
from strappon.models import UserPromo


class PromosRepository(object):

    @staticmethod
    def add(name, eligible_till, active_for, credits):
        promo = Promo(id=unicode(uuid.uuid4()),
                      name=name,
                      eligible_till=eligible_till,
                      active_for=active_for,
                      credits=credits)
        return promo

    @staticmethod
    def activate_promo(user_id, promo_id):
        return UserPromo(id=unicode(uuid.uuid4()),
                         user_id=user_id,
                         promo_id=promo_id)

    @staticmethod
    def get_promo_by_name(name):
        return get_promo_by_name(name)

    @staticmethod
    def get_user_promo_by_user_and_promo(user_id, promo_id):
        return get_user_promo_by_user_and_promo(user_id, promo_id)


def get_promo_by_name(name):
    return expunged(Promo.query.
                    filter(Promo.name == name).
                    filter(Promo.eligible_till >= dt.utcnow()).
                    first(),
                    Promo.session)


def get_user_promo_by_user_and_promo(user_id, promo_id):
    return expunged(UserPromo.query.
                    filter(UserPromo.user_id == user_id).
                    filter(UserPromo.promo_id == promo_id).
                    first(),
                    UserPromo.session)
