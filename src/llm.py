import boto3
from langchain_aws import ChatBedrock

bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-west-2")


def create_llm(model_id: str):
    return ChatBedrock(
        model_id=model_id,
        client=bedrock_runtime,
        model_kwargs={"temperature": 0.7, "max_tokens": 32768},
    )
