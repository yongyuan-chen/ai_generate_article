# import pdb
# import sys

# def custom_excepthook(type, value, traceback):
#     # 在报错时自动进入调试模式
#     print("报错了,进入调试模式...")
#     pdb.post_mortem(traceback)
# sys.excepthook = custom_excepthook

#pdb调试命令
# n：单步执行，跳过函数调用。
# s：单步执行，进入函数内部。
# c：继续运行程序，直到下一个断点或程序结束。
# l：显示当前代码上下文。
# w：显示堆栈跟踪，查看函数调用路径。
# up：向上移动到调用栈的上一层。
# down：向下移动到调用栈的下一层。
# frame 3  使用 frame（或 f）命令可以直接切换到目标帧。  （从上到下编号从 0 开始）。

import os
from openai import AzureOpenAI
import json
import concurrent.futures
from openai import OpenAI
from langchain.prompts import PromptTemplate
#默认使用deepseek，只用添加deepseek的key就能运行。
deepseek_client = OpenAI(api_key="sk-ee31f6dcf3184a8b8bedcf1c226ef3e4", base_url="https://api.deepseek.com") #deepseek的key  官网免费申请500w额度



api_key = "***"#AzureOpenAI 的key，需要用就写，然后再call_llm_json函数参数修改默认调用的model为gpt-4o
azure_endpoint = "https://aireadygo2.openai.azure.com/"
api_version = "2024-05-01-preview"
client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", azure_endpoint), 
  api_key=os.getenv("AZURE_OPENAI_API_KEY",api_key),  
  api_version=api_version
)

# deepseek_client.chat.completions.create(    save_to_json(messages,'messages.json')
model_client_map={'deepseek-chat':deepseek_client,'gpt-4o':client}

import time

def call_llm_json(messages, model='deepseek-chat'):
    """
    调用 LLM 并返回 JSON 格式的响应，支持最多 3 次重试。
    """
    if "AI_MODELING_LLM_TYPE" in os.environ:
        model = os.environ["AI_MODELING_LLM_TYPE"]

    # 最大重试次数
    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            # 调用模型 API
            response = model_client_map[model].chat.completions.create(
                model=model,
                messages=messages,
                response_format={"type": "json_object"},
                max_tokens=8000
            )
            
            # 保存响应为 JSON 文件
            # save_to_json(response.choices[0].message.content, f'response_{messages[0]["content"][:10]}.json')

            result=json.loads(response.choices[0].message.content)
            # 解析 JSON 响应
            return result

        except json.JSONDecodeError as e:
            retry_count += 1
            print(f'{model} 返回错误 JSON 格式数据，第 {retry_count} 次重试...')
            time.sleep(1)  # 延迟 1 秒后重试

        except Exception as e:
            print(f'调用 {model} 时出现未知错误: {e}')
            break

    # 如果重试失败，返回空字典
    print(f'{model} 在重试 {max_retries} 次后仍然失败，返回空数据。')
    return {}

# def call_llm_json(messages,model='deepseek-chat'):
#     # return json.loads()
    
#     if "AI_MODELING_LLM_TYPE" in os.environ:
#         model=os.environ["AI_MODELING_LLM_TYPE"]
#     # import pdb
#     # pdb.set_trace()
#     # deepseek_client
#     response = model_client_map[model].chat.completions.create(model=model,messages=messages,response_format={ "type": "json_object" },max_tokens=8000)
#     #the valid range of max_tokens is [1, 8192]
#     # max_tokens=8000#deepseek未指定 max_tokens，则默认最大输出长度为 4K。其支持的最大长度是8k。需求文档出去table、excel、image，token最长11k
#     # completion_tokens=1604, prompt_tokens=15674, total_tokens=17278, completion_tokens_details=None, prompt_tokens_details=None, prompt_cache_hit_tokens=15616, prompt_cache_miss_tokens=58))
#     #deepseek-chat	上下文64K	最长生成8K
#     save_to_json(response.choices[0].message.content,f'response_{messages[0]["content"][:10]}.json')
#     # save_to_json(messages,'messages.json')

#     try:
#         # 尝试解析 JSON
#         return json.loads(response.choices[0].message.content)
#     except json.JSONDecodeError as e:
#         # 修剪到错误位置之前的内容
#         print(f'{model}返回错误json格式数据')
#         return {}
#     # return json.loads(response.choices[0].message.content)


import concurrent.futures

# 使用 ThreadPoolExecutor 进行并发处理  不会变更顺序
def concurrent_traversal(data, process_item, max_workers=100):
    results = [None] * len(data)  # 预分配结果列表，确保顺序与原始数据一致
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交任务并记录索引
        future_to_index = {executor.submit(process_item, item): idx for idx, item in enumerate(data)}
        for future in concurrent.futures.as_completed(future_to_index):
            idx = future_to_index[future]
            # try:
            result = future.result()
            results[idx] = result  # 将结果放置在正确的位置
            # except Exception as e:
            #     print(f"Error processing item at index {idx}: {e},某些请求出错，重试几次python main.py即可")
            #     # 也可以决定是否存储默认值或者 `None`，具体根据需求调整
            #     results[idx] = None
    return results


