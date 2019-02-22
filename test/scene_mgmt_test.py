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

from ..animation_client.scene_mgmt import _add_aesel_scene, _update_aesel_scene, _delete_aesel_scene, _find_aesel_scenes, _register_aesel_device, _deregister_aesel_device, _save_scene_asset

@pytest.fixture
def update_queue():
    return queue.Queue()

@patch('aesel.AeselTransactionClient.AeselTransactionClient')
def test_scene_crud(MockTransactionClient, update_queue):
    # Set up our mocks
    mock_client = MockTransactionClient()
    general_api_wrapper = GeneralApiWrapper()
    general_api_wrapper.get_selected_scene = MagicMock(return_value="testKey")

    # Run the create test
    _add_aesel_scene(mock_client, update_queue, "testKey", "testName", "testTag")

    assert(not update_queue.empty())
    data_dict = update_queue.get()
    assert(data_dict["type"] == "list_add")
    assert(data_dict["data"].name == "testName")

    # Run the update test
    _update_aesel_scene(general_api_wrapper, mock_client, update_queue, "testName2", "testTag2")

    assert(not update_queue.empty())
    data_dict = update_queue.get()
    assert(data_dict["type"] == "list_update")
    assert(data_dict["data"].name == "testName2")

    # Run the delete test
    _delete_aesel_scene(general_api_wrapper, mock_client, update_queue)

    assert(not update_queue.empty())
    data_dict = update_queue.get()
    assert(data_dict["type"] == "list_delete")
    assert(data_dict["data"] == "testKey")

    # Run the query test
    _find_aesel_scenes(mock_client, update_queue, "testKey", "testName", "testTag")

    assert(not update_queue.empty())
    data_dict = update_queue.get()
    assert(data_dict["type"] == "list_set")

@patch('aesel.AeselTransactionClient.AeselTransactionClient')
def test_scene_registration(MockTransactionClient, update_queue):
    # Set up our mocks
    mock_client = MockTransactionClient()
    mock_client.query_asset_relationships.return_value = [{"assetId": "123",
                                                          "assetSubId": "456",
                                                          "name": "testAsset",
                                                          "relationshipType": "test1",
                                                          "relationshipSubtype": "test2",
                                                          "relatedId": "12345"}]
    mock_client.bulk_query_asset_metadata.return_value = [{"fileType": "blend",
                                                           "key": "123"}]
    mock_client.get_asset.return_value = b'abcdefghijklmnop'
    mock_client.object_query.return_value = {"objects": [{"key": "12345",
                                                          "name": "testName",
                                                          "parent": MagicMock(),
                                                          "transform": []}]}
    addon_prefs = AddonPreferences()
    addon_prefs.asset_file_location = "."
    addon_prefs.device_id = ""
    addon_prefs.advertised_udp_host = ""
    addon_prefs.udp_port = 7000
    general_api_wrapper = GeneralApiWrapper()
    general_api_wrapper.get_addon_preferences = MagicMock(return_value=addon_prefs)
    general_api_wrapper.get_current_scene_id = MagicMock(return_value="testKey")
    general_api_wrapper.get_current_scene_name = MagicMock(return_value="testScene")
    general_api_wrapper.get_executable_filepath = MagicMock(return_value=".")
    general_api_wrapper.get_selected_scene = MagicMock(return_value="testKey")
    general_api_wrapper.get_selected_scene_name = MagicMock(return_value="testScene")
    general_api_wrapper.set_current_scene_id = MagicMock()
    general_api_wrapper.set_current_scene_name = MagicMock()

    # Run the Registration test
    _register_aesel_device(general_api_wrapper, mock_client, update_queue)

    assert(not update_queue.empty())
    data_dict = update_queue.get()
    print(data_dict)
    assert(data_dict["type"] == "asset_import")
    assert(data_dict["dataMap"][0]["relationshipType"] == "test1")

    assert(not update_queue.empty())
    data_dict2 = update_queue.get()
    assert(data_dict2["type"] == "asset_import")
    assert(data_dict2["dataMap"][0]["relationshipType"] == "test1")

    assert(not update_queue.empty())
    data_dict3 = update_queue.get()
    assert(data_dict3["type"] == "parent_updates")

    # Run the deregistration test
    _deregister_aesel_device(general_api_wrapper, mock_client, update_queue)

    assert(not update_queue.empty())
    data_dict = update_queue.get()
    assert(data_dict["type"] == "viewport_clear")

@patch('aesel.AeselTransactionClient.AeselTransactionClient')
def test_save_scene_asset(MockTransactionClient, update_queue):
    # Set up our mocks
    mock_client = MockTransactionClient()

    addon_prefs = AddonPreferences()
    addon_prefs.asset_file_location = "."
    addon_prefs.asset_file_type = "blend"

    general_api_wrapper = GeneralApiWrapper()
    general_api_wrapper.get_addon_preferences = MagicMock(return_value=addon_prefs)
    general_api_wrapper.get_executable_filepath = MagicMock(return_value=".")
    general_api_wrapper.get_current_scene_id = MagicMock(return_value="testKey")
    general_api_wrapper.get_current_scene_name = MagicMock(return_value="testScene")
    general_api_wrapper.get_selected_scene = MagicMock(return_value="testKey")
    general_api_wrapper.get_selected_scene_name = MagicMock(return_value="testScene")
    general_api_wrapper.set_current_scene_id = MagicMock()
    general_api_wrapper.set_current_scene_name = MagicMock()

    object_api_wrapper = ObjectApiWrapper()
    active_object = Object3dInterface("name",
                                      {"key": "123"},
                                      True,
                                      [1.0, 2.0, 3.0],
                                      [6.0, 5.0, 4.0],
                                      [2.0, 2.0, 2.0],
                                      [], None, "")
    object_api_wrapper.iterate_over_selected_objects = MagicMock(return_value=[active_object])

    portation_api_wrapper = PortationApiWrapper()
    portation_api_wrapper.export_blend_file = MagicMock()

    _save_scene_asset(general_api_wrapper, object_api_wrapper, portation_api_wrapper, mock_client, "testAsset", True)
