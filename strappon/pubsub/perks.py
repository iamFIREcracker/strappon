#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import namedtuple

from weblib.pubsub import Publisher

from strappon.pubsub import serialize_date


EnrichedDriverEarlyBirdPerk = namedtuple('EnrichedDriverEarlyBirdPerk',
                                         'perk rides_given'.split())


class DriverPerksGetter(Publisher):
    def perform(self, repository, limit, offset):
        self.publish('perks_found',
                     repository.all_driver_perks(limit, offset))


class EligibleDriverPerksWithNameGetter(Publisher):
    def perform(self, repository, perk_name):
        self.publish('perks_found',
                     repository.eligible_driver_perks_with_name(perk_name))


class ActiveDriverPerksWithNameGetter(Publisher):
    def perform(self, repository, perk_name):
        self.publish('perks_found',
                     repository.active_driver_perks_with_name(perk_name))


class EligibleDriverPerkWithNameAndUserIdGetter(Publisher):
    def perform(self, perks_repository, name, user_id):
        self.publish('perks_found',
                     perks_repository.
                     eligible_driver_perk_with_name_and_user_id(name,
                                                                user_id))


class EligibleDriverPerksActivator(Publisher):
    def perform(self, perks_repository, perks):
        self.publish('perks_activated',
                     [perks_repository.activate_driver_perk(p.user, p.perk)
                      for p in perks])


class DriverErlyBirdPerkEnricher(Publisher):
    def perform(self, drive_requests_repository, perks):
        self.publish('perks_enriched',
                     [EnrichedDriverEarlyBirdPerk(p,
                                                  drive_requests_repository.
                                                  rides_given(p.user_id,
                                                              p.created,
                                                              p.valid_until))
                      for p in perks])


class PassengerPerksGetter(Publisher):
    def perform(self, repository, limit, offset):
        self.publish('perks_found',
                     repository.all_passenger_perks(limit, offset))


def _serialize_perk(gettext, perk):
    if perk is None:
        return None
    return dict(name=gettext("perk_name_%s" % perk.name))


def _serialize_eligible_perk(gettext, perk):
    if perk is None:
        return None
    data = _serialize_perk(gettext, perk.perk)
    data.update(valid_until=serialize_date(perk.valid_until))
    data.update(description=gettext("perk_eligible_description_%s" %
                                    perk.perk.name) %
                dict(valid_until_year=perk.valid_until.year,
                     valid_until_month=perk.valid_until.month,
                     valid_until_day=perk.valid_until.day))
    return data


def _serialize_active_perk(gettext, perk):
    if perk is None:
        return None
    data = _serialize_perk(gettext, perk.perk)
    data.update(valid_until=serialize_date(perk.valid_until))
    data.update(description=gettext("perk_active_description_%s" %
                                    perk.perk.name) %
                dict(valid_until_year=perk.valid_until.year,
                     valid_until_month=perk.valid_until.month,
                     valid_until_day=perk.valid_until.day))
    return data


def serialize_eligible_driver_perk(gettext, driver_perk):
    return _serialize_eligible_perk(gettext, driver_perk)


def serialize_active_driver_perk(gettext, driver_perk):
    return _serialize_active_perk(gettext, driver_perk)


def serialize_eligible_passenger_perk(gettext, passenger_perk):
    return _serialize_eligible_perk(gettext, passenger_perk)


def serialize_active_passenger_perk(gettext, passenger_perk):
    return _serialize_active_perk(gettext, passenger_perk)


class ActiveDriverPerksGetter(Publisher):
    def perform(self, perks_repository, user_id):
        self.publish('active_driver_perks_found',
                     perks_repository.active_driver_perks(user_id))


class ActivePassengerPerksGetter(Publisher):
    def perform(self, perks_repository, user_id):
        self.publish('active_passenger_perks_found',
                     perks_repository.active_passenger_perks(user_id))


class DefaultPerksCreator(Publisher):
    def perform(self, perks_repository, user,
                eligible_driver_perks, active_driver_perks,
                eligible_passenger_perks, active_passenger_perks):
        perks = []
        for p in eligible_driver_perks:
            perks.append(perks_repository.eligiblify_driver_perk(user, p))
        for p in active_driver_perks:
            perks.append(perks_repository.activate_driver_perk(user, p))
        for p in eligible_passenger_perks:
            perks.append(perks_repository.eligiblify_passenger_perk(user, p))
        for p in active_passenger_perks:
            perks.append(perks_repository.activate_passenger_perk(user, p))
        self.publish('perks_created', perks)
