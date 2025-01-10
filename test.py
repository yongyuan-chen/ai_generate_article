text='''
\\begin{thebibliography}{99}
'''

text=r"{'result':'\begin{thebibliography}{99}'}"
print(text)

exit()
import cyy_util
import json

# Load the input prompt from the JSON file
input_prompt = ''
with open('input_prompt.json', 'r', encoding='utf-8') as file:
    input_prompt = file.read()

# Define the prompt for generating the paper catalog
latex_paper_prompt = f'''{input_prompt}
帮我生成论文目录，json格式返回
''' + "格式举例{'title': '***', 'sections': [{'title': '***', 'subsections': []},{'title': '***', 'subsections': []},{'title': '***', 'subsections': []},******  ]}"

# Call the LLM to generate the catalog
catalog = cyy_util.call_llm_json(messages=[{'role': 'user', 'content': latex_paper_prompt}])

# Print the raw catalog for debugging
print("Raw Catalog:")
print(json.dumps(catalog, indent=4, ensure_ascii=False))

# Format and print the catalog
def format_catalog(catalog):
    if not isinstance(catalog, dict):
        return "Invalid catalog format. Expected a dictionary."

    title = catalog.get('title', 'Untitled')
    sections = catalog.get('sections', [])

    formatted_output = f"Title: {title}\n\n"
    formatted_output += "Sections:\n"

    for section in sections:
        section_title = section.get('title', 'Untitled Section')
        formatted_output += f"- {section_title}\n"

        subsections = section.get('subsections', [])
        for subsection in subsections:
            subsection_title = subsection.get('title', 'Untitled Subsection')
            formatted_output += f"  - {subsection_title}\n"

    return formatted_output

# Print the formatted catalog
print("\nFormatted Catalog:")
print(format_catalog(catalog))

# Debugging with pdb
import pdb
pdb.set_trace()