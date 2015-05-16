#!/usr/bin/env python
# -*- coding: utf-8 -*-

from weblib.pubsub import Publisher
from strappon.pubsub import distance


class ClosestRegionGetter(Publisher):
    def perform(self, served_regions, latitude, longitude):
        for region in served_regions:
            d = distance(region['center']['lat'], region['center']['lon'],
                         latitude, longitude)
            if d < region['radius']:
                self.publish('region_found', region['name'])
                return
        else:
            self.publish('region_not_found', latitude, longitude)


class PositionCreator(Publisher):
    def perform(self, positions_repository, user_id, region,
                latitude, longitude):
        position = positions_repository.add(user_id,
                                            region,
                                            latitude,
                                            longitude)
        self.publish('position_created', position)