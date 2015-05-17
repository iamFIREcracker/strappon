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


class PositionsByUserIdGetter(Publisher):
    def perform(self, repository, user_id):
        self.publish('positions_found', repository.get_all_by_user_id(user_id))


class MultiplePositionsArchiver(Publisher):
    def perform(self, positions):
        def archive(p):
            p.archived = True
            return p
        self.publish('positions_archived', [archive(p) for p in positions])


class PositionCreator(Publisher):
    def perform(self, positions_repository, user_id, region,
                latitude, longitude):
        position = positions_repository.add(user_id,
                                            region,
                                            latitude,
                                            longitude)
        self.publish('position_created', position)
