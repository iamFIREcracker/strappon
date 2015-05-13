#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uuid

from strappon.models import UserPosition


class PositionsRepository(object):
    @staticmethod
    def add(user_id, region, latitude, longitude):
        id = unicode(uuid.uuid4())
        position = UserPosition(id=id, user_id=user_id, region=region,
                                latitude=latitude, longitude=longitude)
        return position
