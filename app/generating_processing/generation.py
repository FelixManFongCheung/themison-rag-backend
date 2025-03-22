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

async def call_llm(prompt):
    # Set up your API client
    client = OpenAI(api_key=os.getenv('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")

    try:
        # Use asyncio to run the synchronous API call in a thread pool
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant, answer the user's query based on the provided information."},
                    {"role": "user", "content": prompt},
                ],
                stream=True,
                temperature=0.5,
                
            )
        )
        
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error calling LLM API: {e}")
        return "Sorry, I encountered an error generating a response."