# The Schema-Guided Dialogue Dataset

**Contact -** schema-guided-dst@google.com

## Overview

The **Schema-Guided Dialogue (SGD)** dataset consists of over 20k annotated
multi-domain, task-oriented conversations between a human and a virtual
assistant. These conversations involve interactions with services and APIs
spanning 20 domains, such as banks, events, media, calendar, travel, and
weather. For most of these domains, the dataset contains multiple different
APIs, many of which have overlapping functionalities but different interfaces,
which reflects common real-world scenarios. The wide range of available
annotations can be used for intent prediction, slot filling, dialogue state
tracking, policy imitation learning, language generation, and user simulation
learning, among other tasks for developing large-scale virtual assistants.
Additionally, the dataset contains unseen domains and services in the evaluation
set to quantify the performance in zero-shot or few-shot settings.

**Schema-Guided Dialogue - eXtended (SGD-X)** is a benchmark for measuring the
robustness of dialogue systems to linguistic variations in schemas. SGD-X
extends the SGD dataset with 5 crowdsourced variants for every schema, where
variants are semantically similar yet stylistically diverse. Models trained on
SGD are evaluated on SGD-X to measure how well they can generalize in a
real-world setting, where a large variety of linguistic styles exist.

**The datasets are provided "AS IS" without any warranty, express or implied.
Google disclaims all liability for any damages, direct or indirect, resulting
from the use of this dataset.**

## Updates

**10/19/2021** - SGD-X schemas for measuring robustness to linguistic variations
in schemas released, along with a script to convert dialogue annotations
according to the new schemas.

**07/05/2020** - Test set annotations released. User actions and service calls
made during the dialogue are also released for all dialogues.

