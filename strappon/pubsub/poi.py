#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime as dt

from strappon.pubsub import serialize_date

from weblib.pubsub import Publisher


class ActivePOIExtractor(Publisher):
    def perform(self, poi):
        now = dt.utcnow()
        def predicate(p):
            return (now.date() >= p['starts'].date() and
                    now <= p['ends'])
        self.publish('poi_extracted', filter(predicate, poi))


def serialize(poi):
    if poi is None:
        return None
    data = dict(**poi)
    data.update(starts=serialize_date(poi['starts']))
    data.update(ends=serialize_date(poi['ends']))
    return data


class POISerializer(Publisher):
    def perform(self, poi):
        self.publish('poi_serialized',
                     [serialize(p) for p in poi])
