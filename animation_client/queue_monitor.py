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

from .asset_mgmt import import_obj_asset, import_blend_asset

# Monitor a queue for updates to make to the main viewport on the main thread.
def aesel_queue_monitor(general_api_wrapper, object_api_wrapper, portation_api_wrapper, updates_queue):
    while not updates_queue.empty():
        data_dict = updates_queue.get()
        print("Processing Data on main thread: %s" % data_dict)

        if data_dict['type'] == 'live_update':
            obj = object_api_wrapper.get_object_by_name(data_dict['name'])
            transform = data_dict['transform']
            obj.set_transform(transform)

        elif data_dict['type'] == 'list_add':
            # Populate the Scene List in the UI
            general_api_wrapper.add_to_scenes_ui_list(data_dict['data'].name, data_dict['data'].key)

        elif data_dict['type'] == 'list_update':
            general_api_wrapper.update_scenes_ui_list(data_dict['data'].name, data_dict['data'].key)

        elif data_dict['type'] == 'list_delete':
            general_api_wrapper.remove_from_scenes_ui_list(data_dict['data'])

        elif data_dict['type'] == 'list_set':
            general_api_wrapper.clear_scenes_ui_list()
            for scene in data_dict['data']['scenes']:
                general_api_wrapper.add_to_scenes_ui_list(scene['name'], scene['key'])

        elif data_dict['type'] == 'viewport_clear':
            # select all objects.
            object_api_wrapper.select_all()

            # remove all selected.
            object_api_wrapper.delete_selected_objects()

        elif data_dict['type'] == 'asset_import':
            # Actually call the import operator(s)
            if data_dict["filename"].endswith(".obj"):
                import_obj_asset(general_api_wrapper,
                                 portation_api_wrapper,
                                 data_dict)
            elif data_dict["filename"].endswith(".blend"):
                import_blend_asset(general_api_wrapper,
                                   portation_api_wrapper,
                                   data_dict)

        elif data_dict['type'] == 'lock_object':
            object_api_wrapper.add_live_object(data_dict['obj_name'], data_dict['obj_key'])

        elif data_dict['type'] == 'unlock_object':
            object_api_wrapper.remove_live_object(data_dict['obj_name'], data_dict['obj_key'])

        elif data_dict['type'] == 'obj_key_assign':
            obj = object_api_wrapper.get_object_by_name(data_dict["blender_obj_name"])
            obj.set_property("key", data_dict["aesel_obj_key"])
    return 0.1
