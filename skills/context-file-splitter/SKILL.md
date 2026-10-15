---
name: context-file-splitter
description: Classify Markdown context files and split them into business_development/ and architecture/ outputs.
---

# Split context files

Use this skill when asked to separate project context or documentation into business development and architecture files.

## Workflow

1. Work from the target project root. The splitter reads Markdown files from `src/*.md` and writes generated intermediates to `work/`; do not modify the source documents.
2. Locate the plugin's bundled `split_doc.py` and run it from the target project root:

   ```sh
   python3 /path/to/context-file-splitter/split_doc.py segment
   ```

3. For every generated `work/NN.to_tag.json`, classify every block exactly once using the definitions, decision rule, and JSON format in the plugin's `prompt_tagowanie.md`. Apply those rules directly; do not ask the user to classify blocks or manually approve each file.
   - Use `BL` for business rules, domain terms, roles, permissions, and business states/processes.
   - Use `ARCH` for implementation, components, contracts, integrations, data stores, protocols, technology choices, and non-functional requirements.
   - Use `MIXED` if a block contains both. Split it into `bl_text` and `arch_text` without adding or losing meaning.
   - For `BL` and `ARCH`, set both text fields to `null`. Preserve every input ID exactly once and include a confidence and one-sentence reason.
   - Save the resulting JSON arrays as matching `work/NN.tags.json` files.
4. Run the bundled script's `assemble` command from the target project root to produce `business_development/` and `architecture/`.
5. Run its `check` command. Resolve missing/extra IDs or other reported problems by correcting the tags and reassembling. Report low-confidence IDs for review.
6. Summarize the generated files and any low-confidence classifications. Do not claim success if validation fails.

The script operates on the current working directory, so invoke it with the target project root as the working directory even though the script and prompt are bundled with the plugin.
