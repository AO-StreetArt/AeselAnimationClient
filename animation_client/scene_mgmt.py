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

from .obj_tree import Obj3dNode, _object_list_to_tree
from .asset_file_mgmt import get_assets_file_path
from .asset_mgmt import save_selected_as_obj_asset, save_scene_as_blend_asset

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

def _shrink_relationship_response(scene_relation_response):
    # We will get back multiple relationships, one for each object within
    # the blend file to import.  We want to shrink this down so that we have
    # One entry in the list for each asset, with multiple names for each one
    asset_map = []
    asset_list = []
    for asset in scene_relation_response:
        match_found = False
        for processed_asset in asset_map:
            if processed_asset["assetId"] == asset["assetId"]:
                match_found = True
                processed_asset["dataMap"].append(asset)
                break
        if not match_found:
            new_map_entry = {"assetId": asset["assetId"],
                             "dataMap": [asset]}
            asset_list.append(asset["assetId"])
            asset_map.append(new_map_entry)
    return asset_map, asset_list

def _save_asset_to_disk(asset_id, file_type, content, root_file_path):
    # Find the path we're saving to
    filename = os.path.join(root_file_path, 'asset-%s.%s' % (asset_id, file_type))

    # If a duplicate is found on disk, remove before downloading the rest
    if os.path.isfile(filename):
        os.remove(filename)

    # Write the asset content to file
    with open(filename, 'wb') as asset_file:
        asset_file.write(content)

    return filename

def _add_metadata_to_asset_map(metadata_list, asset_map):
    for asset in asset_map:
        for metadata in metadata_list:
            if asset["assetId"] == metadata["key"]:
                asset["fileType"] = metadata["fileType"]
                break

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

    # We will get back multiple relationships, one for each object within
    # the blend file to import.  We want to shrink this down so that we have
    # One entry in the list for each asset, with multiple names for each one
    asset_map, asset_list = _shrink_relationship_response(scene_relation_response)

    # Now, get the asset metadata for the assets we need to download
    metadata_response = transaction_client.bulk_query_asset_metadata(asset_list)
    _add_metadata_to_asset_map(metadata_response, asset_map)

    root_file_path = get_assets_file_path(general_api_wrapper.get_current_scene_name(),
                                          general_api_wrapper.get_executable_filepath(),
                                          addon_prefs.asset_file_location)

    # Download Scene Assets
    for asset in asset_map:
        content = transaction_client.get_asset(asset["assetId"])

        # Save the asset to a file
        filename = _save_asset_to_disk(asset["assetId"],
                                       asset["fileType"],
                                       content,
                                       root_file_path)

        # Put the file path onto a queue to be imported on the main thread
        updates_queue.put({"filename": filename,
                           "type": "asset_import",
                           "assetId": asset["assetId"],
                           "dataMap": asset["dataMap"],
                           "scene": selected_key,
                           "collection": "scene"})

    # Download Objects
    obj_query = AeselObject()
    obj_query.scene = selected_key
    object_response_json = transaction_client.object_query(selected_key, obj_query)
    print(object_response_json)

    # Start by building a map of all the assets we need to download, as
    # multiple objects can be associated to the same asset.
    asset_map = []
    asset_list = []
    for record in object_response_json['objects']:

        # Find Assets related to the object
        obj_relationship_query = AeselAssetRelationship()
        obj_relationship_query.related = record["key"]
        obj_relationship_query.type = "object"
        obj_relation_result = transaction_client.query_asset_relationships(obj_relationship_query)

        existing_asset_found = False
        for entry in asset_map:
            if obj_relation_result[0]["assetId"] == entry["assetId"]:
                # Existing asset file found
                data_map = obj_relation_result[0]
                data_map["name"] = record["name"]
                data_map["key"] = record["key"]
                data_map["parent"] = record["parent"]
                data_map["transform"] = record["transform"]
                entry["dataMap"].append(data_map)
                existing_asset_found = True

        if not existing_asset_found:
            data_map = obj_relation_result[0]
            data_map["name"] = record["name"]
            data_map["key"] = record["key"]
            data_map["parent"] = record["parent"]
            data_map["transform"] = record["transform"]
            asset_map.append({"assetId": obj_relation_result[0]["assetId"],
                              "dataMap": [data_map]})
            asset_list.append(obj_relation_result[0]["assetId"])

    # Now, get the asset metadata for the assets we need to download
    metadata_response = transaction_client.bulk_query_asset_metadata(asset_list)
    _add_metadata_to_asset_map(metadata_response, asset_map)

    # Download Object Assets
    for asset in asset_map:
        content = transaction_client.get_asset(asset["assetId"])

        # Save the asset to a file
        filename = _save_asset_to_disk(asset["assetId"],
                                       asset["fileType"],
                                       content,
                                       root_file_path)

        # Put the file path onto a queue to be imported on the main thread
        updates_queue.put({"filename": filename,
                           "type": "asset_import",
                           "assetId": asset["assetId"],
                           "dataMap": asset["dataMap"],
                           "collection": "object"})

    # Put an update on the queue after all files have been imported
    # to create parent-child links in blender from the imported data
    object_tree = _object_list_to_tree(object_response_json['objects'])
    updates_queue.put({"type": "parent_updates", "objectTree": object_tree})

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

def _save_scene_asset(general_api_wrapper, object_api_wrapper, portation_api_wrapper, transaction_client, asset_name, asset_public):
    addon_prefs = general_api_wrapper.get_addon_preferences()
    # Get the scene to save the asset against
    scene_key = general_api_wrapper.get_selected_scene()
    if general_api_wrapper.get_current_scene_id() is not None and general_api_wrapper.get_current_scene_id() != '':
        scene_key = general_api_wrapper.get_current_scene_id()

    # Post the file to Aesel
    new_key = None
    if addon_prefs.asset_file_type == "obj":
        new_key = save_selected_as_obj_asset(general_api_wrapper,
                                             portation_api_wrapper,
                                             transaction_client,
                                             asset_name,
                                             asset_public)
        # Post a single asset relationship to the obj asset
        new_relation = AeselAssetRelationship()
        new_relation.asset = new_key
        new_relation.asset_sub_id = ""
        new_relation.type = "scene"
        new_relation.subtype = "object"
        new_relation.related = scene_key
        response_json = transaction_client.save_asset_relationship(new_relation)
        print(response_json)
    else:
        new_key = save_scene_as_blend_asset(general_api_wrapper,
                                      portation_api_wrapper,
                                      transaction_client,
                                      asset_name,
                                      asset_public)

        # Post a new Asset Relationship for each selected object
        for selected_obj in object_api_wrapper.iterate_over_selected_objects():
            new_relation = AeselAssetRelationship()
            new_relation.asset = new_key
            new_relation.asset_sub_id = selected_obj.get_name()
            new_relation.type = "scene"
            new_relation.subtype = "object"
            new_relation.related = scene_key
            response_json = transaction_client.save_asset_relationship(new_relation)
            print(response_json)

    print("Exported New Asset with Key %s" % new_key)
