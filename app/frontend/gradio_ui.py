import gradio as gr
import os
import json
import re
from app.backend.prompt_evalute import evaluate_prompts

MAX_TABS = 5

def detect_placeholders(prompt):
    placeholders = re.findall(r'\{(\w+)\}', prompt)
    return list(set(placeholders))  # Remove duplicates

def update_ui(prompt):
    placeholders = detect_placeholders(prompt)
    new_visibilities = [i < len(placeholders) for i in range(MAX_TABS)]
    updates = [gr.update(visible=vis, label=placeholders[i] if i < len(placeholders) else f"Placeholder {i+1}") 
               for i, vis in enumerate(new_visibilities)]
    return [json.dumps(placeholders)] + updates

def gather_variables(prompt, *dataframes):
    placeholders = detect_placeholders(prompt)
    variables = {}
    for placeholder, df in zip(placeholders, dataframes):
        if df is not None and len(df) > 0:
            values = [row[0] for row in df.values if row[0]]
            if len(values) > 1:
                variables[placeholder] = {
                    "type": "array",
                    "values": values
                }
            else:
                variables[placeholder] = {
                    "type": "single",
                    "value": values[0] if values else ""
                }
    return variables

def prepare_evaluation(prompt, *dataframes):
    gathered_variables = gather_variables(prompt, *dataframes)
    return json.dumps({"prompt": prompt, "variables": gathered_variables})

async def run_evaluation(prompt, model, max_tokens, temperature, *dataframes):
    variables = gather_variables(prompt, *dataframes)
    model_parameters = {
        "model": model,
        "max_tokens_to_sample": max_tokens,
        "temperature": temperature
    }
    
    try:
        results = await evaluate_prompts(prompt, variables, model_parameters)
        return format_results(results)
    except Exception as e:
        return [{"Variables": "", "Prompt": "", "Response": str(e), "Input Tokens": 0, "Output Tokens": 0}]
    
def format_results(results):
    headers = ["Variables", "Prompt", "Response", "Input Tokens", "Output Tokens"]
    formatted_results = [headers]  # Add headers as the first row
    for result in results:
        formatted_results.append([
            json.dumps(result.variables),
            result.prompt,
            result.response,
            result.token_usage.input_tokens,
            result.token_usage.output_tokens
        ])
    return formatted_results

def process_uploaded_json(file):
    if file is None:
        return None
    try:
        if isinstance(file, str):
            # If it's a string, it's likely a file path
            with open(file, 'r') as f:
                json_data = json.load(f)
        else:
            # If it's bytes, we can decode and load it directly
            json_data = json.loads(file.decode('utf-8'))
        return json_data
    except json.JSONDecodeError:
        return None

def update_dataframes(json_data, placeholders):
    if json_data is None or not placeholders:
        return [gr.update(visible=False)] * MAX_TABS

    updates = []
    for i, placeholder in enumerate(placeholders):
        if i >= MAX_TABS:
            break

        if placeholder in json_data:
            value = json_data[placeholder]
            if isinstance(value, dict) and "type" in value:
                if value["type"] == "array" and "values" in value:
                    if isinstance(value["values"], list):
                        updates.append(gr.update(value=[[str(v)] for v in value["values"]], visible=True, label=placeholder))
                    elif isinstance(value["values"], dict):
                        nested_values = [f"{k}: {json.dumps(v)}" for k, v in value["values"].items()]
                        updates.append(gr.update(value=[[v] for v in nested_values], visible=True, label=placeholder))
                elif value["type"] == "single" and "value" in value:
                    updates.append(gr.update(value=[[str(value["value"])]], visible=True, label=placeholder))
            else:
                updates.append(gr.update(value=[[json.dumps(value)]], visible=True, label=placeholder))
        else:
            updates.append(gr.update(visible=True, label=placeholder))  # Empty but visible dataframe for manual input

    # Fill remaining tabs with empty updates
    updates.extend([gr.update(visible=False)] * (MAX_TABS - len(updates)))

    return updates

