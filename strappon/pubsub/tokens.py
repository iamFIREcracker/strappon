#!/usr/bin/env python

from weblib.pubsub import Publisher


class TokensByUserIdGetter(Publisher):
    def perform(self, repository, userid):
        self.publish('tokens_found', repository.get_all_by_user_id(userid))


class TokenCreator(Publisher):
    def perform(self, repository, userid):
        token = repository.create(userid)
        self.publish('token_created', token)


class TokenSerializer(Publisher):
    def perform(self, token):
        self.publish('token_serialized', dict(id=token.id,
                                              user_id=token.user_id))
