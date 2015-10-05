# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import mock
from django.test import TestCase
from django.db import IntegrityError
#from . import factory

#from .. import models

import logging

LOG = logging.getLogger(__name__)

class UsuarioTestCase(TestCase):

    #fixtures = ['initial_usuario.json']

    def setUp(self):
        pass
        #self.usuario = factory.UsuarioFactory()

    def tearDown(self):
        self.usuario = None

    def test_create_user_with_success(self):
        pass
        # self.assertTrue(self.usuario.id)