# 使用 ThreadPoolExecutor 进行并发处理  会变更顺序，以弃用
# def concurrent_traversal(data,process_item,max_workers=100):
#     results = []
#     with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:  # 设置线程池大小为100
#         # 提交任务
#         future_to_item = {executor.submit(process_item, item): item for item in data}
#         for future in concurrent.futures.as_completed(future_to_item):
#             item = future_to_item[future]
#             # try:
#             result = future.result()
#             results.append(result)
#             # print(f"Result for {item[:10]}: {result[:10]}")
#             # except Exception as e:
#             #     print(f"Error processing {item}: {e}")
#     return results



def call_gpt(prompt):
  response = client.chat.completions.create(
      model="gpt-4o", # model = "deployment_name".
      messages=[
          # {"role": "system", "content": "You are a helpful assistant."},
          # {"role": "user", "content": "Does Azure OpenAI support customer managed keys?"},
          # {"role": "assistant", "content": "Yes, customer managed keys are supported by Azure OpenAI."},
          {"role": "user", "content": f"{prompt}"}
      ]
  )
  return response.choices[0].message.content
import re

def fix_json_string(json_string):#有时候llm会输出\n 得改成\\n
    """
    修复 JSON 字符串中的未转义反斜杠和控制字符。
    """
    # 1. 转义未正确转义的反斜杠
    # 这里我们将单个反斜杠（不是已转义的）替换为双反斜杠
    fixed_string = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', json_string)
    
    # 2. 转义所有实际的控制字符（换行、回车、制表符）
    # 直接替换所有的控制字符为其转义形式
    fixed_string = fixed_string.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
    
    return fixed_string

def gpt_response2json(result):
    result=result.replace('```json','').replace('```','')
    if result[0]!='[':
        json_start = result.index("{")
        json_end = result.rindex("}") + 1
        result = result[json_start:json_end]
    result=fix_json_string(result)#有时候llm会输出\n 得改成\\n
    return json.loads(result)

def call_gpt_json(user,sys=None):
    # print(sys)
    # exit()
    messages=[]
    #messges示例
    # [
    #     {"role": "system", "content": f"{sys}"},
    #     # {"role": "user", "content": "Does Azure OpenAI support customer managed keys?"},
    #     # {"role": "assistant", "content": "Yes, customer managed keys are supported by Azure OpenAI."},
    #     {"role": "user", "content": f"{user}"}
    # ]
    if sys!=None:
        messages.append({"role": "system", "content": f"{sys}"})
    
    messages.append({"role": "user", "content": f"{user}"})

    response = client.chat.completions.create(
    model="gpt-4o", # model = "deployment_name".
    messages=messages)
    result=response.choices[0].message.content
    # result=result.replace('```json','').replace('```','')

    return gpt_response2json(result)

def save_to_json(doc_contents, output_file):#把一个数组或者对象或者字典或者字符串保存为json文件
    # 确保输出目录存在
    output_dir = os.path.dirname(output_file)
    if not output_file and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 保存 doc_contents 数组为 JSON 文件
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(doc_contents, json_file, ensure_ascii=False, indent=4)  # 确保支持中文并格式化输出

           
def merge_array(doc_contents):#二维数组去掉第0维  [[1,2,3],[4,5,6]] ->[1,2,3,4,5,6]
    new_doc_contents=[]
    for item in doc_contents:
        new_doc_contents.extend(item)
    return new_doc_contents

def gen_messages(input_provide,template_directory_path):
    # # template_directory_path 示例 输入prompt目录和需要提供的变量，返回messages数组
# AI_modeling/标准答案和大模型输出结果/gss_prompt_for_domainEvent_oder_role_DDD建模2/0_system_doc.json
# AI_modeling/标准答案和大模型输出结果/gss_prompt_for_domainEvent_oder_role_DDD建模2/1_user_null.json
# AI_modeling/标准答案和大模型输出结果/gss_prompt_for_domainEvent_oder_role_DDD建模2/2_assistant_null.json
# AI_modeling/标准答案和大模型输出结果/gss_prompt_for_domainEvent_oder_role_DDD建模2/3_user_null.json
# AI_modeling/标准答案和大模型输出结果/gss_prompt_for_domainEvent_oder_role_DDD建模2/4_assistant_null.json
# AI_modeling/标准答案和大模型输出结果/gss_prompt_for_domainEvent_oder_role_DDD建模2/5_user_null.json
    # Result array
    result_array = []
    messages=[
    # {"role": "system", "content": "You are a helpful assistant."},
    # {"role": "user", "content": "Does Azure OpenAI support customer managed keys?"},
    # {"role": "assistant", "content": "Yes, customer managed keys are supported by Azure OpenAI."},
    # {"role": "user", "content": f"{prompt}"}
]
    # Iterate over all files in the directory
    for filename in sorted(os.listdir(template_directory_path)):
        # print(filename)
        if filename.endswith(".json"):
            file_path = os.path.join(template_directory_path, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            # Extract role and input from the filename
            parts = filename.split('_')
            role = parts[1]
            inputs = parts[2:] if len(parts) > 2 else []
            inputs = [inp.split('.')[0] for inp in inputs if inp != "null.json"]

            # Build the JSON object
            template=PromptTemplate(template=file_content,input_variables=inputs)
            json_obj = {
                "prompt": file_content,
                "role": role,
                "input": inputs,
                "template":template
            }
            input_need={}
            for item1 in inputs:
                for item2 in input_provide:
                    if item1==item2:
                        input_need[item1]=input_provide[item1]
            messages.append({"role":role,"content":template.format(**input_need)})       
            result_array.append(json_obj)
    return messages