**10/14/2019** - DSTC8 challenge concluded. Details about the submissions to the
challenge may be found in the
[DSTC8 overview paper](https://arxiv.org/pdf/2002.01359.pdf).

**10/07/2019** - Test dataset released without the dialogue state annotations.

**07/23/2019** - Train and dev sets are publicly released as part of [DSTC8
challenge](dstc8.md).

## Important Links

*   [Paper - SGD dataset and DST baseline](https://arxiv.org/pdf/1909.05855.pdf)
*   [Paper - DSTC8 overview](https://arxiv.org/pdf/2002.01359.pdf)
*   [Paper - SGD-X](https://arxiv.org/pdf/2110.06800.pdf)
*   [Paper - Template-guided Text Generation](https://arxiv.org/pdf/2004.15006.pdf)
*   [Code - DST baseline](https://github.com/google-research/google-research/tree/master/schema_guided_dst)
*   [Blog - SGD dataset](https://ai.googleblog.com/2019/10/introducing-schema-guided-dialogue.html)

## Data

The SGD dataset consists of schemas outlining the interface of different APIs
and annotated dialogues. The dialogues were generated with the help of a
dialogue simulator and paid crowd-workers. The data collection approach is
summarized in this [paper](https://arxiv.org/pdf/1801.04871.pdf).

The SGD-X dataset consists of 5 linguistic variants of every schema in the
original SGD dataset. Linguistic variants were written by hundreds of paid
crowd-workers. In the SGD-X directory, `v1` represents the variant closest to
the original schemas and `v5` the farthest in terms of linguistic distance. To
evaluate model performance on SGD-X schemas, dialogues must be converted using
the script `generate_sgdx_dialogues.py`.

### Schema Representation

A service or API is essentially a set of functions (called intents), each taking
a set of parameters (called slots). A schema is a normalized representation of
the interface exposed by a service/API. In addition, the schema also includes
natural language descriptions of the included functions and their parameters to
outline the semantics of each element. The SGD schemas were manually generated
by the dataset creators, and SGD-X schema variants were created by having
crowd-workers paraphrase the original schemas. Each schema is represented as a
json object containing the following fields:

*   **service_name\*** - A unique name for the service.
*   **description** - A natural language description of the tasks supported by
    the service.
*   **slots** - A list of slots/attributes corresponding to the entities present
    in the service. Each slot contains the following fields:
    *   **name** - The name of the slot.
    *   **description** - A natural language description of the slot.
    *   **is_categorical** - A boolean value. If true, the slot has a fixed set
        of possible values.
    *   **possible_values** - List of possible values the slot can take on. If
        the slot is categorical, this lists all the possible values. If the slot
        not categorical, it is either an empty list or a small sample of all the
        values the slot can take on.
*   **intents** - The list of intents/tasks supported by the service. Each
    method contains the following fields:
    *   **name** - The name of the intent.
    *   **description** - A natural language description of the intent.
    *   **is_transactional** - A boolean value. If true, the underlying API call
        is transactional (e.g, a booking or a purchase), as opposed to a search
        call.
    *   **required_slots** - A list of slot names whose values must be provided
        before executing an API call.
    *   **optional_slots** - A dictionary mapping slot names to the default
        value taken by the slot. These slots are optionally specified by the
        user, and the user may override the default value. An empty default
        value allows that slot to take any value by default.
    *   **result_slots** - A list of slot names which are present in the results
        returned by a call to the service or API.

\*service_names follow the form "\<domain name\>\_\<number\>" (e.g. Banks_2).
The number is used to disambiguate services from the same domain. SGD-X variant
schemas have two-digit numbers, where the first digit is copied from the
original schema, and the second digit is the SGD-X variant number. For example,
the `v1` variant of Banks_2 is Banks_21.

### Dialogue Representation

Dialogues are represented as a list of turns, where each turn contains either a
user or system utterance. The annotations for a turn are grouped into frames,
where each frame corresponds to a single service. Each turn in the single domain
dataset contains exactly one frame. In multi-domain datasets, some turns may
have multiple frames.

Each dialogue is represented as a json object with the following fields:

*   **dialogue_id** - A unique identifier for a dialogue.
*   **services** - A list of services present in the dialogue.
*   **turns** - A list of annotated system or user utterances.

Each turn consists of the following fields:

*   **speaker** - The speaker for the turn. Possible values are "USER" or
    "SYSTEM".
*   **utterance** - A string containing the natural language utterance.
*   **frames** - A list of frames, where each frame contains annotations for a
    single service.

Each frame consists of the following fields:

*   **service** - The name of the service corresponding to the frame. The slots
    and intents used in the following fields are taken from the schema of this
    service.
*   **slots** - A list of slot spans in the utterance, only provided for
    non-categorical slots. Each slot span contains the following fields:
    *   **slot** - The name of the slot.
    *   **start** - The index of the starting character in the utterance
        corresponding to the slot value.
    *   **exclusive_end** - The index of the character just after the last
        character corresponding to the slot value in the utterance. In python,
        `utterance[start:exclusive_end]` gives the slot value.
*   **actions** - A list of actions corresponding to the system. Each action has
    the following fields:
    *   **act** - The type of action. The list of all possible system acts is
        given below.
    *   **slot** (optional) - A slot argument for some of the actions.
    *   **values** (optional) - A list of values assigned to the slot. If the
        values list is non-empty, then the slot must be present.
    *   **canonical_values** (optional) - The values in their canonicalized form
        as used by the service. It is a list of strings of the same length as
        values.
*   **service_call** (system turns only, optional) - The request sent to the
    service. It consists of the following fields:
    *   **method** - The name of the intent or function of the service or API
        being executed.
    *   **parameters** - A dictionary mapping slot name (all required slots and
        possibly some optional slots) to a value in its canonicalized form.
*   **service_results** (system turns only, optional) - A list of entities
    containing the results obtained from the service. It is only available for
    turns in which a service call is made. Each entity is represented as a
    dictionary mapping a slot name to a string containing its canonical value.
*   **state** (user turns only) - The dialogue state corresponding to the
    service. It consists of the following fields:
    *   **active_intent** - The intent corresponding to the service of the frame
        which is currently being fulfilled by the system. It takes the value
        "NONE" if none of the intents are active.
    *   **requested_slots** - A list of slots requested by the user in the
        current turn.
    *   **slot_values** - A dictionary mapping slot name to a list of strings.
        For categorical slots, this list contains a single value assigned to the
        slot. For non-categorical slots, all the values in this list are spoken
        variations of each other and are equivalent (e.g, "6 pm", "six in the
        evening", "evening at 6" etc.).

List of possible system acts:

*   **INFORM** - Inform the value for a slot to the user. The slot and values
    fields in the corresponding action are always non-empty.
*   **REQUEST** - Request the value of a slot from the user. The corresponding
    action always contains a slot, but values are optional. When values are
    present, they are used as examples for the user e.g, "Would you like to eat
    indian or chinese food or something else?"
*   **CONFIRM** - Confirm the value of a slot before making a transactional
    service call.
*   **OFFER** - Offer a certain value for a slot to the user. The corresponding
    action always contains a slot and a list of values for that slot offered to
    the user.
*   **NOTIFY_SUCCESS** - Inform the user that their request was successful. Slot
    and values are always empty in the corresponding action.
*   **NOTIFY_FAILURE** - Inform the user that their request failed. Slot and
    values are always empty in the corresponding action.
*   **INFORM_COUNT** - Inform the number of items found that satisfy the user's
    request. The corresponding action always has "count" as the slot, and a
    single element in values for the number of results obtained by the system.
*   **OFFER_INTENT** - Offer a new intent to the user. Eg, "Would you like to
    reserve a table?". The corresponding action always has "intent" as the slot,
    and a single value containing the intent being offered. The offered intent
    belongs to the service corresponding to the frame.
*   **REQ_MORE** - Asking the user if they need anything else. Slot and values
    are always empty in the corresponding action.
*   **GOODBYE** - End the dialogue. Slot and values are always empty in the
    corresponding action.

List of possible user acts:

*   **INFORM_INTENT** - Express the desire to perform a certain task to the
    system. The action always has "intent" as the slot and a single value
    containing the intent being informed.
*   **NEGATE_INTENT** - Negate the intent which has been offered by the system.
*   **AFFIRM_INTENT** - Agree to the intent which has been offered by the
    system.
*   **INFORM** - Inform the value of a slot to the system. The slot and values
    fields in the corresponding action are always non-empty.
*   **REQUEST** - Request the value of a slot from the system. The corresponding
    action always contains a slot parameter. It may optionally contain a value,
    in which case, the user asks the system if the slot has the specified value.
*   **AFFIRM** - Agree to the system's proposition. Slot and values are always
    empty.
*   **NEGATE** - Deny the system's proposal. Slot and values are always empty.
*   **SELECT** - Select a result being offered by the system. The corresponding
    action may either contain no parameters, in which case all the values
    proposed by the system are being accepted, or it may contain a slot and
    value parameters, in which case the specified slot and value are being
    accepted.
*   **REQUEST_ALTS** - Ask for more results besides the ones offered by the
    system. Slot and values are always empty.
*   **THANK_YOU** - Thank the system. Slot and values are always empty.
*   **GOODBYE** - End the dialogue. Slot and values are always empty.


## License

The SGD and SGD-X datasets are released under
[**CC BY-SA 4.0**](https://creativecommons.org/licenses/by-sa/4.0/) license. For
the full license, see [LICENSE.txt](LICENSE.txt). Please cite the following
papers if you use the datasets in your work:

**SGD**

```shell
@inproceedings{rastogi2020towards,
  title={Towards scalable multi-domain conversational agents: The schema-guided dialogue dataset},
  author={Rastogi, Abhinav and Zang, Xiaoxue and Sunkara, Srinivas and Gupta, Raghav and Khaitan, Pranav},
  booktitle={Proceedings of the AAAI Conference on Artificial Intelligence},
  volume={34},
  number={05},
  pages={8689--8696},
  year={2020}
}
```

**SGD-X**

```shell
@inproceedings{lee2022sgd,
  title={SGD-X: A Benchmark for Robust Generalization in Schema-Guided Dialogue Systems},
  author={Lee, Harrison and Gupta, Raghav and Rastogi, Abhinav and Cao, Yuan and Zhang, Bin and Wu, Yonghui},
  booktitle={Proceedings of the AAAI Conference on Artificial Intelligence},
  volume={36},
  number={10},
  pages={10938--10946},
  year={2022}
}
```

## Dataset Metadata
The following table is necessary for this dataset to be indexed by search
engines such as <a href="https://g.co/datasetsearch">Google Dataset Search</a>.
<div itemscope itemtype="http://schema.org/Dataset">
<table>
  <tr>
    <th>property</th>
    <th>value</th>
  </tr>
  <tr>
    <td>name</td>
    <td><code itemprop="name">Schema-Guided Dialogue Dataset</code></td>
  </tr>
  <tr>
    <td>alternateName</td>
    <td><code itemprop="alternateName">SGD dataset</code></td>
  </tr>
  <tr>
    <td>url</td>
    <td><code itemprop="url">https://github.com/google-research-datasets/dstc8-schema-guided-dialogue</code></td>
  </tr>
  <tr>
    <td>sameAs</td>
    <td><code itemprop="sameAs">https://github.com/google-research-datasets/dstc8-schema-guided-dialogue</code></td>
  </tr>
  <tr>
    <td>description</td>
    <td><code itemprop="description">The dataset consists of conversations between a virtual assistant and a user ranging over a variety of domains including Travel, Events, Payment, Media, Restaurants, Weather etc. Annotations for natural language understanding, dialogue state tracking, policy learning, natural language generation and user simulation learning are also included.</code></td>
  </tr>
  <tr>
    <td>provider</td>
    <td>
      <div itemscope itemtype="http://schema.org/Organization" itemprop="provider">
        <table>
          <tr>
            <th>property</th>
            <th>value</th>
          </tr>
          <tr>
            <td>name</td>
            <td><code itemprop="name">Google</code></td>
          </tr>
          <tr>
            <td>sameAs</td>
            <td><code itemprop="sameAs">https://en.wikipedia.org/wiki/Google</code></td>
          </tr>
        </table>
      </div>
    </td>
  </tr>
  <tr>
    <td>citation</td>
    <td><code itemprop="citation">https://identifiers.org/arxiv:1909.05855</code></td>
  </tr>
</table>
</div>
