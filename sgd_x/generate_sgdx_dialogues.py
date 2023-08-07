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
"""Generate SGD-X dialogues from variant schemas.

Example usage: From the `.../dstc8-schema-guided-dialogue/` directory, run
  `python3 -m sgd_x.generate_sgdx_dialogues`
"""

import collections
import copy
import os
from typing import Dict, Sequence, Tuple

from absl import app
from absl import flags
from sgd_x import utils
from tensorflow.io import gfile

_ORIGINAL_DATA_DIR = flags.DEFINE_string(
    'original_data_dir', './', 'Path to directory of Original SGD data.')
_VARIANT_DATA_DIR = flags.DEFINE_string('variant_data_dir', './sgd_x/data',
                                        'Path to directory of SGD-X schemas.')
_OUTPUT_DATA_DIR = flags.DEFINE_string(
    'output_data_dir', './sgd_x/data',
    'Output directory for SGD-X dialogues and schemas.')

_DATASET_SPLITS = ['train', 'dev', 'test']
_SGDX_VARIANTS = ['v1', 'v2', 'v3', 'v4', 'v5']

SourceToTarget = Dict[str, str]


def create_schema_name_map(
    source_subdir_to_schemas: Dict[str, utils.Schemas],
    target_subdir_to_schemas: Dict[str, utils.Schemas]
) -> Tuple[SourceToTarget, Dict[str, SourceToTarget], Dict[str,
                                                           SourceToTarget]]:
  """Create mapping from source to target schema element names."""
  service_to_name = {}
  service_slot_to_name = collections.defaultdict(dict)
  service_intent_to_name = collections.defaultdict(dict)

  # Note: this relies on schema order between source and target matching.
  for subdir in source_subdir_to_schemas:
    for idx, source_schema in enumerate(source_subdir_to_schemas[subdir]):
      target_schema = target_subdir_to_schemas[subdir][idx]
      service = source_schema['service_name']

      # Skip processing if schema has already been processed.
      if service in service_to_name:
        continue

      # Service name.
      service_to_name[service] = target_schema['service_name']

      # Slot names.
      for s_idx, slot in enumerate(source_schema['slots']):
        service_slot_to_name[service][
            slot['name']] = target_schema['slots'][s_idx]['name']

      # Intent names.
      for i_idx, intent in enumerate(source_schema['intents']):
        service_intent_to_name[service][
            intent['name']] = target_schema['intents'][i_idx]['name']

  return service_to_name, service_slot_to_name, service_intent_to_name


