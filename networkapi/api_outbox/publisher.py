# -*- coding: utf-8 -*-
"""Publishes outbox events to Pub/Sub through the REST API.

The official google-cloud-pubsub client does not run on Python 2.7, so this module
calls the REST endpoints with ``requests``. The service account token is minted by
signing a JWT with pycrypto (already pinned in requirements.txt).
"""
import base64
import json
import time

import requests

PUBSUB_PUBLISH_URL = 'https://pubsub.googleapis.com/v1/projects/{project}/topics/{topic}:publish'
TOKEN_URL = 'https://oauth2.googleapis.com/token'
PUBSUB_SCOPE = 'https://www.googleapis.com/auth/pubsub'
JWT_GRANT_TYPE = 'urn:ietf:params:oauth:grant-type:jwt-bearer'
REQUEST_TIMEOUT = 30


class PublishError(Exception):
    pass


def build_envelope(event):
    """Wire format shared with the BGP consumer (networkapi-bgp src/outbox/publisher.py)."""
    return {
        'event_id': event.event_id,
        'aggregate': event.aggregate,
        'aggregate_id': event.aggregate_id,
        'op': event.op,
        'version': event.version,
        'origin': event.origin,
        'occurred_at': event.occurred_at.isoformat(),
        'payload': json.loads(event.payload),
    }


def ordering_key(envelope):
    return '%s:%s' % (envelope['aggregate'], envelope['aggregate_id'])


def _b64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=')


def _sign_jwt(claims, private_key_pem):
    from Crypto.Hash import SHA256
    from Crypto.PublicKey import RSA
    from Crypto.Signature import PKCS1_v1_5

    header = _b64url(json.dumps({'alg': 'RS256', 'typ': 'JWT'}, sort_keys=True))
    body = _b64url(json.dumps(claims, sort_keys=True))
    signing_input = header + b'.' + body
    signature = PKCS1_v1_5.new(RSA.importKey(private_key_pem)).sign(SHA256.new(signing_input))
    return (signing_input + b'.' + _b64url(signature)).decode('ascii')


class ServiceAccountTokenProvider(object):
    """Access token for a service account key file. Cached until shortly before expiry."""

    def __init__(self, key_file):
        with open(key_file) as handle:
            key = json.load(handle)
        self._email = key['client_email']
        self._private_key = key['private_key']
        self._token = None
        self._expires_at = 0

    def get(self):
        now = int(time.time())
        if self._token and now < self._expires_at - 60:
            return self._token

        assertion = _sign_jwt(
            {'iss': self._email, 'scope': PUBSUB_SCOPE, 'aud': TOKEN_URL, 'iat': now, 'exp': now + 3600},
            self._private_key,
        )
        response = requests.post(
            TOKEN_URL,
            data={'grant_type': JWT_GRANT_TYPE, 'assertion': assertion},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        body = response.json()
        self._token = body['access_token']
        self._expires_at = now + int(body.get('expires_in', 3600))
        return self._token


class PubSubRestPublisher(object):
    """Publishes envelopes to one topic. The topic must have message ordering enabled."""

    def __init__(self, project_id, topic, token_provider):
        self._url = PUBSUB_PUBLISH_URL.format(project=project_id, topic=topic)
        self._tokens = token_provider

    def publish(self, envelope):
        message = {
            'data': base64.b64encode(json.dumps(envelope, sort_keys=True).encode('utf-8')).decode('ascii'),
            'orderingKey': ordering_key(envelope),
            'attributes': {
                'event_id': envelope['event_id'],
                'aggregate': envelope['aggregate'],
                'op': envelope['op'],
            },
        }
        response = requests.post(
            self._url,
            json={'messages': [message]},
            headers={'Authorization': 'Bearer %s' % self._tokens.get()},
            timeout=REQUEST_TIMEOUT,
        )
        if response.status_code != 200:
            raise PublishError('Pub/Sub returned %s: %s' % (response.status_code, response.text[:500]))
