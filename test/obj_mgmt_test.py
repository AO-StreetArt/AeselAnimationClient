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

from ..animation_client.obj_mgmt import _initiate_create_aesel_obj_flow, _create_aesel_object, _initiate_delete_aesel_obj_flow, _delete_aesel_object, _lock_aesel_object, _unlock_aesel_object

@pytest.fixture
def update_queue():
    return queue.Queue()

@patch('aesel.AeselTransactionClient.AeselTransactionClient')
def test_obj_crud(MockTransactionClient, update_queue):
    # Set up our mock Aesel API's
    mock_client = MockTransactionClient()
    mock_client.query_asset_relationships.return_value = [{"assetId": "123",
                                                          "assetSubId": "456",
                                                          "name": "testAsset",
                                                          "relationshipType": "test1",
                                                          "relationshipSubtype": "test2",
                                                          "relatedId": "abc"}]
    mock_client.object_query.return_value = {"objects": [{"key": "12345",
                                                          "name": "testName",
                                                          "transform": []}]}

    # Set up our mock Blender API's
    addon_prefs = AddonPreferences()
    addon_prefs.asset_file_location = "."

    general_api_wrapper = GeneralApiWrapper()
    general_api_wrapper.get_addon_preferences = MagicMock(return_value=addon_prefs)
    general_api_wrapper.get_executable_filepath = MagicMock(return_value=".")
    general_api_wrapper.get_current_scene_id = MagicMock(return_value="testKey")
    general_api_wrapper.get_current_scene_name = MagicMock(return_value="testScene")
    general_api_wrapper.set_current_scene_id = MagicMock()
    general_api_wrapper.set_current_scene_name = MagicMock()

    object_api_wrapper = ObjectApiWrapper()
    active_object = Object3dInterface("name",
                                      {"key": "123"},
                                      True,
                                      [1.0, 2.0, 3.0],
                                      [6.0, 5.0, 4.0],
                                      [2.0, 2.0, 2.0],
                                      [])
    object_api_wrapper.get_active_object = MagicMock(return_value=active_object)
    object_api_wrapper.delete_selected_objects = MagicMock()

    portation_api_wrapper = PortationApiWrapper()
    portation_api_wrapper.export_obj_file = MagicMock()

    # Test Object Create flow
    new_obj = _initiate_create_aesel_obj_flow(general_api_wrapper,
                                              portation_api_wrapper,
                                              object_api_wrapper,
                                              mock_client)

    assert(new_obj.name == "name")
    assert(new_obj.scene == "testKey")
    assert(new_obj.translation == [1.0, 2.0, 3.0])
    assert(new_obj.euler_rotation == [6.0, 5.0, 4.0])
    assert(new_obj.scale == [2.0, 2.0, 2.0])

    _create_aesel_object(general_api_wrapper,
                         portation_api_wrapper,
                         object_api_wrapper,
                         mock_client,
                         update_queue, new_obj)

    assert(not update_queue.empty())
    data_dict = update_queue.get()
    assert(data_dict["type"] == "obj_key_assign")
    assert(data_dict["blender_obj_name"] == "name")

    # Test Object Delete Flow
    scene_id, obj_id = _initiate_delete_aesel_obj_flow(general_api_wrapper, object_api_wrapper)

    _delete_aesel_object(mock_client, scene_id, obj_id)
    mock_client.delete_object.assert_called_with(scene_id, obj_id)

@patch('aesel.AeselTransactionClient.AeselTransactionClient')
def test_obj_locking(MockTransactionClient, update_queue):
    # Set up our mock Aesel API's
    mock_client = MockTransactionClient()

    # Set up our mock Blender API's
    addon_prefs = AddonPreferences()
    addon_prefs.device_id = "abc"

    general_api_wrapper = GeneralApiWrapper()
    general_api_wrapper.get_addon_preferences = MagicMock(return_value=addon_prefs)
    general_api_wrapper.get_current_scene_id = MagicMock(return_value="testKey")

    object_api_wrapper = ObjectApiWrapper()
    active_object = Object3dInterface("name",
                                      {"key": "123"},
                                      True,
                                      [1.0, 2.0, 3.0],
                                      [6.0, 5.0, 4.0],
                                      [2.0, 2.0, 2.0],
                                      [])
    object_api_wrapper.get_active_object = MagicMock(return_value=active_object)

    # Execute Lock Test
    _lock_aesel_object(general_api_wrapper, object_api_wrapper, mock_client, update_queue)

    assert(not update_queue.empty())
    data_dict = update_queue.get()
    assert(data_dict["type"] == "lock_object")
    assert(data_dict["obj_key"] == "123")
    assert(data_dict["obj_name"] == "name")

    mock_client.lock_object.assert_called_with("testKey", "123", "abc")

    # Execute Unlock Test
    _unlock_aesel_object(general_api_wrapper, object_api_wrapper, mock_client, update_queue)

    assert(not update_queue.empty())
    data_dict = update_queue.get()
    assert(data_dict["type"] == "unlock_object")
    assert(data_dict["obj_key"] == "123")
    assert(data_dict["obj_name"] == "name")

    mock_client.unlock_object.assert_called_with("testKey", "123", "abc")
