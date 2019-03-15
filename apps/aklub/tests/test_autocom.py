# -*- coding: utf-8 -*-

# Author: Petr Dlouhý <petr.dlouhy@auto-mat.cz>
#
# Copyright (C) 2017 o.s. Auto*Mat
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase

from .. import autocom
from ..models import AutomaticCommunication, Event, Interaction, Condition, TerminalCondition, UserInCampaign, UserProfile


class AutocomTest(TestCase):
    def setUp(self):
        self.userprofile = UserProfile.objects.create(sex='male')
        self.campaign = Event.objects.create(created=datetime.date(2010, 10, 10))
        self.userincampaign = UserInCampaign.objects.create(userprofile=self.userprofile, campaign=self.campaign)
        c = Condition.objects.create(operation="nor")
        TerminalCondition.objects.create(
            variable="action",
            value="test-autocomm",
            operation="==",
            condition=c,
        )
        AutomaticCommunication.objects.create(
            condition=c,
            template="Vazen{y|a} {pane|pani} $addressment $regular_frequency testovací šablona",
            template_en="Dear {sir|miss} $addressment $regular_frequency test template",
            subject="Testovací komunikace",
            subject_en="Testing communication",
        )

    def test_autocom(self):
        autocom.check(action="test-autocomm")
        communication = Interaction.objects.get(user=self.userprofile)
        self.assertTrue("testovací šablona" in communication.summary)
        self.assertTrue("příteli Auto*Matu" in communication.summary)
        self.assertTrue("Vazeny pane" in communication.summary)

    def test_autocom_female(self):
        self.userprofile.sex = 'female'
        self.userprofile.save()
        autocom.check(action="test-autocomm")
        communication = Interaction.objects.get(user=self.userprofile)
        self.assertIn("testovací šablona", communication.summary)
        self.assertIn("přítelkyně Auto*Matu", communication.summary)
        self.assertIn("Vazena pani", communication.summary)

    def test_autocom_unknown(self):
        self.userprofile.sex = 'unknown'
        self.userprofile.save()
        autocom.check(action="test-autocomm")
        communication = Interaction.objects.get(user=self.userprofile)
        self.assertIn("testovací šablona", communication.summary)
        self.assertIn("příteli/kyně Auto*Matu", communication.summary)
        self.assertIn("Vazeny/a pane/pani", communication.summary)

    def test_autocom_addressment(self):
        self.userprofile.sex = 'male'
        self.userprofile.addressment = 'own addressment'
        self.userprofile.save()
        autocom.check(action="test-autocomm")
        communication = Interaction.objects.get(user=self.userprofile)
        self.assertIn("testovací šablona", communication.summary)
        self.assertIn("own addressment", communication.summary)
        self.assertIn("Vazeny pane", communication.summary)

    def test_autocom_en(self):
        self.userprofile.sex = 'unknown'
        self.userprofile.language = 'en'
        self.userprofile.save()
        autocom.check(action="test-autocomm")
        communication = Interaction.objects.get(user=self.userprofile)
        self.assertIn("test template", communication.summary)
        self.assertIn("Auto*Mat friend", communication.summary)
        self.assertIn("Dear sir", communication.summary)


class GenderStringsValidatorTest(TestCase):
    def test_matches(self):
        self.assertEquals(autocom.gendrify_text('', 'male'), '')
        self.assertEquals(autocom.gendrify_text('asdfasdf', 'male'), 'asdfasdf')
        self.assertEquals(autocom.gendrify_text('{ý|á}', 'male'), 'ý')
        self.assertEquals(autocom.gendrify_text('{ý|á}', 'female'), 'á')
        self.assertEquals(autocom.gendrify_text('{ý/á}', 'female'), 'á')
        self.assertEquals(autocom.gendrify_text('{|á}', 'male'), '')
        self.assertEquals(autocom.gendrify_text('{|á}', 'female'), 'á')
        self.assertEquals(autocom.gendrify_text('{|á}', ''), '/á')
        self.assertEquals(autocom.gendrify_text('asdfasdf{ý|á}', 'male'), 'asdfasdfý')
        self.assertEquals(autocom.gendrify_text('{ý|á}asdfadsfasd', 'male'), 'ýasdfadsfasd')
        self.assertEquals(autocom.gendrify_text('asdfasdf{ý|á}asdfadsfasd', ''), 'asdfasdfý/áasdfadsfasd')
        self.assertEquals(autocom.gendrify_text('asdfasdf{ý/á}asdfadsfasd', ''), 'asdfasdfý/áasdfadsfasd')
        self.assertEquals(autocom.gendrify_text('{ý|á}{ý|á}', 'male'), 'ýý')
        self.assertEquals(autocom.gendrify_text('{ý|á}asdfasdf{ý|á}', 'male'), 'ýasdfasdfý')
        self.assertEquals(autocom.gendrify_text('{ý/á}asdfasdf{ý|á}', 'male'), 'ýasdfasdfý')

    def test_mismatches(self):
        with self.assertRaises(ValidationError):
            autocom.gendrify_text('{ý.á}', 'male')
        with self.assertRaises(ValidationError):
            autocom.gendrify_text('{ý|á}{ý.á}', 'male')
        with self.assertRaises(ValidationError):
            autocom.gendrify_text('{ý.á}{ý|á}', 'male')
        with self.assertRaises(ValidationError):
            autocom.gendrify_text('{ý.á}asdfasdfasdf', 'male')
        with self.assertRaises(ValidationError):
            autocom.gendrify_text('asdfasdfasdf{ý.á}', 'male')
        with self.assertRaises(ValidationError):
            autocom.gendrify_text('asdfasfasfaiasdfasfasdfsdfsfasdfasfasfasfasdfasd{ý.á}')
