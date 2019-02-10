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

from aesel.model.AeselAssetMetadata import AeselAssetMetadata

# Imports

def import_obj_asset(object_api_wrapper, portation_api_wrapper, ops):
    # Import the obj file using the built-in operator
    portation_api_wrapper.import_obj_file(ops["filename"])
    imported_blender_object = object_api_wrapper.get_active_object()

    print('Imported Name %s' % imported_blender_object.get_name())

    # Update object attributes
    if "name" in ops:
        imported_blender_object.set_name(ops["name"])
    if "key" in ops:
        imported_blender_object.set_property("key", ops["key"])

    # Apply object transforms
    if "transform" in ops:
        imported_blender_object.set_transform(ops["transform"])

def import_blend_asset(portation_api_wrapper, ops):
    filename = ops["filename"]
    data_name = None
    if "dataname" in ops:
        data_name = ops["dataname"]

    # Load the data from the blend file
    portation_api_wrapper.import_blend_file(filename, data_name)

# Exports
# Generate an instance of asset metadata to save
def gen_asset_metadata(name, file_type, public):
    metadata = AeselAssetMetadata()
    metadata.name = name
    metadata.asset_type = "Blender"
    metadata.content_type = "text/plain"
    metadata.file_type = file_type
    metadata.isPublic = public
    return metadata

# Save the full current scene in Blender to Aesel as an asset
def save_scene_as_blend_asset(general_api_wrapper,
                              portation_api_wrapper,
                              transaction_client,
                              name,
                              public):
    addon_prefs = general_api_wrapper.get_addon_preferences()
    
    # Create the Asset Metadata
    metadata = gen_asset_metadata(name, "blend", public)

    # Determine the base path to save to
    root_file_path = get_assets_file_path(general_api_wrapper.get_current_scene_name(),
                                          general_api_wrapper.get_executable_filepath(),
                                          addon_prefs.asset_file_location)

    # Export the blender object to a blend file
    target_file = os.path.join(root_file_path, name + '.blend')
    portation_api_wrapper.export_blend_file(target_file)

    # Post the file to Aesel
    return transaction_client.create_asset(target_file, metadata)

# Export the selected objects as a .obj Asset
# The resulting file name should be 'new_key.obj'
def save_selected_as_obj_asset(general_api_wrapper,
                               portation_api_wrapper,
                               transaction_client,
                               name,
                               public,
                               export_file=True,
                               post_asset=True):
    addon_prefs = general_api_wrapper.get_addon_preferences()
    # Create the Asset Metadata
    metadata = gen_asset_metadata(name, "obj", public)

    # Determine the base path to save to
    root_file_path = get_assets_file_path(general_api_wrapper.get_current_scene_name(),
                                          general_api_wrapper.get_executable_filepath(),
                                          addon_prefs.asset_file_location)

    # Export the blender object to an Obj file
    target_file = os.path.join(root_file_path, name + '.obj')
    if export_file:
        portation_api_wrapper.export_obj_file(target_file)

    # Post the file to Aesel
    new_asset_key = None
    if post_asset:
        new_asset_key = transaction_client.create_asset(target_file, metadata)
        print("Exported New Asset with Key %s" % new_asset_key)

    return new_asset_key
