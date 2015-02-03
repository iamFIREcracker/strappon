#!/usr/bin/env python
# -*- coding: utf-8 -*-

from math import floor

from weblib.pubsub import Publisher


BASE_COST = 0.30  # € per Km per passengers


def reimbursement_for(fixed_rate, multiplier, seats, distance):
    return fixed_rate + \
        multiplier * seats * floor(1.0 + 1.2 * distance) * BASE_COST


class ReimbursementCalculator(Publisher):
    def perform(self, fixed_rate, multiplier, seats, distance):
        self.publish('reimbursement_calculated',
                     reimbursement_for(fixed_rate, multiplier, seats,
                                       distance))


def fare_for(fixed_rate, multiplier, seats, distance):
    return fixed_rate + \
        multiplier * seats * floor(1.0 + 1.2 * distance) * BASE_COST


class FareCalculator(Publisher):
    def perform(self, fixed_rate, multiplier, seats, distance):
        self.publish('fare_calculated',
                     fare_for(fixed_rate, multiplier, seats, distance))


class ReimbursementCreator(Publisher):
    def perform(self, payments_repository, drive_request_id, driver_user_id,
                credits_):
        self.publish('reimbursement_created',
                     payments_repository.add(drive_request_id,
                                             None,
                                             driver_user_id,
                                             credits_,
                                             None,
                                             None))


class FareCreator(Publisher):
    def perform(self, payments_repository, drive_request_id, passenger_user_id,
                credits_):
        self.publish('fare_created',
                     payments_repository.add(drive_request_id,
                                             passenger_user_id,
                                             None,
                                             credits_,
                                             None,
                                             None))


class PaymentForPromoCodeCreator(Publisher):
    def perform(self, payments_repository, user_id, promo_code):
        self.publish('payment_created',
                     payments_repository.add(None,
                                             None,
                                             user_id,
                                             0,
                                             promo_code.credits,
                                             promo_code.id))
