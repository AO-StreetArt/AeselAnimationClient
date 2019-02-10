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

class Object3dInterface(object):
    def __init__(self, name, props, is_selected, location, erotation, scale, transform):
        self.name = name
        self.properties = props
        self.is_selected = is_selected
        self.location = location
        self.erotation = erotation
        self.scale = scale
        self.transform = transform

    def get_name(self):
        return self.name

    def set_name(self, new_name):
        self.name = new_name

    def get_property(self, prop_name):
        return self.properties[prop_name]

    def set_property(self, prop_name, prop_val):
        self.properties[prop_name] = prop_val

    def set_selection(self, selection):
        self.is_selected = selection

    def selected(self):
        return self.is_selected

    def get_location_x(self):
        return self.location[0]

    def set_location_x(self, new_loc):
        self.location[0] = new_loc

    def get_location_y(self):
        return self.location[1]

    def set_location_y(self, new_loc):
        self.location[1] = new_loc

    def get_location_z(self):
        return self.location[2]

    def set_location_z(self, new_loc):
        self.location[2] = new_loc

    def get_erotation_x(self):
        return self.erotation[0]

    def set_erotation_x(self, new_rot):
        self.erotation[0] = new_rot

    def get_erotation_y(self):
        return self.erotation[1]

    def set_erotation_y(self, new_rot):
        self.erotation[1] = new_rot

    def get_erotation_z(self):
        return self.erotation[2]

    def set_erotation_z(self, new_rot):
        self.erotation[2] = new_rot

    def get_scale_x(self):
        return self.scale[0]

    def set_scale_x(self, new_scl):
        self.scale[0] = new_scl

    def get_scale_y(self):
        return self.scale[1]

    def set_scale_y(self, new_scl):
        self.scale[1] = new_scl

    def get_scale_z(self):
        return self.scale[2]

    def set_scale_z(self, new_scl):
        self.scale[2] = new_scl

    def set_transform(self, transform):
        self.transform = transform

    def get_transform(self):
        return self.transform


class ObjectApiWrapper(object):
    get_active_object = None
    get_object_by_name = None
    delete_selected_objects = None
    iterate_over_all_objects = None
    add_live_object = None
    remove_live_object = None
    iterate_over_live_objects = None
