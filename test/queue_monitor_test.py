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
from ..animation_client.obj_tree import Obj3dNode

from ..animation_client.queue_monitor import aesel_queue_monitor

from aesel.model.AeselScene import AeselScene

@pytest.fixture
def update_queue():
    return queue.Queue()

@pytest.fixture
def general_api_wrapper():
    return GeneralApiWrapper()

@pytest.fixture
def object_api_wrapper():
    return ObjectApiWrapper()

@pytest.fixture
def portation_api_wrapper():
    return PortationApiWrapper()

def test_scene_list_updates(update_queue, general_api_wrapper, object_api_wrapper, portation_api_wrapper):
    # Set up our mocks
    general_api_wrapper.add_to_scenes_ui_list = MagicMock()
    general_api_wrapper.update_scenes_ui_list = MagicMock()
    general_api_wrapper.remove_from_scenes_ui_list = MagicMock()
    general_api_wrapper.clear_scenes_ui_list = MagicMock()

    # Test Add Scene to Scene List
    new_scene = AeselScene()
    new_scene.name = "test"
    new_scene.key = "testKey"
    update_queue.put({"type": "list_add", "data": new_scene})

    aesel_queue_monitor(general_api_wrapper,
                        object_api_wrapper,
                        portation_api_wrapper,
                        update_queue)

    general_api_wrapper.add_to_scenes_ui_list.assert_called_with("test", "testKey")

    # Test Update Scene in Scene List
    new_scene = AeselScene()
    new_scene.name = "test"
    new_scene.key = "testKey"
    update_queue.put({"type": "list_update", "data": new_scene})

    aesel_queue_monitor(general_api_wrapper,
                        object_api_wrapper,
                        portation_api_wrapper,
                        update_queue)

    general_api_wrapper.update_scenes_ui_list.assert_called_with("test", "testKey")

    # Test Delete Scene from Scene List
    update_queue.put({"type": "list_delete", "data": "testKey"})

    aesel_queue_monitor(general_api_wrapper,
                        object_api_wrapper,
                        portation_api_wrapper,
                        update_queue)

    general_api_wrapper.remove_from_scenes_ui_list.assert_called_with("testKey")

    # Test Set Scene List
    update_queue.put({"type": "list_set", "data": {"scenes": [{"key": "testKey", "name": "test"}]}})

    aesel_queue_monitor(general_api_wrapper,
                        object_api_wrapper,
                        portation_api_wrapper,
                        update_queue)

    general_api_wrapper.clear_scenes_ui_list.assert_called()
    general_api_wrapper.add_to_scenes_ui_list.assert_called_with("test", "testKey")

def test_obj3d_updates(update_queue, general_api_wrapper, object_api_wrapper, portation_api_wrapper):
    # Set up our mocks
    active_object = Object3dInterface("name",
                                      {"key": "123"},
                                      True,
                                      [1.0, 2.0, 3.0],
                                      [6.0, 5.0, 4.0],
                                      [2.0, 2.0, 2.0],
                                      [], None, None)
    object_api_wrapper.select_all = MagicMock()
    object_api_wrapper.get_object_by_name = MagicMock(return_value=active_object)
    object_api_wrapper.add_live_object = MagicMock()
    object_api_wrapper.remove_live_object = MagicMock()
    object_api_wrapper.delete_selected_objects = MagicMock()

    # Test Live Update Flow
    update_queue.put({"type": "live_update", "name": "test", "transform": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]})

    aesel_queue_monitor(general_api_wrapper,
                        object_api_wrapper,
                        portation_api_wrapper,
                        update_queue)

    object_api_wrapper.get_object_by_name.assert_called_with("test")

    # Test Viewport Clear Flow
    update_queue.put({"type": "viewport_clear"})

    aesel_queue_monitor(general_api_wrapper,
                        object_api_wrapper,
                        portation_api_wrapper,
                        update_queue)

    object_api_wrapper.select_all.assert_called()
    object_api_wrapper.delete_selected_objects.assert_called()

    # Test Object Lock
    update_queue.put({"type": "lock_object", "obj_name": "name", "obj_key": "key"})

    aesel_queue_monitor(general_api_wrapper,
                        object_api_wrapper,
                        portation_api_wrapper,
                        update_queue)

    object_api_wrapper.add_live_object.assert_called_with("name", "key")

    # Test Object Unlock
    update_queue.put({"type": "unlock_object", "obj_name": "name", "obj_key": "key"})

    aesel_queue_monitor(general_api_wrapper,
                        object_api_wrapper,
                        portation_api_wrapper,
                        update_queue)

    object_api_wrapper.remove_live_object.assert_called_with("name", "key")

    # Test Object Key Assign
    update_queue.put({"type": "obj_key_assign", "blender_obj_name": "name", "aesel_obj_key": "key"})

    aesel_queue_monitor(general_api_wrapper,
                        object_api_wrapper,
                        portation_api_wrapper,
                        update_queue)

    object_api_wrapper.get_object_by_name.assert_called_with("name")

    # Test parent updates
    root_node = Obj3dNode({"parent":"", "name":"1"})
    child_node = Obj3dNode({"parent":"1", "name":"2"})
    child_node.children.append(Obj3dNode({"parent":"2", "name":"3"}))
    root_node.children.append(child_node)
    update_queue.put({"type": "parent_updates",
                      "objectTree": [root_node]})

    aesel_queue_monitor(general_api_wrapper,
                        object_api_wrapper,
                        portation_api_wrapper,
                        update_queue)

    object_api_wrapper.get_object_by_name.assert_called_with("3")
