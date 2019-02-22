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
    def __init__(self, name, props, is_selected, location, erotation, scale, transform, parent, type):
        self._name = name
        self._properties = props
        self._is_selected = is_selected
        self._location = location
        self._erotation = erotation
        self._scale = scale
        self._transform = transform
        self._parent = parent
        self._type = type

    def get_type(self):
        return self._type

    def set_type(self, new_type):
        self._type = new_type

    def get_parent(self):
        return self._parent

    def set_parent(self, new_parent):
        self._parent = new_parent

    def get_name(self):
        return self._name

    def set_name(self, new_name):
        self._name = new_name

    def get_property(self, prop_name):
        return self._properties[prop_name]

    def set_property(self, prop_name, prop_val):
        self._properties[prop_name] = prop_val

    def set_selection(self, selection):
        self._is_selected = selection

    def selected(self):
        return self._is_selected

    def get_location_x(self):
        return self._location[0]

    def set_location_x(self, new_loc):
        self._location[0] = new_loc

    def get_location_y(self):
        return self._location[1]

    def set_location_y(self, new_loc):
        self._location[1] = new_loc

    def get_location_z(self):
        return self._location[2]

    def set_location_z(self, new_loc):
        self._location[2] = new_loc

    def get_erotation_x(self):
        return self._erotation[0]

    def set_erotation_x(self, new_rot):
        self._erotation[0] = new_rot

    def get_erotation_y(self):
        return self._erotation[1]

    def set_erotation_y(self, new_rot):
        self._erotation[1] = new_rot

    def get_erotation_z(self):
        return self._erotation[2]

    def set_erotation_z(self, new_rot):
        self._erotation[2] = new_rot

    def get_scale_x(self):
        return self._scale[0]

    def set_scale_x(self, new_scl):
        self._scale[0] = new_scl

    def get_scale_y(self):
        return self._scale[1]

    def set_scale_y(self, new_scl):
        self._scale[1] = new_scl

    def get_scale_z(self):
        return self._scale[2]

    def set_scale_z(self, new_scl):
        self._scale[2] = new_scl

    def set_transform(self, transform):
        self._transform = transform

    def get_transform(self):
        return self._transform


class ObjectApiWrapper(object):
    get_active_object = None
    get_object_by_name = None
    delete_selected_objects = None
    iterate_over_all_objects = None
    add_live_object = None
    remove_live_object = None
    iterate_over_live_objects = None
    iterate_over_selected_objects = None
