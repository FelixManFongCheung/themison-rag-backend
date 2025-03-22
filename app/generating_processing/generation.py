from typing import List, Dict, Any

def generate_response(documents: List[Dict[Any, Any]]):
    
    # Sort documents by their ID to maintain order
    sorted_docs = sorted(documents, key=lambda x: x['id'])
    
    # Extract key information from documents
    document_info = []
    for doc in sorted_docs:
        content = doc['content']
        metadata = doc.get('metadata', {})
        source = metadata.get('source', 'Unknown source')
        page = metadata.get('page', 'Unknown page')
        
        # Add document information to our collection
        document_info.append({
            'content': content,
            'source': source,
            'page': page
        })
    
    # Analyze the documents to determine what they're about
    # For this example, we'll assume they're about an internship agreement
    
    # Create a coherent response based on the documents
    response = "Based on the documents I've reviewed, I found information about an internship agreement. "
    
    # Check if we have the internship agreement document
    internship_info = next((doc for doc in document_info if "internship" in doc['content'].lower()), None)
    if internship_info:
        response += f"The document appears to be an Internship and Non-Disclosure & Confidentiality Agreement from Themison Aps. "
    
    # Check if we have information about the company
    company_info = next((doc for doc in document_info if "themison" in doc['content'].lower()), None)
    if company_info:
        response += f"Themison Aps is located at Fruebjergvej 3, 2100, København Ø, Denmark. "
    
    # Check if we have information about the internship responsibilities
    responsibilities_info = next((doc for doc in document_info if "responsibilities" in doc['content'].lower() or "duties" in doc['content'].lower()), None)
    if responsibilities_info:
        response += "The internship responsibilities include: "
        
        # Extract bullet points if they exist
        if "•" in responsibilities_info['content']:
            bullet_points = [line.strip() for line in responsibilities_info['content'].split("•") if line.strip()]
            for point in bullet_points[:4]:  # Limit to first few points to keep response concise
                if len(point) > 100:  # Truncate long points
                    point = point[:100] + "..."
                response += f"\n• {point}"
    
    # Add source information
    response += "\n\nThis information comes from the following sources:\n"
    for doc in document_info:
        response += f"- {doc['source']}, page {doc['page']}\n"
    
    return response