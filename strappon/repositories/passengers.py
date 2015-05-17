#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uuid
from datetime import datetime
from datetime import timedelta

from sqlalchemy.sql.expression import true
from sqlalchemy.sql.expression import false
from sqlalchemy.sql.expression import null
from strappon.models import Base
from strappon.models import Passenger
from strappon.models import UserPosition
from strappon.models import User
from weblib.db import and_
from weblib.db import contains_eager
from weblib.db import or_
from weblib.db import expunged
from weblib.db import joinedload


class PassengersRepository(object):
    @staticmethod
    def get(id):
        return expunged(Passenger.query.options(joinedload('user')).\
                                filter(User.deleted == False).\
                                filter(Passenger.id == id).\
                                first(),
                        Passenger.session)

    @staticmethod
    def get_active_by_id(id):
        return get_active_by_id(id)

    @staticmethod
    def copy(other):
        passenger = \
            Passenger(id=other.id,
                      user_id=other.user_id,
                      origin=other.origin,
                      origin_latitude=other.origin_latitude,
                      origin_longitude=other.origin_longitude,
                      destination=other.destination,
                      destination_latitude=other.destination_latitude,
                      destination_longitude=other.destination_longitude,
                      distance=other.distance,
                      seats=other.seats,
                      pickup_time_new=other.pickup_time_new,
                      matched=other.matched,
                      active=other.active)
        return passenger

    @staticmethod
    def get_all_unmatched():
        return get_all_unmatched()

    @staticmethod
    def get_all_unmatched_by_region(region):
        return get_all_unmatched_by_region(region)

    @staticmethod
    def get_all_expired(expire_after):
        return get_all_expired(expire_after)

    @staticmethod
    def get_all_active():
        return get_all_active()

    @staticmethod
    def add(user_id, origin, origin_latitude, origin_longitude,
            destination, destination_latitude, destination_longitude, distance,
            seats, pickup_time_new):
        id = unicode(uuid.uuid4())
        passenger = Passenger(id=id,
                              user_id=user_id,
                              origin=origin,
                              origin_latitude=origin_latitude,
                              origin_longitude=origin_longitude,
                              destination=destination,
                              destination_latitude=destination_latitude,
                              destination_longitude=destination_longitude,
                              distance=distance,
                              seats=seats,
                              pickup_time_new=pickup_time_new,
                              matched=False, active=True)
        return passenger

    @staticmethod
    def deactivate(passenger_id):
        passenger = PassengersRepository.get(passenger_id)
        if passenger is None:
            return None
        else:
            passenger.active = False
            return passenger


def _get_active_by_id(id):
    return (Base.session.query(Passenger).
            options(contains_eager('user')).
            select_from(Passenger).
            join(User).
            filter(User.deleted == false()).
            filter(Passenger.id == id).
            filter(Passenger.active == true()))


def get_active_by_id(id):
    return expunged(_get_active_by_id(id).first(), Base.session)


def _get_all_unmatched():
    return (Base.session.query(Passenger).
            options(contains_eager('user')).
            select_from(Passenger).
            join(User).
            filter(User.deleted == false()).
            filter(Passenger.active == true()).
            filter(Passenger.matched == false()))


def get_all_unmatched():
    return [expunged(p, Base.session)
            for p in _get_all_unmatched()]


def _get_all_unmatched_by_region(region):
    return (Base.session.query(Passenger).
            options(contains_eager('user')).
            select_from(Passenger).
            join(User).
            outerjoin(UserPosition).
            filter(User.deleted == false()).
            filter(Passenger.active == true()).
            filter(Passenger.matched == false()).
            filter(or_(UserPosition.region.is_(None),
                       UserPosition.region == region)))


def get_all_unmatched_by_region(region):
    return [expunged(p, Base.session)
            for p in _get_all_unmatched_by_region(region)]


def _get_all_active():
    return (Base.session.query(Passenger).
            options(contains_eager('user')).
            select_from(Passenger).
            join(User).
            filter(User.deleted == false()).
            filter(Passenger.active == true()))


def get_all_active():
    return [expunged(p, Base.session)
            for p in _get_all_active()]


def _get_all_expired(expire_after):
    expire_date = datetime.utcnow() - timedelta(minutes=expire_after)
    return (Base.session.query(Passenger).
            options(contains_eager('user')).
            select_from(Passenger).
            join(User).
            filter(User.deleted == false()).
            filter(Passenger.active == true()).
            filter(Passenger.matched == false()).
            filter(or_(and_(Passenger.pickup_time_new == null(),
                            Passenger.created < expire_date),
                       and_(Passenger.pickup_time_new != null(),
                            Passenger.pickup_time_new < expire_date))))


def get_all_expired(expire_after):
    return [expunged(p, Base.session)
            for p in _get_all_expired(expire_after)]
