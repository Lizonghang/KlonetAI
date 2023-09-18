import openai
from transformers import Tool
from key import OpenAI_API_Key
from template import qa_template

openai.api_key = OpenAI_API_Key


class SummarizeTool(Tool):
    name = "summarize_query"
    description = ('''
    Summarize a long tutorial text into a shorter text based on a query. It 
    aims to reduce the subsequent API call costs by providing a concise summary.
    
    Args:
        context (str): The long tutorial text to be summarized.
        query (str): The query that guides the summarization process.
        
    Returns:
        str: A concise summary of the tutorial text based on the query. It is 
            automatically determined by the agent based on the prompt's needs.
            
    
    Example:
        # Replace <Your-URL-Path> to the document you need.
        >>> tutorial = text_downloader(url="<Your-URL-Path>")
        # Replace <Your-Query-Text> to the query you need.
        >>> user_query = "<Your-Query-Text>"
        >>> summary = summarize_query(context=tutorial, query=user_query)
    ''')

    inputs = ["str", "str"]
    outputs = ["str"]

    def __call__(self, context: str, query: str):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[{
                "role": "system",
                "content": qa_template.substitute(
                    context=context,
                    query=query
                )
            }]
        )
        content = response['choices'][0]['message']['content']
        context = content.replace('```', '\n')
        return context
