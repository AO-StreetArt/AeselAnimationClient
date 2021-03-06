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
import pytest

from ..animation_client.asset_file_mgmt import get_assets_file_path

def test_base_file_finder():
    path1 = get_assets_file_path("testScene", "test1", ".")
    assert(path1 == os.path.relpath("test1/testScene"))
    assert(os.path.exists(os.path.relpath("test1/testScene")))

    path2 = get_assets_file_path("testScene", "test2", "test3")
    assert(path2 == os.path.relpath("test3/testScene"))
    assert(os.path.exists(os.path.relpath("test3/testScene")))

    os.rmdir(path1)
    os.rmdir(path2)
    os.rmdir("test1")
    os.rmdir("test3")
