# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import mock
from django.test import TestCase
from django.db import IntegrityError
from networkapi.usuario.tests import factory

import logging

LOG = logging.getLogger(__name__)

class UsuarioTestCase(TestCase):

    #fixtures = ['initial_usuario.json']

    def setUp(self):
        self.usuario = factory.UserWithGroupFactory()

    def tearDown(self):
        self.usuario = None

    def test_create_user_with_success(self):
        self.assertTrue(self.usuario.id)