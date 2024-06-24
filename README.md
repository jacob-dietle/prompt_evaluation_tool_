---
title: Prompt Evaluation Tool
emoji: 🟠
colorFrom: yellow
colorTo: yellow
sdk: gradio
sdk_version: 4.36.1
app_file: app.py
pinned: false
license: agpl-3.0
---

# 🟠Prompt Evaluation Tool

The Prompt Evaluation Tool is a Gradio-based application designed to accelerate prompt engineering by allowing users to test multiple prompt and variable combinations simultaneously.


You can use this app hosted on HF Spaces at this [link]()

## Features:

- Interactive UI for inputting prompt templates and variables
- Support for multiple placeholders in prompts
- JSON variable upload functionality
- Dynamic creation of input fields based on detected placeholders
- Integration with Claude API for prompt evaluation
- Configurable model parameters (model selection, max tokens, temperature)

### [Loom on How to use](https://www.loom.com/share/4baee550b7ef40e7a7fb0a7bda438466?sid=a785f579-1187-4281-8f10-ade220d4c3c9)

## Import Notes & Usage:

**Setting Variables:** You can either insert variables manually via the table or upload a JSON file. When uploading variables as a JSON file, use the following format:

```
{
  "placeholder_name": {
    "type": "single",
    "value": "single_value"
  },
  "another_placeholder": {
    "type": "array",
    "values": ["value1", "value2", "value3"]
  }
}
```

**Placeholder Max:** The tool supports up to 5 placeholders in a single prompt template. You can change this to an arbitrary number, it was just required to enable the dynamic creation of placeholder tabs in the uI.


## Contributing:

Contributions to improve the Prompt Evaluation Tool are welcome. Please feel free to submit issues or pull requests to the repository.


## License:

AGPL3




