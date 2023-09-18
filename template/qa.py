from string import Template

template = Template('''

**Instruction Template for Question-Answer ChatGPT Application**

This template is designed to provide answers to questions based on 
a given context text and a query. Please follow the guidelines below 
for effective interactions:

===

1. **Context Text:**
    - Provide a clear and concise context text that contains information relevant to the query.
    - The context text is wrapped by <begin> <end>, e.g., <begin> I am Lucy and live in London. <end>

Context: <begin> $context <end>

===

2. **Query:**
    - Be as concise as possible while providing enough information for a meaningful response.
    - The query text is wrapped by <begin> <end>, e.g., <begin> What is my name? <end>

Query: <begin> $query <end>

===

3. **Response:**
    - The response will be provided in code or text form, depending on the goal of the query.
    - If requesting code, specify the programming language or platform you want the code in.
        default to Python.
''')
