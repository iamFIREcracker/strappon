#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uuid

from strappon.models import Base
from strappon.models import UserPosition
from weblib.db import expunged
from sqlalchemy.sql.expression import false


class PositionsRepository(object):
    @staticmethod
    def add(user_id, region, latitude, longitude):
        id = unicode(uuid.uuid4())
        position = UserPosition(id=id, user_id=user_id, region=region,
                                latitude=latitude, longitude=longitude)
        return position

    @staticmethod
    def get_all_by_user_id(user_id):
        return get_all_by_user_id(user_id)


def _get_all_by_user_id(user_id):
    return (Base.session.query(UserPosition).
            filter(UserPosition.user_id == user_id).
            filter(UserPosition.archived == false()))


def get_all_by_user_id(user_id):
    return [expunged(t, Base.session)
            for t in _get_all_by_user_id(user_id)]
