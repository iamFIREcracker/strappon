#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uuid

from strappon.models import Token
from strappon.models import User
from strappon.repositories.tokens import TokensRepository
from sqlalchemy.orm import aliased
from weblib.db import and_
from weblib.db import exists
from weblib.db import expunged
from weblib.db import joinedload
from weblib.db import joinedload_all


class UsersRepository(object):
    @staticmethod
    def get(id):
        return expunged(User.query.options(joinedload('active_driver'),
                                           joinedload('active_passenger')).\
                        filter(User.deleted == False).\
                        filter(User.id == id).first(),
                        User.session)

    @staticmethod
    def add(acs_id, facebook_id, facebook_token, first_name, last_name, name,
            avatar_unresolved, avatar, email, locale):
        id = unicode(uuid.uuid4())
        user = User(id=id, acs_id=acs_id, facebook_id=facebook_id,
                    facebook_token=facebook_token,
                    first_name=first_name, last_name=last_name, name=name,
                    avatar_unresolved=avatar_unresolved, avatar=avatar,
                    email=email, locale=locale)
        return user

    @staticmethod
    def refresh_token(user_id):
        return TokensRepository.add(user_id)

    @staticmethod
    def authorized_by(token_id):
        return authorized_by(token_id)

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


def authorized_by(token_id):
    Token2 = aliased(Token)
    token = (Token.query.options(joinedload_all('user.active_driver'),
                                 joinedload_all('user.active_passenger'),
                                 joinedload_all('user.position')).
             filter(Token.id == token_id).
             filter(~exists().where(
                 and_(Token2.user_id == Token.user_id,
                      Token2.created > Token.created))).
             first())
    if token is None or token.id != token_id:
        return None
    return expunged(token.user, Token.session)
