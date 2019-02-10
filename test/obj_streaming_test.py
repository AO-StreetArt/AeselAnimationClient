# -*- coding: utf-8 -*-

"""
Apache2 License Notice
Copyright 2018 Alex Barry
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import pytest
import queue

from unittest.mock import MagicMock, patch

from ..animation_client.api_wrapper.general_api_wrapper import AddonPreferences, GeneralApiWrapper
from ..animation_client.api_wrapper.portation_api_wrapper import PortationApiWrapper
from ..animation_client.api_wrapper.obj_api_wrapper import ObjectApiWrapper, Object3dInterface

from ..animation_client.obj_streaming import send_object_updates, listen_for_object_updates

@pytest.fixture
def update_queue():
    return queue.Queue()

mock_loop_shutoff = True
mock_loop_iterations = 0

def shutoff_mock_loop():
    global mock_loop_shutoff
    global mock_loop_iterations
    if (mock_loop_shutoff and mock_loop_iterations > 0):
        return False
    if mock_loop_iterations == 0:
        mock_loop_iterations += 1
    return True

@patch('socket.socket')
def test_updates_recv(MockSocket, update_queue):
    global mock_loop_shutoff
    sock = MockSocket()
    # This is generated with the following command, using the key and IV generated below:
    # echo -n "{\"test\":1}" | openssl enc -e -aes-256-cbc -a -K 3A7452FE1DF78115B9CCD85C8D0BDCCCE54B3E0EC72372B69E68A466F0A01823 -iv AFD6814E8FDA687E6D2CDDFCF6D55890
    sock.recvfrom.return_value = ("K1RzYX1Wb/8VbzfNBle62Q==", "")

    # Set up our mock Blender API's
    addon_prefs = AddonPreferences()
    addon_prefs.udp_host = "127.0.0.1"
    addon_prefs.udp_port = 9000
    addon_prefs.udp_encryption_active = True
    # These are generated with the following command:
    # openssl enc -aes-256-cbc -k testPassword -P -md sha1
    addon_prefs.aesel_udp_decryption_iv = "AFD6814E8FDA687E6D2CDDFCF6D55890"
    addon_prefs.aesel_udp_decryption_key = "3A7452FE1DF78115B9CCD85C8D0BDCCCE54B3E0EC72372B69E68A466F0A01823"

    general_api_wrapper = GeneralApiWrapper()
    general_api_wrapper.get_addon_preferences = MagicMock(return_value=addon_prefs)
    general_api_wrapper.is_udp_listener_active = MagicMock(return_value=mock_loop_shutoff, side_effect=shutoff_mock_loop)

    listen_for_object_updates(general_api_wrapper, update_queue)

    assert(not update_queue.empty())
    data_dict = update_queue.get()
    assert(data_dict["type"] == "live_update")

@patch('aesel.AeselEventClient.AeselEventClient')
def test_updates_send(MockEventClient, update_queue):
    # Set up our mock Aesel API's
    mock_client = MockEventClient()

    # Set up our mock Blender API's
    addon_prefs = AddonPreferences()
    addon_prefs.asset_file_location = "."
    addon_prefs.update_rate = 2.0

    general_api_wrapper = GeneralApiWrapper()
    general_api_wrapper.get_addon_preferences = MagicMock(return_value=addon_prefs)
    general_api_wrapper.get_current_scene_id = MagicMock(return_value="testKey")
    general_api_wrapper.is_udp_sender_active = MagicMock(return_value=True)

    object_api_wrapper = ObjectApiWrapper()
    active_object = Object3dInterface("name",
                                      {"key": "123"},
                                      True,
                                      [1.0, 2.0, 3.0],
                                      [6.0, 5.0, 4.0],
                                      [2.0, 2.0, 2.0],
                                      [[1.0, 1.0, 1.0, 1.0], [1.0, 1.0, 1.0, 1.0], [1.0, 1.0, 1.0, 1.0], [1.0, 1.0, 1.0, 1.0]])
    object_api_wrapper.iterate_over_live_objects = MagicMock(return_value=[("123", "name")])
    object_api_wrapper.get_object_by_name = MagicMock(return_value=active_object)

    # Test Sending Object Updates
    send_object_updates(general_api_wrapper, object_api_wrapper, mock_client, update_queue)

    mock_client.send_object_update.assert_called()