def create_modified_dialogues(
    subdir_to_dialogues: Dict[str, utils.DialoguesDict],
    service_to_name: SourceToTarget, service_slot_to_name: Dict[str,
                                                                SourceToTarget],
    service_intent_to_name: Dict[str, SourceToTarget]
) -> Dict[str, utils.DialoguesDict]:
  """Update annotations in dialogues to use new schema element names."""
  new_subdir_to_dialogues = copy.deepcopy(subdir_to_dialogues)

  # Process dialogue JSON files and edit names.
  for filename_to_dialogues in new_subdir_to_dialogues.values():
    for dialogues in filename_to_dialogues.values():
      for dialogue in dialogues:
        services_list = dialogue['services']

        # Edit top-level services.
        utils.replace_list_elements_with_mapping(services_list, service_to_name)

        # Edit names within frames.
        for turn in dialogue['turns']:
          for frame in turn['frames']:
            # Convenience variables
            service_name = frame['service']
            slot_to_name = service_slot_to_name[service_name]
            intent_to_name = service_intent_to_name[service_name]

            # Edit service.
            utils.replace_dict_value_with_mapping(frame, 'service',
                                                  service_to_name)

            # Edit slots.
            for slot_with_positions in frame['slots']:
              utils.replace_dict_value_with_mapping(slot_with_positions, 'slot',
                                                    slot_to_name)

            # Edit state.
            if 'state' in frame:
              state_json = frame['state']
              utils.replace_dict_value_with_mapping(state_json, 'active_intent',
                                                    intent_to_name)
              utils.replace_list_elements_with_mapping(
                  state_json['requested_slots'], slot_to_name)
              utils.replace_dict_keys_with_mapping(state_json['slot_values'],
                                                   slot_to_name)

            # Edit actions.
            for action in frame.get('actions', []):
              # Replace values if slot is intent.
              if 'slot' in action:
                if (
                    action['slot'] == 'intent'
                    # Don't process the slot named "intent" from Homes service.
                    and action['act'] in ['OFFER_INTENT', 'INFORM_INTENT']
                ):
                  utils.replace_list_elements_with_mapping(
                      action.get('canonical_values', []), intent_to_name)
                  utils.replace_list_elements_with_mapping(
                      action.get('values', []), intent_to_name)
                else:
                  utils.replace_dict_value_with_mapping(action, 'slot',
                                                        slot_to_name)

            # Edit service results.
            for service_result in frame.get('service_results', []):
              utils.replace_dict_keys_with_mapping(service_result, slot_to_name)

            # Edit service_call.
            if 'service_call' in frame:
              service_call_json = frame['service_call']
              utils.replace_dict_value_with_mapping(service_call_json, 'method',
                                                    intent_to_name)
              utils.replace_dict_keys_with_mapping(
                  service_call_json['parameters'], slot_to_name)

  return new_subdir_to_dialogues


def main(argv: Sequence[str]) -> None:
  if len(argv) > 1:
    raise app.UsageError('Too many command-line arguments.')

  # Load original schemas and dialogues.
  orig_subdir_to_schemas = {}
  orig_subdir_to_dialogues = collections.defaultdict(dict)
  for subdir in _DATASET_SPLITS:
    utils.load_schemas_to_dict(_ORIGINAL_DATA_DIR.value, subdir,
                               orig_subdir_to_schemas)
    utils.load_dialogues_to_dict(_ORIGINAL_DATA_DIR.value, subdir,
                                 orig_subdir_to_dialogues)

  # Loop through variant schemas and create matching dialogues.
  for var in _SGDX_VARIANTS:

    # Load variant schemas.
    var_subdir_to_schemas = {}
    for subdir in _DATASET_SPLITS:
      utils.load_schemas_to_dict(
          os.path.join(_VARIANT_DATA_DIR.value, var), subdir,
          var_subdir_to_schemas)

    # Create mappings from original to variant schema element names.
    (service_to_name, service_slot_to_name,
     service_intent_to_name) = create_schema_name_map(orig_subdir_to_schemas,
                                                      var_subdir_to_schemas)

    # Create modified dialogues that use variant schema elements.
    var_subdir_to_dialogues = create_modified_dialogues(
        orig_subdir_to_dialogues, service_to_name, service_slot_to_name,
        service_intent_to_name)

    # Write out modified dialogues and variant schema files.
    for subdir in _DATASET_SPLITS:
      var_output_dir = os.path.join(_OUTPUT_DATA_DIR.value, var)

      # Make directory if not exists.
      gfile.makedirs(os.path.join(var_output_dir, subdir))

      # Copy over schema file if not exists.
      var_schema_path = os.path.join(var_output_dir, subdir, 'schema.json')
      if not gfile.exists(var_schema_path):
        gfile.copy(
            os.path.join(_VARIANT_DATA_DIR.value, var, subdir, 'schema.json'),
            var_schema_path,
            overwrite=False)

      # Write out dialogue files.
      utils.write_dialogue_dir(var_output_dir, subdir, var_subdir_to_dialogues)


if __name__ == '__main__':
  flags.mark_flag_as_required('original_data_dir')
  flags.mark_flag_as_required('variant_data_dir')
  flags.mark_flag_as_required('output_data_dir')
  app.run(main)
