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

from .asset_file_mgmt import get_assets_file_path
from .asset_mgmt import save_selected_as_obj_asset

from aesel.AeselTransactionClient import AeselTransactionClient
from aesel.model.AeselScene import AeselScene
from aesel.model.AeselAssetRelationship import AeselAssetRelationship
from aesel.model.AeselUserDevice import AeselUserDevice
from aesel.model.AeselObject import AeselObject

# Method for creating a scene in the Aesel server
def _add_aesel_scene(transaction_client, updates_queue, key, name, tags):
    # Build a new Aesel scene
    new_scene = AeselScene()
    if name != "":
        new_scene.name = name
    if tags != "":
        new_scene.tags = tags.split(",")

    # Send the request
    response_json = transaction_client.create_scene(key, new_scene)
    print(response_json)

    # Put a message onto the updates queue to update the UI
    new_scene.key = key
    updates_queue.put({'type': 'list_add', 'data': new_scene})

def _update_aesel_scene(general_api_wrapper, transaction_client, updates_queue, name, tags):
    # Get the key of the selected scene in the list
    selected_key = general_api_wrapper.get_selected_scene()

    # Build a new Aesel scene
    new_scene = AeselScene()
    if name != "":
        new_scene.name = name
    if tags != "":
        new_scene.tags = tags.split(",")

    # Send the request
    response_json = transaction_client.update_scene(selected_key, new_scene)
    new_scene.key = selected_key
    updates_queue.put({'type': 'list_update', 'data': new_scene})
    print(response_json)

def _delete_aesel_scene(general_api_wrapper, transaction_client, updates_queue):
    selected_key = general_api_wrapper.get_selected_scene()

    response_json = transaction_client.delete_scene(selected_key)
    print(response_json)

    updates_queue.put({'type': 'list_delete', 'data': selected_key})

def _find_aesel_scenes(transaction_client, updates_queue, key, name, tags):
    # Build a new Aesel scene
    scene_query = AeselScene()
    if key != "":
        scene_query.key = key
    if name != "":
        scene_query.name = name
    if tags != "":
        scene_query.tags = tags.split(",")

    # Send the Aesel request
    response_json = transaction_client.scene_query(scene_query)
    updates_queue.put({'type': 'list_set', 'data': response_json})
    print(response_json)

def _register_aesel_device(general_api_wrapper, transaction_client, updates_queue):
    addon_prefs = general_api_wrapper.get_addon_preferences()

    selected_key = general_api_wrapper.get_selected_scene()

    # Set the current Scene ID to the selected one
    general_api_wrapper.set_current_scene_id(selected_key)
    general_api_wrapper.set_current_scene_name(general_api_wrapper.get_selected_scene_name())

    # Build the user device for registration
    device = AeselUserDevice()
    device.key = addon_prefs.device_id
    device.hostname = addon_prefs.advertised_udp_host
    device.port = addon_prefs.udp_port

    # Send the registration request
    response_json = transaction_client.register(selected_key, device)
    print(response_json)

    # Get Assets related to the Scene
    scene_relationship_query = AeselAssetRelationship()
    scene_relationship_query.related = selected_key
    scene_relationship_query.type = "scene"
    scene_relation_response = transaction_client.query_asset_relationships(scene_relationship_query)

    # Download Scene Assets
    for asset in scene_relation_response:
        content = transaction_client.get_asset(asset["assetId"])

        # Save the asset to a file
        root_file_path = get_assets_file_path(general_api_wrapper.get_current_scene_name(),
                                              general_api_wrapper.get_executable_filepath(),
                                              addon_prefs.asset_file_location)
        filename = os.path.join(root_file_path, 'asset-%s.blend' % asset["assetId"])
        with open(filename, 'wb') as asset_file:
            asset_file.write(content)

        # Put the file path onto a queue to be imported on the main thread
        updates_queue.put({"filename": filename,
                           "type": "asset_import",
                           "relationship_type": asset["relationshipType"],
                           "relationship_subtype": asset["relationshipSubtype"],
                           "assetId": asset["assetId"],
                           "assetSubId": asset["assetSubId"],
                           "relatedId": asset["relatedId"]})

    # Download Objects
    obj_query = AeselObject()
    obj_query.scene = selected_key
    object_response_json = transaction_client.object_query(selected_key, obj_query)
    print(object_response_json)

    for record in object_response_json['objects']:

        # Find Assets related to the object
        obj_relationship_query = AeselAssetRelationship()
        obj_relationship_query.related = record["key"]
        obj_relationship_query.type = "object"
        obj_relation_result = transaction_client.query_asset_relationships(obj_relationship_query)

        # Download Object Assets
        for asset in obj_relation_result:
            content = transaction_client.get_asset(asset["assetId"])

            # Save the asset to a file
            root_file_path = get_assets_file_path(general_api_wrapper.get_current_scene_name(),
                                                  general_api_wrapper.get_executable_filepath(),
                                                  addon_prefs.asset_file_location)
            filename = os.path.join(root_file_path, 'asset-%s.blend' % asset["assetId"])
            with open(filename, 'wb') as asset_file:
                asset_file.write(content)

            # Put the file path onto a queue to be imported on the main thread
            updates_queue.put({"filename": filename,
                               "name": record["name"],
                               "key": record["key"],
                               "transform": record["transform"],
                               "type": "asset_import",
                               "relationship_type": asset["relationshipType"],
                               "relationship_subtype": asset["relationshipSubtype"],
                               "assetId": asset["assetId"],
                               "assetSubId": asset["assetSubId"],
                               "relatedId": asset["relatedId"]})

def _deregister_aesel_device(general_api_wrapper, transaction_client, updates_queue):
    addon_prefs = general_api_wrapper.get_addon_preferences()
    scene_id = general_api_wrapper.get_current_scene_id()
    general_api_wrapper.set_current_scene_id("")
    general_api_wrapper.set_current_scene_name("")

    # execute a request to Aesel
    response_json = transaction_client.deregister(scene_id, addon_prefs.device_id)
    print(response_json)

    # Queue a message to clear the viewport of objects on the main thread
    updates_queue.put({'type': 'viewport_clear'})

def _save_scene_asset(general_api_wrapper, portation_api_wrapper, transaction_client, asset_name, asset_public):
    # Get the scene to save the asset against
    scene_key = general_api_wrapper.get_selected_scene()
    if general_api_wrapper.get_current_scene_id() is not None and general_api_wrapper.get_current_scene_id() != '':
        scene_key = general_api_wrapper.get_current_scene_id()

    # Post the file to Aesel
    new_key = save_selected_as_obj_asset(general_api_wrapper, portation_api_wrapper, transaction_client, asset_name, asset_public)
    print("Exported New Asset with Key %s" % new_key)

    # Post a new Asset Relationship
    new_relation = AeselAssetRelationship()
    new_relation.asset = new_key
    new_relation.type = "scene"
    new_relation.related = scene_key
    response_json = transaction_client.save_asset_relationship(new_relation)

    print(response_json)
