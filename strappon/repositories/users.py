#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uuid

from strappon.models import Base
from strappon.models import Token
from strappon.models import User
from sqlalchemy.sql.expression import false
from weblib.db import expunged
from weblib.db import contains_eager
from weblib.db import joinedload


class UsersRepository(object):
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
    def get(user_id):
        return get(user_id)

    @staticmethod
    def with_facebook_id(facebook_id):
        return with_facebook_id(facebook_id)

    @staticmethod
    def with_acs_id(acs_id):
        return with_acs_id(acs_id)

    @staticmethod
    def authorized_by(token_id):
        return authorized_by(token_id)


def _get(user_id):
    return (User.query.options(joinedload('active_driver'),
                               joinedload('active_passenger')).
            filter(User.id == user_id).
            filter(User.deleted == false()))


def get(user_id):
    return expunged(_get(user_id).first(), User.session)


def _with_facebook_id(facebook_id):
    return (User.query.
            filter(User.facebook_id == facebook_id).
            filter(User.deleted == false()))


def with_facebook_id(facebook_id):
    return expunged(_with_facebook_id(facebook_id).first(), User.session)


def _with_acs_id(acs_id):
    return (User.query.
            filter(User.acs_id == acs_id).
            filter(User.deleted == false()))


def with_acs_id(acs_id):
    return expunged(_with_acs_id(acs_id).first(), User.session)


def _authorized_by(token_id):
    return (Base.session.query(User).
            options(contains_eager(User.active_driver),
                    contains_eager(User.active_passenger),
                    contains_eager(User.position)).
            select_from(User).
            outerjoin(User.active_driver).
            outerjoin(User.active_passenger).
            outerjoin(User.position).
            join(User.token).
            filter(Token.id == token_id))


def authorized_by(token_id):
    return expunged(_authorized_by(token_id).first(), Base.session)
