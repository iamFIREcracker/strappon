#!/usr/bin/env python
# -*- coding: utf-8 -*-

from math import pi

from weblib.pubsub import Publisher


BASE_COST = 0.30  # € per Km per passengers


def reimbursement_for(fixed_rate, multiplier, seats, distance):
    adjusted_distance = distance * 1.5
    if adjusted_distance <= pi:
        if seats == 1:
            return 1.5
        else:
            return 3
    else:
        if seats == 1:
            return 2.5
        else:
            return 5


class ReimbursementCalculator(Publisher):
    def perform(self, fixed_rate, multiplier, seats, distance):
        self.publish('reimbursement_calculated',
                     reimbursement_for(fixed_rate, multiplier, seats,
                                       distance))


def fare_for(fixed_rate, multiplier, seats, distance):
    adjusted_distance = distance * 1.5
    if adjusted_distance <= pi:
        if seats == 1:
            return 1.5
        else:
            return 3
    else:
        if seats == 1:
            return 2.5
        else:
            return 5


class FareCalculator(Publisher):
    def perform(self, fixed_rate, multiplier, seats, distance):
        self.publish('fare_calculated',
                     fare_for(fixed_rate, multiplier, seats, distance))


class ReimbursementCreator(Publisher):
    def perform(self, payments_repository, drive_request_id, driver_user_id,
                credits_):
        self.publish('payments_created',
                     [payments_repository.add(drive_request_id,
                                              None,
                                              driver_user_id,
                                              credits_,
                                              None,
                                              None)])


class FareCreator(Publisher):
    def perform(self, payments_repository, drive_request_id, passenger_user_id,
                detailed_balance, credits_):
        payments = []
        for (amount, promo_code_id) in reversed(detailed_balance):
            if credits_ > 0:
                value = min(credits_, amount)
                credits_ -= value
                real_credits = value if promo_code_id is None else 0
                bonus_credits = value if promo_code_id is not None else 0
                payments.append(payments_repository.add(drive_request_id,
                                                        passenger_user_id,
                                                        None,
                                                        real_credits,
                                                        bonus_credits,
                                                        promo_code_id))
        self.publish('payments_created', payments)


class PaymentForPromoCodeCreator(Publisher):
    def perform(self, payments_repository, user_id, promo_code):
        self.publish('payment_created',
                     payments_repository.add(None,
                                             None,
                                             user_id,
                                             0,
                                             promo_code.credits,
                                             promo_code.id))


class CreditsByUserIdGetter(Publisher):
    def perform(self, payments_repository, user_id):
        self.publish('credits_found',
                     payments_repository.detailed_balance(user_id))


class CreditsReserver(Publisher):
    def perform(self, payments_repository, detailed_balance, credits):
        for (amount, _) in detailed_balance:
            if credits > 0:
                credits -= amount
        if credits > 0:
            self.publish('credits_not_found', credits)
        else:
            self.publish('payments_created', None)


def serialize(payment):
    if payment is None:
        return None
    data = dict(id=payment.id,
                credits=payment.credits,
                bonus_credits=payment.bonus_credits,
                promo_code_id=payment.promo_code_id)
    return data


class PaymentSerializer(Publisher):
    def perform(self, payment):
        self.publish('payment_serializer', serialize(payment))
