#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import partial

from weblib.pubsub import Publisher


class UserWithIdGetter(Publisher):
    def perform(self, repository, user_id):
        """Get the user identified by ``user_id``.

        If such user exists, a 'user_found' message is published containing the
        user details;  on the other hand, if no user exists with the specified
        ID, a 'user_not_found' message will be published
        """
        user = repository.get(user_id)
        if user is None:
            self.publish('user_not_found', user_id)
        else:
            self.publish('user_found', user)


class UserWithFacebookIdGetter(Publisher):
    def perform(self, repository, facebook_id):
        user = repository.with_facebook_id(facebook_id)
        if user is None:
            self.publish('user_not_found', facebook_id)
        else:
            self.publish('user_found', user)


class UserWithAcsIdGetter(Publisher):
    def perform(self, repository, acs_id):
        user = repository.with_acs_id(acs_id)
        if user is None:
            self.publish('user_not_found', acs_id)
        else:
            self.publish('user_found', user)


class AccountRefresher(Publisher):
    def perform(self, repository, userid, externalid, accounttype):
        """Refreshes the user external account.

        When done, a 'account_refreshed' message will be published toghether
        with the refreshed record.
        """
        account = repository.refresh_account(userid, externalid, accounttype)
        self.publish('account_refreshed', account)


class TokenRefresher(Publisher):
    def perform(self, repository, userid):
        """Refreshes the token associated with user identified by ``userid``.

        When done, a 'token_refreshed' message will be published toghether
        with the refreshed record.
        """
        token = repository.refresh_token(userid)
        self.publish('token_refreshed', token)


class TokenSerializer(Publisher):
    def perform(self, token):
        """Convert the given token into a serializable dictionary.

        At the end of the operation the method will emit a
        'token_serialized' message containing the serialized object (i.e.
        token dictionary).
        """
        self.publish('token_serialized', dict(id=token.id,
                                              user_id=token.user_id))


class UserCreator(Publisher):
    def perform(self, repository, acs_id, facebook_id, facebook_token,
                first_name, last_name, name, avatar_unresolved, avatar, email,
                locale):
        user = repository.add(acs_id, facebook_id, facebook_token,
                              first_name, last_name, name,
                              avatar_unresolved, avatar, email, locale)
        self.publish('user_created', user)


class UserUpdater(Publisher):
    def perform(self, user, acs_id, facebook_id, facebook_token,
                first_name, last_name, name,
                avatar_unresolved, avatar, email, locale):
        user.acs_id = acs_id
        user.facebook_id = facebook_id
        user.facebook_token = facebook_token
        user.first_name = first_name
        user.last_name = last_name
        user.name = name
        user.avatar_unresolved = avatar_unresolved
        user.avatar = avatar
        user.email = email
        user.locale = locale
        self.publish('user_updated', user)


def serialize(user):
    if user is None:
        return None
    data = dict(id=user.id, name=user.name, avatar=user.avatar,
                locale=user.locale)
    if hasattr(user, 'stars'):
        data.update(stars=user.stars)
    if hasattr(user, 'received_rates'):
        data.update(received_rates=user.received_rates)
    return data


class UserSerializer(Publisher):
    def perform(self, user):
        self.publish('user_serialized', serialize(user))


def serialize_private(gettext, user):
    from strappon.pubsub.perks import serialize_eligible_driver_perk
    from strappon.pubsub.perks import serialize_active_driver_perk
    from strappon.pubsub.perks import serialize_eligible_passenger_perk
    from strappon.pubsub.perks import serialize_active_passenger_perk

    localized_gettext = partial(gettext, lang=user.locale)
    data = serialize(user)
    if hasattr(user, 'rides_driver'):
        data.update(rides_driver=user.rides_driver,
                    rides_given=user.rides_driver)
    if hasattr(user, 'rides_passenger'):
        data.update(rides_passenger=user.rides_passenger)
    if hasattr(user, 'distance_driver'):
        data.update(distance_driver=user.distance_driver,
                    distance_driven=user.distance_driver)
    if hasattr(user, 'distance_passenger'):
        data.update(distance_passenger=user.distance_passenger)
    if hasattr(user, 'eligible_driver_perks'):
        data.update(eligible_driver_perks=[
            serialize_eligible_driver_perk(localized_gettext, p)
            for p in user.eligible_driver_perks])
    if hasattr(user, 'active_driver_perks'):
        data.update(active_driver_perks=[
            serialize_active_driver_perk(localized_gettext, p)
            for p in user.active_driver_perks])
    if hasattr(user, 'eligible_passenger_perks'):
        data.update(eligible_passenger_perks=[
            serialize_eligible_passenger_perk(localized_gettext, p)
            for p in user.eligible_passenger_perks])
    if hasattr(user, 'active_passenger_perks'):
        data.update(active_passenger_perks=[
            serialize_active_passenger_perk(localized_gettext, p)
            for p in user.active_passenger_perks])
    if hasattr(user, 'balance'):
        data.update(balance=user.balance)
    if hasattr(user, 'bonus_balance'):
        data.update(bonus_balance=user.bonus_balance)
    return data


class UserSerializerPrivate(Publisher):
    def perform(self, gettext, user):
        self.publish('user_serialized', serialize_private(gettext, user))


def enrich_common(rates_repository, user):
    user.stars = rates_repository.avg_stars(user.id)
    user.received_rates = rates_repository.received_rates(user.id)
    return user


def enrich(rates_repository, user):
    user = enrich_common(rates_repository, user)
    return user


def _enrich(rates_repository, user):
    return enrich(rates_repository, user)


class UserEnricher(Publisher):
    def perform(self, rates_repository, user):
        self.publish('user_enriched', _enrich(rates_repository, user))


def enrich_private(rates_repository, drive_requests_repository,
                   perks_repository, payments_repository, user):
    user = enrich_common(rates_repository, user)
    user.rides_driver = drive_requests_repository.rides_driver(user.id)
    user.rides_passenger = drive_requests_repository.rides_passenger(user.id)
    user.distance_driver = drive_requests_repository.distance_driver(user.id)
    user.distance_passenger = \
        drive_requests_repository.distance_passenger(user.id)
    user.eligible_driver_perks = perks_repository.\
        eligible_driver_perks(user.id)
    user.active_driver_perks = perks_repository.\
        active_driver_perks_without_standard_one(user.id)
    user.eligible_passenger_perks = perks_repository.\
        eligible_passenger_perks(user.id)
    user.active_passenger_perks = perks_repository.\
        active_passenger_perks_without_standard_one(user.id)
    user.balance = payments_repository.balance(user.id)
    user.bonus_balance = payments_repository.bonus_balance(user.id)
    return user


def _enrich_private(rates_repository, drive_requests_repository,
                    perks_repository, payments_repository, user):
    return enrich_private(rates_repository, drive_requests_repository,
                          perks_repository, payments_repository, user)


class UserEnricherPrivate(Publisher):
    def perform(self, rates_repository, drive_requests_repository,
                perks_repository, payments_repository, user):
        self.publish('user_enriched',
                     _enrich_private(rates_repository,
                                     drive_requests_repository,
                                     perks_repository,
                                     payments_repository,
                                     user))


class UsersACSUserIdExtractor(Publisher):
    def perform(self, users):
        self.publish('acs_user_ids_extracted',
                     filter(None, [u.acs_id for u in users]))


class UserRegionExtractor(Publisher):
    def perform(self, user):
        if user.position is None:
            self.publish('region_not_found')
        else:
            self.publish('region_found', user.position.region)
