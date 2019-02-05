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

import copy

from .asset_mgmt import save_selected_as_obj_asset, gen_asset_metadata

from aesel.AeselTransactionClient import AeselTransactionClient
from aesel.model.AeselAssetRelationship import AeselAssetRelationship
from aesel.model.AeselObject import AeselObject

def _create_aesel_object(general_api_wrapper, object_api_wrapper, transaction_client, updates_queue, new_obj):
    scene_key = general_api_wrapper.get_current_scene_id()
    active_obj = object_api_wrapper.get_active_object()

    # Post the Object
    obj_response_json = transaction_client.create_object(scene_key, new_obj)
    print(obj_response_json)

    # Send a request on a queue to update the obj key on the main thread
    updates_queue.put({'type': 'obj_key_assign',
                       'blender_obj_name': active_obj.get_name(),
                       'aesel_obj_key': obj_response_json["objects"][0]["key"]})

    # Post an Asset
    new_asset_key = save_selected_as_obj_asset(new_obj.name, True, export_file=False)

    # Post a new Asset Relationship
    new_relation = AeselAssetRelationship()
    new_relation.asset = new_asset_key
    new_relation.type = "object"
    new_relation.related = obj_response_json["objects"][0]["key"]
    response_json = transaction_client.save_asset_relationship(new_relation)

    print(response_json)

def _initiate_create_aesel_obj_flow(general_api_wrapper, object_api_wrapper, transaction_client, updates_queue):
    active_obj = object_api_wrapper.get_active_object()
    # First, we need to save the current transform, and move the object
    # to (0,0,0) so that it exports correctly
    current_location = [copy.deepcopy(active_obj.get_location_x()),
                        copy.deepcopy(active_obj.get_location_y()),
                        copy.deepcopy(active_obj.get_location_z())]
    current_rotation = [copy.deepcopy(active_obj.get_erotation_x()),
                        copy.deepcopy(active_obj.get_erotation_y()),
                        copy.deepcopy(active_obj.get_erotation_z())]
    current_scale = [copy.deepcopy(active_obj.get_scale_x()),
                     copy.deepcopy(active_obj.get_scale_y()),
                     copy.deepcopy(active_obj.get_scale_z())]
    active_obj.set_location_x(0.0)
    active_obj.set_location_y(0.0)
    active_obj.set_location_z(0.0)
    active_obj.set_erotation_x(0.0)
    active_obj.set_erotation_y(0.0)
    active_obj.set_erotation_z(0.0)
    active_obj.set_scale_x(0.0)
    active_obj.set_scale_y(0.0)
    active_obj.set_scale_z(0.0)
    save_selected_as_obj_asset(active_obj.name, True, post_asset=False)
    # Move the object back
    active_obj.set_location_x(current_location[0])
    active_obj.set_location_y(current_location[1])
    active_obj.set_location_z(current_location[2])
    active_obj.set_erotation_x(current_rotation[0])
    active_obj.set_erotation_y(current_rotation[1])
    active_obj.set_erotation_z(current_rotation[2])
    active_obj.set_scale_x(current_scale[0])
    active_obj.set_scale_y(current_scale[1])
    active_obj.set_scale_z(current_scale[2])

    # Build an Aesel Object
    new_obj = AeselObject()
    new_obj.name = obj.name
    new_obj.type = "mesh"
    new_obj.subtype = "custom"
    new_obj.scene = general_api_wrapper.get_current_scene_id()
    new_obj.translation = current_location
    new_obj.euler_rotation = current_rotation
    new_obj.scale = current_scale

    return new_obj

def _delete_aesel_object(transaction_client, scene_key, object_key):
    # Get the assets associated to the selected object
    obj_relationship_query = AeselAssetRelationship()
    obj_relationship_query.related = object_key
    obj_relationship_query.type = "object"
    obj_relation_result = transaction_client.query_asset_relationships(obj_relationship_query)

    # Delete the object assets
    for relation in obj_relation_result:
        transaction_client.delete_asset(relation["assetId"])

    # Delete the object from aesel
    transaction_client.delete_object(scene_key, object_key)

def _initiate_delete_aesel_obj_flow(general_api_wrapper, object_api_wrapper):
    # Get return information out of Blender state before changing it
    scene_id = general_api_wrapper.get_current_scene_id()
    active_obj = object_api_wrapper.get_active_object()
    object_key = active_obj.get_property("key")

    # Delete selected objects from blender
    object_api_wrapper.delete_selected_objects()

    # Return the scene key and object key
    return scene_id, object_key

def _lock_aesel_object(general_api_wrapper, object_api_wrapper, transaction_client, updates_queue):
    addon_prefs = general_api_wrapper.get_addon_preferences()
    scene_id = general_api_wrapper.get_current_scene_id()
    active_obj = object_api_wrapper.get_active_object()
    object_key = active_obj.get_property("key")
    object_name = active_obj.get_name()

    # Send the Aesel request
    response_json = transaction_client.lock_object(scene_id, object_key, addon_prefs.device_id)
    print(response_json)

    # Drop a message on the queue to make the object live
    updates_queue.put({'type': 'lock_object',
                       'obj_key': object_key,
                       'obj_name': object_name})

def _unlock_aesel_object(general_api_wrapper, object_api_wrapper, transaction_client, updates_queue):
    addon_prefs = general_api_wrapper.get_addon_preferences()
    scene_id = general_api_wrapper.get_current_scene_id()
    active_obj = object_api_wrapper.get_active_object()
    object_key = active_obj.get_property("key")
    object_name = active_obj.get_name()

    # Send the Aesel request
    response_json = transaction_client.unlock_object(scene_id, object_key, addon_prefs.device_id)
    print(response_json)

    # Drop a message on the queue to make the object live
    updates_queue.put({'type': 'unlock_object',
                       'obj_key': object_key,
                       'obj_name': object_name})
