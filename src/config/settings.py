import yaml
from pathlib import Path

PROMPTS_PATH = Path(__file__).parent / "prompts.yaml"

with open(PROMPTS_PATH, "r") as f:
    PROMPTS = yaml.safe_load(f)

CLASSIFY_PROMPT = PROMPTS["classify_prompt"]
GRADING_PROMPT = PROMPTS["grading_prompt"]
REWRITE_PROMPT = PROMPTS["rewrite_prompt"]
GENERATE_PROMPT = PROMPTS["generate_prompt"]
