
input_prompt = '' #必填 在input_prompt.json编辑
name='张三'  #默认
language='英语' #默认
#这是输入

import cyy_util
import json
paper=''
# Load the input prompt from the JSON file

with open('input_prompt.json', 'r', encoding='utf-8') as file:
    input_prompt = file.read()

# Define the prompt for generating the paper catalog
latex_paper_prompt = f'''{input_prompt}
帮我生成论文目录，json格式返回,语言用{language}
''' + "格式举例{'title': '***', 'sections': [{'title': '***', 'subsections': []},{'title': '***', 'subsections': []},{'title': '***', 'subsections': []},******  ]}"

# Call the LLM to generate the catalog
catalog = cyy_util.call_llm_json(messages=[{'role': 'user', 'content': latex_paper_prompt}])
# catalog=json.loads("{\n  \"title\": \"论文综述：多模态大语言模型在机器人操作中的应用\",\n  \"sections\": [\n    {\n      \"title\": \"引言\",\n      \"subsections\": []\n    },\n    {\n      \"title\": \"多模态大语言模型在机器人操作中的基础\",\n      \"subsections\": [\n        {\n          \"title\": \"PaLM-E: 一种具身多模态语言模型\",\n          \"subsections\": []\n        },\n        {\n          \"title\": \"ManipVQA: 向多模态大语言模型注入机器人操作知识\",\n          \"subsections\": []\n        },\n        {\n          \"title\": \"ManipLLM: 面向对象中心机器人操作的具身多模态大语言模型\",\n          \"subsections\": []\n        }\n      ]\n    },\n    {\n      \"title\": \"视觉-语言模型在机器人任务规划中的应用\",\n      \"subsections\": [\n        {\n          \"title\": \"Look Before You Leap: 揭示GPT-4V在机器人视觉-语言规划中的力量\",\n          \"subsections\": []\n        },\n        {\n          \"title\": \"LEO: 3D世界中的具身通用代理\",\n          \"subsections\": []\n        }\n      ]\n    },\n    {\n      \"title\": \"模仿学习在机器人操作中的应用\",\n      \"subsections\": [\n        {\n          \"title\": \"MimicPlay: 通过观看人类游戏进行长时程模仿学习\",\n          \"subsections\": []\n        },\n        {\n          \"title\": \"Vid2Robot: 使用跨注意力变换器的端到端视频条件策略学习\",\n          \"subsections\": []\n        },\n        {\n          \"title\": \"UMI: 无需野外机器人的野外机器人教学\",\n          \"subsections\": []\n        },\n        {\n          \"title\": \"DexCap: 可扩展和便携的动捕数据收集系统\",\n          \"subsections\": []\n        },\n        {\n          \"title\": \"HIRO Hand: 用于手把手模仿学习的可穿戴机器人手\",\n          \"subsections\": []\n        }\n      ]\n    },\n    {\n      \"title\": \"生成模型在机器人学习中的应用\",\n      \"subsections\": [\n        {\n          \"title\": \"RoboGen: 通过生成模拟释放无限数据用于自动化机器人学习\",\n          \"subsections\": []\n        },\n        {\n          \"title\": \"MimicGen: 使用人类示范进行可扩展机器人学习的数据生成系统\",\n          \"subsections\": []\n        }\n      ]\n    },\n    {\n      \"title\": \"结论与未来工作\",\n      \"subsections\": []\n    }\n  ]\n}")
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

    for index1,section in enumerate(sections):
        section_title = section.get('title', 'Untitled Section')
        formatted_output += f"-{index1+1}.{section_title}\n"

        subsections = section.get('subsections', [])
        for index2,subsection in enumerate(subsections):
            subsection_title = subsection.get('title', 'Untitled Subsection')
            formatted_output += f"  -{index1+1}.{index2+1}. {subsection_title}\n"

    return formatted_output

# Print the formatted catalog
print("\nFormatted Catalog:")
print(format_catalog(catalog))


catalog

paper=r'''
\documentclass[a4paper]{article}
\usepackage[english]{babel}
\usepackage[utf8]{inputenc}
\usepackage{amsmath}
\usepackage{graphicx}
\usepackage[colorinlistoftodos]{todonotes}
\usepackage{hyperref}
\usepackage{ctex}
'''

