import itertools
import asyncio
from claude_api import ClaudeAPIClient
from models.claude_api_models import ClaudeResponse
from models.output_models import OutputContent
import json 


def load_model_parameters(file_path):
    with open(file_path) as file:
        return json.load(file)

def load_json(file_path):
    with open(file_path, encoding='utf-8') as file:
        return json.load(file)

def load_prompt(file_path):
    with open(file_path) as file:
        return file.read()


def generate_prompt_combinations(base_prompt, variables):
    variable_names = list(variables.keys())
    variable_values = []
    
    for name in variable_names:
        if variables[name]["type"] == "single":
            variable_values.append([variables[name]["value"]])
        elif variables[name]["type"] == "array":
            variable_values.append(variables[name]["values"])
    
    for combination in itertools.product(*variable_values):
        prompt_data = {name: value for name, value in zip(variable_names, combination)}
        try:
            yield base_prompt.format(*combination, **prompt_data)
        except KeyError as e:
            raise KeyError(f"Missing variable in prompt data: {e}")

class PromptEvaluator:
    def __init__(self, model_parameters):
        self.api_client = ClaudeAPIClient()
        self.model_parameters = model_parameters

    async def evaluate_prompt(self, prompt):
        response = await self.api_client.generate_response(prompt, self.model_parameters)
        return ClaudeResponse(**response)

async def evaluate_prompts(base_prompt, variables, model_parameters):
    evaluator = PromptEvaluator(model_parameters)
    prompts = list(generate_prompt_combinations(base_prompt, variables))
    
    tasks = []
    for prompt in prompts:
        task = asyncio.create_task(evaluator.evaluate_prompt(prompt))
        tasks.append(task)

    responses = await asyncio.gather(*tasks)

    output_contents = []
    for prompt, response in zip(prompts, responses):
        if response:
            output_content = OutputContent(
                variables=variables,
                prompt=prompt,
                response=''.join([block.text for block in response.content]),
                token_usage=response.usage
            )
            output_contents.append(output_content)

    return output_contents

