#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uuid

from strappon.models import Token
from strappon.models import User
from strappon.repositories.tokens import TokensRepository
from weblib.db import expunged
from weblib.db import joinedload


class UsersRepository(object):
    @staticmethod
    def get(id):
        return expunged(User.query.options(joinedload('active_driver'),
                                           joinedload('active_passenger')).\
                        filter(User.deleted == False).\
                        filter(User.id == id).first(),
                        User.session)

    @staticmethod
    def add(acs_id, facebook_id, first_name, last_name, name,
            avatar_unresolved, avatar, email, locale):
        id = unicode(uuid.uuid4())
        user = User(id=id, acs_id=acs_id, facebook_id=facebook_id,
                    first_name=first_name, last_name=last_name, name=name,
                    avatar_unresolved=avatar_unresolved, avatar=avatar,
                    email=email, locale=locale)
        return user

    @staticmethod
    def refresh_token(user_id):
        return TokensRepository.add(user_id)

    @staticmethod
    def authorized_by(token):
        return expunged(User.query.options(joinedload('active_driver'),
                                           joinedload('active_passenger')).\
                        filter(Token.id == token).\
                        filter(User.id == Token.user_id).\
                        filter(User.deleted == False).\
                        first(),
                        User.session)

    @staticmethod
    def with_facebook_id(facebook_id):
        return expunged(User.query.\
                                filter(User.facebook_id == facebook_id).\
                                filter(User.deleted == False).first(),
                        User.session)

    @staticmethod
    def with_acs_id(acs_id):
        return expunged(User.query.\
                                filter(User.acs_id == acs_id).\
                                filter(User.deleted == False).first(),
                        User.session)
