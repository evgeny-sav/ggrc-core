# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Unit test suite for appengine login logic."""

import json
import unittest

import mock
from werkzeug import exceptions

from ggrc.login import appengine as login_appengine
from ggrc.utils import structures


class TestAppengineLogin(unittest.TestCase):
  """Unit test suite for appengine login logic."""

  # pylint: disable=invalid-name; test method names are too long for pylint

  ALLOWED_APPID = "allowed"
  EMAIL = "user@example.com"

  def setUp(self):
    """Set up request mock and mock dependencies."""
    self.request = mock.MagicMock()
    self.request.headers = structures.CaseInsensitiveDict()

    self.settings_patcher = mock.patch("ggrc.login.appengine.settings")
    self.settings_mock = self.settings_patcher.start()
    self.settings_mock.ALLOWED_QUERYAPI_APP_IDS = [self.ALLOWED_APPID]

    self.person_patcher = mock.patch("ggrc.login.appengine.all_models.Person")
    self.person_mock = self.person_patcher.start()

    # valid headers by default
    self.request.headers["X-appengine-inbound-appid"] = self.ALLOWED_APPID
    self.request.headers["X-ggrc-user"] = json.dumps({"email": self.EMAIL})

  def tearDown(self):
    """Stop patchers."""
    self.person_patcher.stop()
    self.settings_patcher.stop()

  def test_request_loader_no_appid_header(self):
    """No app2app auth if Appid header is missing."""
    self.request.headers.pop("X-appengine-inbound-appid")

    result = login_appengine.request_loader(self.request)

    self.assertIs(result, None)

  def test_request_loader_disallowed_appid(self):
    """HTTP400 if Appid header value is not whitelisted."""
    self.request.headers["X-appengine-inbound-appid"] = "disallowed"

    with self.assertRaises(exceptions.BadRequest):
      login_appengine.request_loader(self.request)

  def test_request_loader_no_user_header(self):
    """HTTP400 if user header is missing."""
    self.request.headers.pop("X-ggrc-user")

    with self.assertRaises(exceptions.BadRequest):
      login_appengine.request_loader(self.request)

  def test_request_loader_user_invalid_json(self):
    """HTTP400 if user header contains invalid json."""
    self.request.headers["X-ggrc-user"] = "not a valid json"

    with self.assertRaises(exceptions.BadRequest):
      login_appengine.request_loader(self.request)

  def test_request_loader_user_incomplete_json(self):
    """HTTP400 if user header contains json with no email."""
    self.request.headers["X-ggrc-user"] = "{}"

    with self.assertRaises(exceptions.BadRequest):
      login_appengine.request_loader(self.request)

  def test_request_loader_user_non_dict_json(self):
    """HTTP400 if user header contains json with not a dict."""
    self.request.headers["X-ggrc-user"] = "[]"

    with self.assertRaises(exceptions.BadRequest):
      login_appengine.request_loader(self.request)

    self.request.headers["X-ggrc-user"] = "12"

    with self.assertRaises(exceptions.BadRequest):
      login_appengine.request_loader(self.request)

  def test_request_loader_user_not_registered(self):
    """HTTP400 if user header contains json with unknown user."""
    # imitate no user found
    self.person_mock.query.filter_by.return_value.first.return_value = None

    with self.assertRaises(exceptions.BadRequest):
      login_appengine.request_loader(self.request)

  def test_request_loader_valid_auth(self):
    """User logged in if Appid and user headers are correct."""
    person = mock.MagicMock()
    self.person_mock.query.filter_by.return_value.first.return_value = person

    result = login_appengine.request_loader(self.request)

    self.assertIs(result, person)
    self.person_mock.query.filter_by.assert_called_with(email=self.EMAIL)
