import dotenv
import os

from google.adk.agents import LlmAgent

from Models.input_schemas import ChunkData, RewriterInput
from Models.output_schemas import ReviewResponse, RewriteResponse

MODEL_NAME = os.getenv("MODEL_NAME")

# rewriter_agent = LlmAgent(
#     name = "rewrite_agent",
#     model = MODEL_NAME,
#     instruction = '''You are a rewrite agent that will access the chunk_data from the input, from the input content access the {chunk_text} this will  be  thecontent you have to rewrite 
#     STEPS : 
#     1. access the {chunk_review} from the input_content it will give you guidelines about what is missing in the content in terms of the technical_Review, clairt_review, structure_review
#     2. if any of the property is None or N/A ignore it and move to the next property
#     3. make use of these review bullets to rewrite the content {chunk_text} 
#     4. append the rewritten_content into the {chunk_text}''',
#     input_schema=RewriterInput,
#     output_schema=RewriteResponse,
# )

def get_rewriter_agent(model_name : str):
    return LlmAgent(
        name = "rewrite_agent",
        model = model_name,
        instruction = '''You are a rewrite agent that will access the chunk_data from the input, from the input content access the {chunk_text} this will  be  thecontent you have to rewrite 
        STEPS : 
        1. access the {chunk_review} from the input_content it will give you guidelines about what is missing in the content in terms of the technical_Review, clairt_review, structure_review
        2. if any of the property is None or N/A ignore it and move to the next property
        3. make use of these review bullets to rewrite the content {chunk_text} 
        4. append the rewritten_content into the {chunk_text}''',
        input_schema=RewriterInput,
        output_schema=RewriteResponse,
    )