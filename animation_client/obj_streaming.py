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

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

from aesel.model.AeselObject import AeselObject

import base64
import json
import socket

# Listen for updates from Aesel
def listen_for_object_updates(general_api_wrapper, updates_queue):
    addon_prefs = general_api_wrapper.get_addon_preferences()
    server_address = (addon_prefs.udp_host, addon_prefs.udp_port)
    print('Opening UDP Port: %s :: %s' % server_address)
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # AES-256-cbc Decryption
    cipher_backend = default_backend()
    enc_key = bytes(bytearray.fromhex(addon_prefs.aesel_udp_decryption_key))
    enc_iv = bytes(bytearray.fromhex(addon_prefs.aesel_udp_decryption_iv))
    cipher = Cipher(algorithms.AES(enc_key), modes.CBC(enc_iv), backend=cipher_backend)

    # Bind the socket to the port
    sock.bind(server_address)
    while(general_api_wrapper.is_udp_listener_active()):
        # Recieve a message from Aesel
        data, address = sock.recvfrom(8192)
        print(data)
        data_str = None
        if data:
            # Decode the recieved data, and decrypt if necessary
            print(base64.b64decode(data))
            if addon_prefs.udp_encryption_active:
                decryptor = cipher.decryptor()
                decrypted_bytes = decryptor.update(base64.b64decode(data)) + decryptor.finalize()
                data_str = decrypted_bytes.decode("utf-8")
                data_str = data_str[0:data_str.rfind('}')+1]
                # data_str = base64.b64decode(decrypted_bytes)
            else:
                data_str = data.decode("utf-8")
            print("Recieved data %s" % data_str)

            # Parse the data and drop it onto a queue for processing
            data_dict = json.loads(data_str)
            data_dict["type"] = "live_update"
            updates_queue.put(data_dict)
    print("Not listening on UDP port anymore")

def send_object_updates(general_api_wrapper, object_api_wrapper, event_client, updates_queue):
    if general_api_wrapper.is_udp_sender_active():
        addon_prefs = general_api_wrapper.get_addon_preferences()
        for elt in object_api_wrapper.iterate_over_live_objects():
            obj = object_api_wrapper.get_object_by_name(elt[1])
            print("Sending UDP update for object %s" % elt[1])
            aesel_obj = AeselObject()
            aesel_obj.key = elt[0]
            aesel_obj.name = elt[1]
            aesel_obj.scene = general_api_wrapper.get_current_scene_id()
            aesel_obj.transform = [obj.get_transform()[0][0], obj.get_transform()[0][1],
                                   obj.get_transform()[0][2], obj.get_transform()[0][3],
                                   obj.get_transform()[1][0], obj.get_transform()[1][1],
                                   obj.get_transform()[1][2], obj.get_transform()[1][3],
                                   obj.get_transform()[2][0], obj.get_transform()[2][1],
                                   obj.get_transform()[2][2], obj.get_transform()[2][3],
                                   obj.get_transform()[3][0], obj.get_transform()[3][1],
                                   obj.get_transform()[3][2], obj.get_transform()[3][3]]
            # Send the actual message
            event_client.send_object_update(aesel_obj)
    # Return 1 / (updates per second) for the blender timer api
    return 1.0 / addon_prefs.update_rate
