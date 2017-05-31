# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import logging

import mock
from django.db import IntegrityError
from django.test import TestCase

from networkapi.usuario.tests import factory

LOG = logging.getLogger(__name__)


class UsuarioTestCase(TestCase):

    fixtures = ['initial_ugrupo.json', 'initial_usuario.json']

    def setUp(self):
        self.usuario = factory.UserWithGroupFactory()

    def tearDown(self):
        self.usuario = None

    def test_create_user_with_success(self):
        self.assertTrue(self.usuario.id)
