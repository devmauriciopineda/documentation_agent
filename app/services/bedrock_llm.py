from typing import List, Optional

import boto3
import litellm
from config.config import settings
from schemas.schemas import Message

REGION = settings.aws_region
ACCESS_KEY = settings.aws_access_key_id
SECRET_KEY = settings.aws_secret_access_key
LLM_NAME = settings.llm_name
TEMPERATURE = settings.temperature
TOKENS = settings.tokens

client = boto3.client('bedrock-runtime', region_name=REGION)
AWS_MODEL = f"bedrock/{LLM_NAME}"
AWS_MODEL_ARN = F"arn:aws:bedrock:{REGION}:559050237389:inference-profile/{LLM_NAME}"

litellm.api_base = "https://bedrock-runtime.us-east-1.amazonaws.com"


def query_model(
    messages: List[Message],
    temperature: Optional[float] = TEMPERATURE,
    tokens: Optional[int] = TOKENS,
) -> str:
    """Query a Large Language Model."""
    response = litellm.completion(
        model=AWS_MODEL,
        api_base=litellm.api_base,
        messages=messages,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        aws_region_name=REGION,
        temperature=temperature,
        max_tokens=tokens,
        drop_params=True,
    )
    aws_answer = response.choices[0].message.content
    return aws_answer