def process_upload_and_update(file, placeholders):
    json_data = process_uploaded_json(file)
    if json_data and placeholders:
        # placeholders is already a list, no need to parse it
        return update_dataframes(json_data, placeholders)
    return [gr.update(visible=False)] * MAX_TABS

def set_api_key(api_key):
    os.environ["USER_API_KEY"] = api_key
    return "API Key set successfully!"

logo_markdown = """
<a href="https://www.generateleverage.com" target="_blank">
    <img src="https://cdn.prod.website-files.com/65cbec81500fdd8e6fd9b5ef/65cbffa7cba3a28066124cfc_Digital%20Leverage%20Logo%20SVG.svg" alt="Digital Leverage Logo" style="height: 50px; width: auto;">
</a>
"""

with gr.Blocks() as demo:
    gr.Markdown("# 🟠Prompt Evaluation Tool")
    gr.Markdown("This app allows you test multiple prompt and variable combinations at once to accelerate your prompt engineering. How to use video [here](https://www.youtube.com/watch?v=djV11QZ7zK8)")
    
    

    with gr.Row():
        with gr.Column(scale=1):
            prompt_template = gr.Textbox(lines=5, label="Prompt Template")

        
        with gr.Column(scale=1):
            detected_placeholders = gr.JSON(label="Detected Placeholders", visible=True)
            
            gr.Markdown("## Model Configuration")
            model = gr.Dropdown(
                ["claude-3-5-sonnet-20240620", "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
                label="Model",
                value="claude-3-5-sonnet-20240620"
            )
            max_tokens = gr.Slider(
                minimum=1,
                maximum=4000,
                value=1000,
                step=1,
                label="Max Tokens",
                info="Maximum number of tokens to generate (1-4000)"
            )
            temperature = gr.Slider(
                minimum=0,
                maximum=1,
                value=0.7,
                step=0.01,
                label="Temperature",
                info="Controls randomness (0-1)"
            )

            api_key_input = gr.Textbox(type="password", label="API Key")
            set_key_button = gr.Button("Set API Key")
            api_key_message = gr.Markdown()
            set_key_button.click(set_api_key, inputs=api_key_input, outputs=api_key_message)

    
    upload_button = gr.UploadButton(
        "Upload JSON Variables",
        file_count="single",
        file_types=[".json"],
        type="binary"
    )
    
    tabs = []
    dataframes = []
    with gr.Tabs():
        for i in range(MAX_TABS):
            with gr.Tab(f"Placeholder {i+1}", visible=False) as tab:
                df = gr.Dataframe(
                    headers=["Variable"],
                    datatype=["str"],
                    col_count=(1, "fixed"),
                    row_count=(1, "dynamic"),
                    label=f"Variables for Placeholder {i+1}",
                    interactive=True,
                    wrap=True
                )
                tabs.append(tab)
                dataframes.append(df)
    
    prompt_template.change(
        update_ui,
        inputs=[prompt_template],
        outputs=[detected_placeholders] + tabs
    )
    
    # Move the upload event listener inside the gr.Blocks context
    upload_button.upload(
        process_upload_and_update,
        inputs=[upload_button, detected_placeholders],
        outputs=dataframes
    )
    
    evaluate_button = gr.Button("Evaluate Prompt")
    evaluation_input = gr.JSON(label="Evaluation Input", visible=False)

    results = gr.Dataframe(
        headers=["Variables", "Prompt", "Response", "Input Tokens", "Output Tokens"],
        datatype=["str", "str", "str", "number", "number"],
        label="Evaluation Results",
        wrap=False,
        line_breaks=True,
        interactive=True,
        column_widths=[75, 75, 250, 50, 50]      
    )
    
    
    gr.Markdown(logo_markdown)


    evaluate_button.click(
        run_evaluation,
        inputs=[prompt_template, model, max_tokens, temperature] + dataframes,
        outputs=[results]
    )

if __name__ == "__main__":
    demo.launch(reload=True, show_error=True)
