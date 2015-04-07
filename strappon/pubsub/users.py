#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import namedtuple
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
    def perform(self, repository, acs_id, facebook_id,
                first_name, last_name, name, avatar_unresolved, avatar, email,
                locale):
        user = repository.add(acs_id, facebook_id, first_name, last_name, name,
                              avatar_unresolved, avatar, email, locale)
        self.publish('user_created', user)


class UserUpdater(Publisher):
    def perform(self, user, acs_id, facebook_id, first_name, last_name, name,
                avatar_unresolved, avatar, email, locale):
        user.acs_id = acs_id
        user.facebook_id = facebook_id
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
    if hasattr(user, 'mutual_friends'):
        data.update(mutual_friends=[dict(name=mf.name, avatar=mf.avatar)
                                    for mf in user.mutual_friends])
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
    user.mutual_friends = mutual_friends()
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


MutualFriend = namedtuple('MutualFriend', 'name avatar')


def mutual_friends():
    import random
    users = [
        MutualFriend('David H.',
                     'https://fbcdn-profile-a.akamaihd.net/hprofile-ak-xfa1/v/t1.0-1/c18.0.200.200/p200x200/10624986_1477350769217645_465727595051312050_n.jpg?oh=ab5078065ccd474c2dd6ef054092753a&oe=555A5B55&__gda__=1435179072_1829d38f3ba4962e808d6cf461a29cd7'),
        MutualFriend('Sandra S.',
                     'https://fbcdn-profile-a.akamaihd.net/hprofile-ak-xpf1/v/t1.0-1/c60.0.200.200/p200x200/10419476_1411591069121334_820946196806376594_n.jpg?oh=1bc977aa955d52a980e3a9f6fc587d7d&oe=553897E9&__gda__=1429922601_e3e22d6bb6334d47ffed67bf9489ef5c'),
        MutualFriend('Giovanni B.',
                     'https://fbcdn-profile-a.akamaihd.net/hprofile-ak-xpf1/v/t1.0-1/c13.0.200.200/p200x200/10380893_10154576263220436_7890624139659593470_n.jpg?oh=e4af87eacd56b1f8e3e6b9df4d50190e&oe=55777D39&__gda__=1438548252_b3d58731b3dd88bc8839e1516f3506c2'),
        MutualFriend('Tommaso F.',
                     'https://fbcdn-profile-a.akamaihd.net/hprofile-ak-xfp1/v/t1.0-1/p200x200/10622955_1447363295547164_4638427295998374982_n.jpg?oh=47ddb776733de2a64766afbc1f89e815&oe=554A8DD6&__gda__=1435626944_e613637c8f7fb01562442af283b0a822'),
        MutualFriend('Matteo L.',
                     'https://fbcdn-profile-a.akamaihd.net/hprofile-ak-xap1/v/t1.0-1/p200x200/10868127_10204374991667470_3572364612501862863_n.jpg?oh=03ebcdb664870b133c394de37f386bcb&oe=557F3545&__gda__=1435448976_68d834c718dd9a6c8ffd748b8878ae51'),
        MutualFriend('Serena P.',
                     'https://fbcdn-profile-a.akamaihd.net/hprofile-ak-xaf1/v/t1.0-1/p200x200/10456246_1468843330057838_7142733258662762811_n.jpg?oh=7f3d7664a8e0ddd8d6b962f12f225c4f&oe=55B735FF&__gda__=1437895988_c97db30e9e7ea0226e85f4c445056508'),
        MutualFriend('Davide M.',
                     'https://fbcdn-profile-a.akamaihd.net/hprofile-ak-xfp1/v/t1.0-1/p200x200/10552479_1473248416290481_3001336802249778574_n.jpg?oh=f4998c49cbb1cb59103d3c6a635cdfd3&oe=552AF855&__gda__=1425913923_541e369920e5f956848122376d39ee6c'),
        MutualFriend('Paola B.',
                     'https://fbcdn-profile-a.akamaihd.net/hprofile-ak-xpf1/v/t1.0-1/c0.56.200.200/p200x200/10170698_10202420088615054_8979964403504391043_n.jpg?oh=d27867fb0f0a941bdd08f73ac11b3736&oe=553BAE73&__gda__=1425896022_7375e21ffb92020e97d28c16a92e316b'),
        MutualFriend('Mercedes L.',
                     'https://fbcdn-profile-a.akamaihd.net/hprofile-ak-ash2/v/t1.0-1/c33.0.200.200/p200x200/580483_10201087598369262_1745409923_n.jpg?oh=9cdab6f2de3e9328bf90f742e27cb8a5&oe=553492F9&__gda__=1426058946_09c0f70d759f7bfc3becf5ff4ac4aee7'),
        MutualFriend('Vittoria C.',
                     'https://fbcdn-profile-a.akamaihd.net/hprofile-ak-xpf1/v/t1.0-1/p200x200/10653468_298134990371275_4908610022188667937_n.jpg?oh=e5762040b057d735900c0f9fcb8ac931&oe=554D65CB&__gda__=1432502573_1fb83adfa633fab6925a63455c955191'),
        MutualFriend('Stefania B.',
                     'https://fbcdn-profile-a.akamaihd.net/hprofile-ak-xaf1/v/t1.0-1/c0.0.200.200/p200x200/10671216_383300195159736_5370918852172017002_n.jpg?oh=34858d6cad91617dbf108ef04c30b831&oe=55395846&__gda__=1428905733_8972aa461f99a2b36c9ef1d80d0c90ac'),
        MutualFriend('Tom S.',
                     'https://fbcdn-profile-a.akamaihd.net/hprofile-ak-xpf1/v/t1.0-1/c33.0.200.200/p200x200/10256998_1404979933111128_6454708213465189421_n.jpg?oh=b07ec672e0d7645b7fd0b37f9496121d&oe=558D2255&__gda__=1435459587_a56bccc6f5cc3776d33b3a93ebdfc2d6'),
        MutualFriend('Laura C.',
                     'https://fbcdn-profile-a.akamaihd.net/hprofile-ak-xfa1/v/t1.0-1/c33.0.200.200/p200x200/1926809_1474787226134281_3779165220712858598_n.jpg?oh=65399fb70a2fe94f089779c439dc6e50&oe=552A10CE&__gda__=1430584539_5919c3b4949fbd88a8b0c87d30ea5082'),
        MutualFriend('Margerita M.',
                     'https://fbcdn-profile-a.akamaihd.net/hprofile-ak-xfp1/v/t1.0-1/p200x200/10478178_1375484966087429_4446006849314134874_n.jpg?oh=e055ae455030056465162eaf5b114a1a&oe=557CFEB1&__gda__=1437643943_b02e085de20e7cca66eb21df48edc14d'),
        MutualFriend('Francesco B.',
                     'https://fbcdn-profile-a.akamaihd.net/hprofile-ak-xfa1/v/t1.0-1/c0.0.200.200/p200x200/10660268_364398580387247_2251372498450011203_n.jpg?oh=9dea94ae4b9eebc030297bd4831400d1&oe=557F1376&__gda__=1434716574_68125d726e401bcf0855a998320f2e35'),
    ]
    number_friends = [0, 0, 0, 0, 0, 1, 1, 3, 3, 8, 8]
    return [mf for mf in random.sample(users,
                                       random.sample(number_friends, 1)[0])]
