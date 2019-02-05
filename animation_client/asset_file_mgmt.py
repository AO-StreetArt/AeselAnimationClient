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

# Get the root file path for assets
def get_assets_file_path(current_scene_name, executable_folder, base_folder):
    # Get the base file path
    base_file_path = None
    if base_folder == ".":
        base_file_path = os.path.relpath(executable_folder)
    else:
        base_file_path = os.path.relpath(base_folder)

    # Join the base file path with the scene
    if current_scene_name != "":
        target = os.path.join(base_file_path, current_scene_name)
    else:
        target = os.path.join(base_file_path, "default")

    # If the target directory doesn't exist, create it
    if not os.path.exists(target):
        os.makedirs(target)

    # Return the target directory
    return target
