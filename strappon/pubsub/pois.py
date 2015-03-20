#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime as dt

from strappon.pubsub import serialize_date

from weblib.pubsub import Publisher


class ActivePOISExtractor(Publisher):
    def perform(self, pois):
        now = dt.utcnow()
        def predicate(p):
            return (now.date() >= p['starts'].date() and
                    now <= p['ends'])
        self.publish('pois_extracted', filter(predicate, pois))


def serialize(localized_gettext, poi):
    if poi is None:
        return None
    data = dict(**poi)
    data.update(info=localized_gettext(poi['info']))
    data.update(starts=serialize_date(poi['starts']))
    data.update(ends=serialize_date(poi['ends']))
    return data


class POISSerializer(Publisher):
    def perform(self, localized_gettext, pois):
        self.publish('pois_serialized',
                     [serialize(localized_gettext, poi) for poi in pois])
