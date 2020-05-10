# The Schema-Guided Dialogue Dataset

**Contact -** schema-guided-dst@google.com

## Overview

The Schema-Guided Dialogue (SGD) dataset consists of over 20k annotated
multi-domain, task-oriented conversations between a human and a virtual
assistant. These conversations involve interactions with services and APIs
spanning 20 domains, ranging from banks and events to media, calendar, travel,
and weather. For most of these domains, the dataset contains multiple different
APIs, many of which have overlapping functionalities but different interfaces,
which reflects common real-world scenarios. The wide range of available
annotations can be used for intent prediction, slot filling, dialogue state
tracking, policy imitation learning, language generation, user simulation
learning, among other tasks in large-scale virtual assistants. Besides these,
the dataset has unseen domains and services in the evaluation set to quantify
the performance in zero-shot or few shot settings.

**The dataset is provided "AS IS" without any warranty, express or implied.
Google disclaims all liability for any damages, direct or indirect, resulting
from the use of this dataset.**

## Updates

**07/05/2020** - Test set annotations released. User actions and service calls
made during the dialogue are also released for all dialogues.

**10/14/2019** - DSTC8 challenge concluded. Details about the submissions to the
challenge may be found in the [challenge overview
paper](https://arxiv.org/pdf/2002.01359.pdf).

**10/07/2019** - Test dataset released without the dialogue state annotations.

**07/23/2019** - Train and dev sets are publicly released as part of [DSTC8
challenge](dstc8.md).

## Important Links

* [Paper for dataset and DST baseline](https://arxiv.org/pdf/1909.05855.pdf)
* [DSTC8 overview paper](https://arxiv.org/pdf/2002.01359.pdf)
* [Code for DST
  baseline](https://github.com/google-research/google-research/tree/master/schema_guided_dst)
* [Natural language generation](https://arxiv.org/pdf/2004.15006.pdf)
* [Blog post announcing the
  dataset](https://ai.googleblog.com/2019/10/introducing-schema-guided-dialogue.html)

## Data
The dataset consists of schemas outlining the interface of different APIs, and
annotated dialogues. The dialogues have been generated with the help of a
dialogue simulator and paid crowd-workers. The data collection approach is
summarized in our [paper](https://arxiv.org/pdf/1801.04871.pdf).


### Scheme Representation
A service or API is essentially a set of functions (called intents), each taking
a set of parameters (called slots). A schema is a normalized representation of
the interface exposed by a service/API. In addition, the schema also includes
natural language description of the included functions and their parameters to
outline the semantics of each element. The schemas have been manually generated
by the dataset creators. The schema for a service contains the following fields:

*   **service_name** - A unique name for the service.
*   **description** - A natural language description of the tasks supported by
    the service.
*   **slots** - A list of slots/attributes corresponding to the entities present
    in the service. Each slot contains the following fields:
    *   **name** - The name of the slot.
    *   **description** - A natural language description of the slot.
    *   **is_categorical** - A boolean value. If it is true, the slot has a
        fixed set of possible values.
    *   **possible_values** - List of possible values the slot can take. If the
        slot is a categorical slot, it is a complete list of all the possible
        values. If the slot is a non categorical slot, it is either an empty
        list or a small sample of all the values taken by the slot.
*   **intents** - The list of intents/tasks supported by the service. Each
    method contains the following fields:
    *   **name** - The name of the intent.
    *   **description** - A natural language description of the intent.
    *   **is_transactional** - A boolean value. If true, indicates that the
        underlying API call is transactional (e.g, a booking or a purchase), as
        opposed to a search call.
    *   **required_slots** - A list of slot names whose values must be provided
        before making a call to the service.
    *   **optional_slots** - A dictionary mapping slot names to the default
        value taken by the slot. These slots may be optionally specified by the
        user and the user may override the default value. An empty default value
        allows that slot to take any value by default, but the user may override
        it.
    *   **result_slots** - A list of slot names which are present in the results
        returned by a call to the service or API.

### Dialogue Representation

The dialogue is represented as a list of turns, where each turn contains either
a user or a system utterance. The annotations for a turn are grouped into
frames, where each frame corresponds to a single service. Each turn in the
single domain dataset contains exactly one frame. In multi-domain datasets, some
turns may have multiple frames.

Each dialogue is represented as a json object with the following fields:

*   **dialogue_id** - A unique identifier for a dialogue.
*   **services** - A list of services present in the dialogue.
*   **turns** - A list of annotated system or user utterances.

Each turn consists of the following fields:

*   **speaker** - The speaker for the turn. Possible values are "USER" or
    "SYSTEM".
*   **utterance** - A string containing the natural language utterance.
*   **frames** - A list of frames, each frame containing annotations for a
    single service.

Each frame consists of the fields listed below. The fields marked with * will
be excluded from all user turns in the test data released to the participants.

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

The dataset is released under [**CC BY-SA
4.0**](https://creativecommons.org/licenses/by-sa/4.0/) license. For the full
license, see [LICENSE.txt](LICENSE.txt). Please cite the following paper if you
use this dataset in your work

```shell
@article{rastogi2019towards,
  title={Towards Scalable Multi-domain Conversational Agents: The Schema-Guided Dialogue Dataset},
  author={Rastogi, Abhinav and Zang, Xiaoxue and Sunkara, Srinivas and Gupta, Raghav and Khaitan, Pranav},
  journal={arXiv preprint arXiv:1909.05855},
  year={2019}
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
