#!/usr/bin/env python

from strappon.pubsub import Publisher


class PromoCodeWithNameGetter(Publisher):
    def perform(self, repository, name):
        promo_code = repository.get_promo_code_by_name(name)
        if promo_code is None:
            self.publish('promo_code_not_found', name)
        else:
            self.publish('promo_code_found', promo_code)


class UserPromoCodeWithUserIdAndPromoCodeIdGetter(Publisher):
    def perform(self, repository, user_id, promo_code_id):
        user_promo_code = repository.\
            get_user_promo_code_by_user_and_promo_code(user_id, promo_code_id)
        if user_promo_code is None:
            self.publish('user_promo_code_not_found', user_id, promo_code_id)
        else:
            self.publish('user_promo_code_found', user_promo_code)


class PromoCodeActivator(Publisher):
    def perform(self, repository, user_id, promo_code_id):
        self.publish('user_promo_code_activated',
                     repository.activate_promo_code(user_id, promo_code_id))


class PromoCodeSerializer(Publisher):
    def perform(self, promo_code):
        self.publish('promo_code_serialized', dict(name=promo_code.name,
                                              active_for=promo_code.active_for,
                                              credits=promo_code.credits))
