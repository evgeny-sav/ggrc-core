# -*- coding: utf-8 -*-

# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Tests for the CustomAttributeColumHandler class"""

import unittest

from mock import MagicMock, patch

from ggrc import app  # noqa  # pylint: disable=unused-import
from ggrc.converters.handlers.custom_attribute import (
    CustomAttributeColumHandler
)
from ggrc.models import CustomAttributeDefinition


CA_TYPES = CustomAttributeDefinition.ValidTypes  # pylint: disable=invalid-name


class CustomAttributeColumHandlerTestCase(unittest.TestCase):
  """Base class for CustomAttributeColumHandler tests"""
  def setUp(self):
    row_converter = MagicMock(name=u"row_converter")
    key = u"a_checkbox_field"
    self.handler = CustomAttributeColumHandler(row_converter, key)


@patch.object(CustomAttributeColumHandler, u"get_ca_definition")
class GetValueTestCase(CustomAttributeColumHandlerTestCase):
  """Tests for the get_value() method"""
  # pylint: disable=invalid-name

  def setUp(self):
    super(GetValueTestCase, self).setUp()
    self.handler.row_converter.obj.custom_attribute_values = []

  @staticmethod
  def _ca_value_factory(id_, type_, value):
    """Create a mocked custom attribute value object"""
    mock_config = {
        u"custom_attribute_id": id_,
        u"custom_attribute.attribute_type": type_,
        u"attribute_object": MagicMock(name=u"attribute_object"),
        u"attribute_value": value,
    }
    return MagicMock(**mock_config)

  def test_returns_string_true_for_truthy_checkbox(self, get_ca_definition):
    """The method should return "TRUE" for checked checkbox CAs."""
    get_ca_definition.return_value = MagicMock(id=117)

    ca_value = self._ca_value_factory(
        id_=117, type_=CA_TYPES.CHECKBOX, value=u"1")
    self.handler.row_converter.obj.custom_attribute_values.append(ca_value)

    result = self.handler.get_value()
    self.assertEqual(result, u"TRUE")

  def test_returns_string_false_for_falsy_checkbox(self, get_ca_definition):
    """The method should return "FALSE" for unchecked checkbox CAs."""
    get_ca_definition.return_value = MagicMock(id=117)

    ca_value = self._ca_value_factory(
        id_=117, type_=CA_TYPES.CHECKBOX, value=u"0")
    self.handler.row_converter.obj.custom_attribute_values.append(ca_value)

    result = self.handler.get_value()
    self.assertEqual(result, u"FALSE")

  def test_returns_string_false_for_missing_checkbox_value(
      self, get_ca_definition
  ):
    """The method should return "FALSE" for checkbox CAs with no value."""
    get_ca_definition.return_value = MagicMock(id=117)

    ca_value = self._ca_value_factory(
        id_=117, type_=CA_TYPES.CHECKBOX, value=None)
    self.handler.row_converter.obj.custom_attribute_values.append(ca_value)

    result = self.handler.get_value()
    self.assertEqual(result, u"FALSE")
