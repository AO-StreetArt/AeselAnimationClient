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

class AddonPreferences(object):
    aesel_addr = None
    aesel_udp_host = None
    aesel_udp_port = None
    udp_encryption_active = None
    aesel_udp_decryption_key = None
    aesel_udp_decryption_iv = None
    aesel_udp_encryption_key = None
    aesel_udp_encryption_iv = None
    device_id = None
    udp_host = None
    advertised_udp_host = None
    udp_port = None
    update_rate = None
    asset_file_type = None
    asset_file_location = None
    enable_bg_schedulers = None

class GeneralApiWrapper(object):
    get_addon_preferences = None
    get_executable_filepath = None
    get_current_scene_id = None
    set_current_scene_id = None
    get_current_scene_name = None
    set_current_scene_name = None
    get_selected_scene = None
    get_selected_scene_name = None
    add_to_scenes_ui_list = None
    update_scenes_ui_list = None
    remove_from_scenes_ui_list = None
    clear_scenes_ui_list = None
    is_udp_listener_active = None
    set_udp_listener_active = None
    is_udp_sender_active = None
    set_udp_sender_active = None
