# -*- coding: utf-8 -*-
from plone import api


def setoAuthTokenFromCASSAMLProperties(event):
    """ This subscriber is responsible for the update of the oauth_token from the CAS
        authentication.
    """
    user = api.user.get(event.properties['username'])
    user.setMemberProperties(mapping=dict(oauth_token=event.properties['oauthToken']))
