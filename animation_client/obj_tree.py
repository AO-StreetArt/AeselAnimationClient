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

class Obj3dNode(object):
    # Allows for representing Aesel objects in a tree structure
    def __init__(self, aesel_obj):
        self.obj_ref = aesel_obj
        self.children = []

    def iter_children(self):
        for child in self.children:
            yield child

# Recursively look for a parent in an existing tree and attempt an insertion
def _insert_into_tree_if_parent_found(obj, parent):
    if obj['parent'] == parent.obj_ref['name']:
        parent.children.append(Obj3dNode(obj))
        return True
    else:
        for child in parent.iter_children():
            if _insert_into_tree_if_parent_found(obj, child):
                return True
        return False

# Convert a list of aesel objects into a tree of nodes which can be walked
def _object_list_to_tree(obj_list):
    # Start by getting root nodes that don't have any parents
    root_node_list = []
    remaining_objects_list = []
    for aesel_obj in obj_list:
        if aesel_obj['parent'] == "":
            root_node_list.append(Obj3dNode(aesel_obj))
        else:
            remaining_objects_list.append(aesel_obj)

    # Keep trying to add elements to the trees until we have none left
    while(len(remaining_objects_list) > 0):
        parents_found_in_iteration = 0
        tmp_remaining_objects_list = []
        for aesel_obj in remaining_objects_list:
            for existing_root in root_node_list:
                if not _insert_into_tree_if_parent_found(aesel_obj, existing_root):
                    tmp_remaining_objects_list.append(aesel_obj)
                else:
                    parents_found_in_iteration += 1
        remaining_objects_list = tmp_remaining_objects_list

        # Detect tree generation errors (if the parent entry in the objects
        # from Aesel don't have a match in the scene)
        if parents_found_in_iteration == 0:
            print("Unable to fully generate object tree")
            for obj in remaining_objects_list:
                print("Unable to find parent for object %s" % obj.name)
            break

    return root_node_list
