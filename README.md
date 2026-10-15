# Context File Splitter

An Antigravity plugin that classifies Markdown context and generates separate
`business_development/` and `architecture/` documentation.

## Use

Place the source Markdown files in `src/` in the target project, then invoke the
`context-file-splitter` skill in Antigravity. The skill segments each document,
classifies each block using `prompt_tagowanie.md`, assembles both output trees,
and validates the results.

The bundled `split_doc.py` expects to run from the target project root and uses
these commands:

```sh
python3 /path/to/context-file-splitter/split_doc.py segment
# The agent creates work/NN.tags.json classifications.
python3 /path/to/context-file-splitter/split_doc.py assemble
python3 /path/to/context-file-splitter/split_doc.py check
```

The original files in `src/` are not modified. Low-confidence classifications
are reported for review.