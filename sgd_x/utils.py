# coding=utf-8
# Copyright 2021 The Google Research Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Utility functions for editing schemas and dialogues."""

import json
import os
from typing import Any, Dict, List

from absl import logging
from tensorflow.io import gfile

DialoguesDict = Dict[str, Any]
Schemas = List[Any]


def load_schemas_to_dict(data_dir: str, subdir: str,
                         output_dict: Dict[str, Schemas]) -> None:
  """Load schema json from a given subdir into a provided dict."""
  schema_file_path = os.path.join(data_dir, subdir, "schema.json")
  with gfile.GFile(schema_file_path) as f:
    output_dict[subdir] = json.load(f)
    logging.info("Loaded schema file %s", schema_file_path)


def load_dialogues_to_dict(data_dir: str, subdir: str,
                           output_dict: Dict[str, DialoguesDict]) -> None:
  """Load dialogue jsons from a given subdir into a provided dict."""
  dialogue_files = gfile.glob(os.path.join(data_dir, subdir, "dialogues*.json"))
  for dialogue_file_path in dialogue_files:
    dialogue_filename = os.path.basename(dialogue_file_path)
    with gfile.GFile(dialogue_file_path) as f:
      output_dict[subdir][dialogue_filename] = json.load(f)
    logging.info("Loaded dialogue file %s", dialogue_file_path)


def replace_list_elements_with_mapping(elem_list: List[Any],
                                       mapping: Dict[Any, Any]) -> None:
  """Replace elements in a list in-place based on a mapping."""
  for idx, elem in enumerate(elem_list):
    if elem in mapping:
      elem_list[idx] = mapping[elem]


def replace_dict_keys_with_mapping(d: Dict[Any, Any],
                                   mapping: Dict[Any, Any]) -> None:
  """Replace dictionary keys in-place based on a mapping."""
  keys = list(d.keys())
  values = [d.pop(k) for k in keys]
  for k, v in zip(keys, values):
    if k in mapping:
      k = mapping[k]
    d[k] = v


def replace_dict_value_with_mapping(d: Dict[Any, Any], key: Any,
                                    mapping: Dict[Any, Any]) -> None:
  """Replace dictionary value associated with key based on mapping, in-place."""
  if d[key] in mapping:
    d[key] = mapping[d[key]]


def write_dialogue_dir(data_dir: str, subdir: str,
                       output_dict: Dict[str, DialoguesDict]) -> None:
  """Write dialogues from json object into files."""
  destination_dir = os.path.join(data_dir, subdir)
  gfile.makedirs(destination_dir)
  for dialogue_filename in output_dict[subdir]:
    dialogue_file = os.path.join(destination_dir, dialogue_filename)
    with gfile.GFile(dialogue_file, "w") as output_dialogue_file:
      json.dump(
          output_dict[subdir][dialogue_filename],
          output_dialogue_file,
          indent=2,
          separators=(",", ": "),
          sort_keys=True)
      logging.info("Wrote dialogue file %s", dialogue_file)


def write_schema_dir(data_dir: str, subdir: str,
                     output_dict: Dict[str, Any]) -> None:
  """Write schemas from json object into files."""
  destination_dir = os.path.join(data_dir, subdir)
  gfile.makedirs(destination_dir)
  schema_file = os.path.join(destination_dir, "schema.json")
  with gfile.GFile(schema_file, "w") as output_schema_file:
    json.dump(
        output_dict[subdir],
        output_schema_file,
        indent=2,
        separators=(",", ": "),
        sort_keys=True)
    logging.info("Wrote schema file %s", schema_file)
