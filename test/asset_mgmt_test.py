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

from unittest.mock import MagicMock, patch

from ..animation_client.api_wrapper.general_api_wrapper import AddonPreferences, GeneralApiWrapper
from ..animation_client.api_wrapper.portation_api_wrapper import PortationApiWrapper
from ..animation_client.api_wrapper.obj_api_wrapper import ObjectApiWrapper, Object3dInterface

from ..animation_client.asset_mgmt import import_obj_asset, import_blend_asset, gen_asset_metadata, save_scene_as_blend_asset, save_selected_as_obj_asset


def test_obj_import():
    # Set up our mocks
    portation_api_wrapper = PortationApiWrapper()
    portation_api_wrapper.import_obj_file = MagicMock()

    object_api_wrapper = ObjectApiWrapper()
    active_object = Object3dInterface("name",
                                      {},
                                      True,
                                      (0.0, 0.0, 0.0),
                                      (0.0, 0.0, 0.0),
                                      (0.0, 0.0, 0.0),
                                      [], None, None)
    object_api_wrapper.get_active_object = MagicMock(return_value=active_object)

    # Run the test
    import_obj_asset(object_api_wrapper, portation_api_wrapper, {"filename": "test",
                                                                 "name": "test",
                                                                 "key": "123",
                                                                 "transform": [0.0]})
    assert(active_object.get_name() == "test")
    assert(active_object.get_property("key") == "123")
    assert(len(active_object.get_transform()) > 0)

@patch('aesel.AeselTransactionClient.AeselTransactionClient')
def test_obj_export(MockTransactionClient):
    # Set up our mocks
    addon_prefs = AddonPreferences()
    addon_prefs.asset_file_location = "."
    general_api_wrapper = GeneralApiWrapper()
    general_api_wrapper.get_addon_preferences = MagicMock(return_value=addon_prefs)
    general_api_wrapper.get_current_scene_name = MagicMock(return_value="testScene")
    general_api_wrapper.get_executable_filepath = MagicMock(return_value=".")

    portation_api_wrapper = PortationApiWrapper()
    portation_api_wrapper.export_obj_file = MagicMock()

    mock_client = MockTransactionClient()

    # Run the test
    new_key = save_selected_as_obj_asset(general_api_wrapper,
                                         portation_api_wrapper,
                                         mock_client, "name", True)

def test_blend_import():
    # Set up our mocks
    portation_api_wrapper = PortationApiWrapper()
    portation_api_wrapper.import_blend_file = MagicMock()

    object_api_wrapper = ObjectApiWrapper()
    active_object = Object3dInterface("cube",
                                      {},
                                      True,
                                      (0.0, 0.0, 0.0),
                                      (0.0, 0.0, 0.0),
                                      (0.0, 0.0, 0.0),
                                      [], None, None)
    object_api_wrapper.iterate_over_selected_objects = MagicMock(return_value=[active_object])
    object_api_wrapper.get_object_by_name = MagicMock(return_value=active_object)

    # Run the test
    import_blend_asset(object_api_wrapper,
                       portation_api_wrapper,
                       {"filename": "test.txt",
                       "dataname": "cube",
                       "scene": "1",
                       "dataMap": [{"name": "cube", "key": "testKey", "assetSubId": "cube", "transform": []}]})

    portation_api_wrapper.import_blend_file.assert_called_with("test.txt", ["cube"])

@patch('aesel.AeselTransactionClient.AeselTransactionClient')
def test_blend_export(MockTransactionClient):
    # Set up our mocks
    addon_prefs = AddonPreferences()
    addon_prefs.asset_file_location = "."
    general_api_wrapper = GeneralApiWrapper()
    general_api_wrapper.get_addon_preferences = MagicMock(return_value=addon_prefs)
    general_api_wrapper.get_current_scene_name = MagicMock(return_value="testScene")
    general_api_wrapper.get_executable_filepath = MagicMock(return_value="test")

    portation_api_wrapper = PortationApiWrapper()
    portation_api_wrapper.export_blend_file = MagicMock()

    mock_client = MockTransactionClient()

    # Run the test
    response = save_scene_as_blend_asset(general_api_wrapper,
                                         portation_api_wrapper,
                                         mock_client, "test", True)

    portation_api_wrapper.export_blend_file.assert_called_with("test/testScene/test.blend")