paper=paper+f"\\title{{{catalog['title']}}}"+f"\n\\author{{{name}}}"

paper+=r'''
\begin{document}
\maketitle
'''
# Debugging with pdb
# import pdb
# pdb.set_trace()


# abstract_promtp=f'''
# 这是论文需求和目录
# {input_prompt}
# {catalog}
# 生成摘要,json格式返回,语言用{language}
# '''+r"{'result':'\n \begin{abstract} \n   *** \n    \end{abstract}'}"
# abstract = cyy_util.call_llm_json(messages=[{'role': 'user', 'content': abstract_promtp}])['result']
# # abstract=json.loads("{\n  \"result\": \"\\\\begin{abstract} \\n   This paper presents a comprehensive analysis and discussion based on the provided input prompt and catalog. It aims to explore the underlying themes, methodologies, and potential contributions to the field of study. Through a detailed examination of the topics outlined in the catalog, the paper seeks to offer insights and propose innovative solutions or perspectives. The abstract encapsulates the essence of the research, highlighting the objectives, scope, and significance of the study. \\n    \\\\end{abstract}\"\n}")['result']
# print(abstract)

# paper+='\n'+abstract


# for sec in catalog['sections']:
#     sec_promtp=f'''
#     这是论文需求和目录
#     {input_prompt}
#     {catalog}
#     生成章节{sec},json格式返回,语言用{language},文字尽可能多，1k以上,文字尽可能多，1k
    
#     '''+r"{'result':'\section{***}***\n'}"
#     # sec_content = cyy_util.call_llm_json(messages=[{'role': 'user', 'content': sec_promtp}])['result']
#     sec_content=json.loads("{\n  \"result\": \"\\\\section{Introduction}This section introduces the background, significance, and objectives of the research.\\n\"\n}")['result']
#     paper+='\n'+sec_content
#     print(sec_content)
#     break
#     concurrent_data.append([{'role': 'user', 'content': sec_promtp}])


# ref_promtp=f'''
# 这是论文需求和目录
# {input_prompt}
# {catalog}
# 生成引用,json格式返回,语言用{language}
# '''+r"{'result':'\begin{thebibliography}{99}'} ***********  \n \end{thebibliography}"
# ref_content = cyy_util.call_llm_json(messages=[{'role': 'user', 'content': ref_promtp}])['result']
# paper+='\n'+ref_content
# print(ref_content)
#这是单线程代码

concurrent_data=[]
def concurrent_gen(messages):
    for i in range(4):
        if i >0:
            print(f'第{i}次重试')
        result=cyy_util.call_llm_json(messages=messages)
        try:
            if 'result' in result:
                return result['result']
        except Exception as e:
            continue



abstract_promtp=f'''
这是论文需求和目录
{input_prompt}
{catalog}
生成摘要,json格式返回,语言用{language}
'''+r"{'result':'\n \begin{abstract} \n   *** \n    \end{abstract}'}"

concurrent_data.append([{'role': 'user', 'content': abstract_promtp}])

for sec in catalog['sections']:
    sec_promtp=f'''
    这是论文需求和目录
    {input_prompt}
    {catalog}
    生成章节{sec},json格式返回,语言用{language},文字尽可能多，1k以上
    
    '''+r"{'result':'\section{***}***\n'}"

    concurrent_data.append([{'role': 'user', 'content': sec_promtp}])


ref_promtp=f'''
这是论文需求和目录
{input_prompt}
{catalog}
生成引用,json格式返回,语言用{language}
'''+r"{'result':'\begin{thebibliography}{99}'} ***********  \n \end{thebibliography}"
concurrent_data.append([{'role': 'user', 'content': ref_promtp}])

cc_result=cyy_util.concurrent_traversal(concurrent_data,concurrent_gen)

for content in cc_result:
    paper+='\n'+content

paper+=r'''
\end{document}
'''
import time
#获取时间戳，新建目录 时间戳-name-language
import os
save_path=f'{time.time()}_{name}_{language}'
os.makedirs(save_path,exist_ok=True)

with open(os.path.join(save_path,'main.tex'),'w',encoding='utf-8') as file:
    file.write(paper)
# import pdb
# pdb.set_trace()
print(f"main.tex以保存至{os.path.join(save_path,'main.tex')}")