from typing import List, Dict, Any
import os
from openai import OpenAI
import asyncio
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

def generate_response(query, retrieved_documents: List[Dict[Any, Any]]):
    # Format retrieved documents into context
    context = ""
    for i, doc in enumerate(retrieved_documents):
        source = doc.get('metadata', {}).get('source', 'Unknown')
        page = doc.get('metadata', {}).get('page', 'Unknown')
        context += f"\nDocument {i+1} (Source: {source}, Page: {page}):\n{doc['content']}\n"
    
    # Create a structured prompt
    prompt = f"""
    User Query: {query}
    
    Retrieved Information:
    {context}
    
    Based on the above information only, provide a comprehensive answer to the user's query.
    If the information is not sufficient to answer the query, acknowledge this limitation.
    Include citations to the specific documents you reference.
    """
    
    return prompt

async def call_llm_stream(prompt):
    # Set up your API client
    client = OpenAI(api_key=os.getenv('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")

    try:
        # Create a generator function for streaming
        async def response_generator():
            # Start the stream in a separate thread
            stream_response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant, answer the user's query based on the provided information."},
                        {"role": "user", "content": prompt},
                    ],
                    stream=True,  # Enable streaming
                    temperature=0.5,
                )
            )
            
            # Iterate through the stream chunks
            for chunk in stream_response:
                # Check if the chunk has content
                if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content is not None:
                        yield delta.content
    
        return response_generator()
    except Exception as e:
        logger.error(f"Error calling LLM API: {e}")
        async def error_generator():
            yield "Sorry, I encountered an error generating a response."
        return error_generator()