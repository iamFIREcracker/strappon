#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uuid

from strappon.models import Base
from strappon.models import Token
from weblib.db import expunged


class TokensRepository(object):
    @staticmethod
    def add(user_id):
        id = unicode(uuid.uuid4())
        token = Token(id=id, user_id=user_id)
        return token

    @staticmethod
    def get_all_by_user_id(user_id):
        return get_all_by_user_id(user_id)


def _get_all_by_user_id(user_id):
    return (Base.session.query(Token).
            filter(Token.user_id == user_id))


def get_all_by_user_id(user_id):
    return [expunged(t, Base.session)
            for t in _get_all_by_user_id(user_id)]
