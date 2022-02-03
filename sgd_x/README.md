# The Schema-Guided Dialogue - eXtended (SGD-X) Dataset

## About

For a full explanation of the SGD-X dataset, see
`.../dstc8-schema-guided-dialogue/README.md` or the
[SGD-X paper](https://arxiv.org/pdf/2110.06800.pdf).

The 5 variants schemas are under the folders
`.../dstc8-schema-guided-dialogue/sgd_x/data/v{i}`, where `i` is the variant
number. Only the schemas are populated in these folders, and the corresponding
dialogues must be generated using the script `generate_sgdx_dialogues.py`.

## Instructions for Generating Dialogues

`generate_sgdx_dialogues.py` copies the original dialogues and substitutes the
original schema element names for the variant ones. New dialogue files must be
generated in order to evaluate performance on SGD-X.

To run the script, `cd` into the `.../dstc8-schema-guided-dialogue/` directory.
Then run the following command:

```shell
python3 -m sgd_x.generate_sgdx_dialogues
```

By default, the script will copy data from `.../dstc8-schema-guided-dialogue/`
and add the generated dialogue files into
`.../dstc8-schema-guided-dialogue/sgd_x/data/`. However, the filepaths can be
changed with CLI arguments as needed.
