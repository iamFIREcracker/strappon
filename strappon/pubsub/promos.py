#!/usr/bin/env python

from strappon.pubsub import Publisher


class PromoWithNameGetter(Publisher):
    def perform(self, repository, name):
        promo = repository.get_promo_by_name(name)
        if promo is None:
            self.publish('promo_not_found', name)
        else:
            self.publish('promo_found', promo)


class UserPromoWithUserIdAndPromoIdGetter(Publisher):
    def perform(self, repository, user_id, promo_id):
        user_promo = repository.\
            get_user_promo_by_user_and_promo(user_id, promo_id)
        if user_promo is None:
            self.publish('user_promo_not_found', user_id, promo_id)
        else:
            self.publish('user_promo_found', user_promo)


class PromoActivator(Publisher):
    def perform(self, repository, user_id, promo_id):
        self.publish('user_promo_activated',
                     repository.activate_promo(user_id, promo_id))
