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
            save_to_json(response.choices[0].message.content, f'response_{messages[0]["content"][:10]}.json')

            # 解析 JSON 响应
            return json.loads(response.choices[0].message.content)

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
            try:
                result = future.result()
                results[idx] = result  # 将结果放置在正确的位置
            except Exception as e:
                print(f"Error processing item at index {idx}: {e}")
                # 也可以决定是否存储默认值或者 `None`，具体根据需求调整
                results[idx] = None
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

split_text_prompt='''请你仔细阅读传入的需求文档，依据文档中的大标题对其进行切分操作。这里的大标题是指以“1.”或者“1、”作为序号的标题，例如“1.库存管理”“1、库存管理”等。而小标题则是以“1.1”“1.1.1”等形式呈现的。在生成的结果中，我们将其存储在名为 sections 的数据结构里，需要特别注意的是，sections 中的第一个 section 必须从以“1.”或者“1、”为序号的大标题开始，要严格按照顺序输出每个 section。例如，如果文档中第一个大标题是“2.库存管理”，你需要跳过该部分，继续查找并从以“1.”或者“1、”开头的大标题开始，确保 sections 中第一个 section 是从序号 1 开始，然后按顺序依次输出后续的 section，注意要将文件完整切分，如果需求文档有5个大标题就分成5部分，4个大标题就分成四部分。请你严格按照上述规则进行操作，以保证需求文档的正确切分和 sections 的有序输出。
例如将一个具有3个大标题的需求文档切分后的格式如下所示：
{"sections":[
{"section":"1.检查项目分类及检查类别详细信息",
"content":"此界面用于维护检查项目分类\n检查项目分类取自检查类别字典EXAM_CLASS_DICT表中的本机构的非停用的分类，分类名称以树状结构展示，按照序号SERIAL_NO排序，可折叠，一般为三级分类\n该模块支持对检查项目分类的【新增】【停用】以及【刷新】\n各科室进入页面，只能在页面看到自己科室的分类，例如放射科进入页面，只能看到“放射"分类，超声科进入页面，只能看到“超声”分类（一级分类由系统预设，增加应用参数维护该工作站可见的检查项目一级分类，根据科室进行维护即可）\n\n1.1 新增\n1.1.1 功能详细说明\n新增顶级分类\n当鼠标未选中检查项目分类，直接点击【新增】按钮时，则为新增顶级分类\n【新增】按钮点击后，检查类别详细信息tab页显示如下图所示\n填写好信息后，点击页面底部【保存】按钮，调用项目分类新增接口\n\n\n点击图片可查看完整电子表格\n新增子级分类\n当鼠标选中检查项目分类，点击【新增】按钮时，则为新增子级分类\n【新增】按钮点击后，检查类别详细信息tab页显示如下图所示\n填写好信息后，点击页面底部【保存】按钮，调用项目分类新增接口\n\n\n点击图片可查看完整电子表格\n1.1.2 接口流程图\n\n1.1.3 数据流\n新增：检查类别字典EXAM_CLASS_DICT(clinic\exam\exam_class_dictionary)\n\n点击图片可查看完整电子表格\n新增：检查分类扩展表EXAM_CLASS_DICT_EXTEND(clinic\clinic_dictionary\exam\exam_class_dictionary_extension)\n\n点击图片可查看完整电子表格\n1.2 编辑\n1.2.1 功能详细说明\n该功能没有单独的【编辑】按钮，左侧鼠标选中任意分类，右侧检查类别详细信息tab页就显示该分类的信息，直接修改后点击【保存】按钮即为编辑\n编辑时的控件、布局、交互和新增时相同，不再贴图说明，唯一不同的是，“类别编码”不可编辑\n\n点击图片可查看完整电子表格\n1.2.2 接口流程图\n\n1.2.3 数据流\n修改：检查类别字典 EXAM_CLASS_DICT(clinic\exam\exam_class_dictionary)\n新增/删除/修改：检查分类扩展表EXAM_CLASS_DICT_EXTEND(clinic\clinic_dictionary\exam\exam_class_dictionary_extension)\n\n点击图片可查看完整电子表格\n1.3 停用\n1.3.1 功能详细说明\n鼠标单击选中选中某一检查项目分类，点击【停用】按钮，弹出确认弹窗，弹窗点击【确定】，调用停用接口，点击【取消】关闭弹窗\n\n1.3.2 接口流程图\n\n\n停用分类下所有检查项目，详见检查项目维护 \n1.3.3 数据流\n修改：检查类别字典 EXAM_CLASS_DICT(clinic\exam\exam_class_dictionary)\n\n点击图片可查看完整电子表格\n1.4 刷新\n1.4.1 功能详细说明\n点击【刷新】按钮，刷新左侧树状检查项目分类，页面回到初始状态\n"
},
{
"section":"2.执行科室维护",
"content":" \n此界面用于维护各级检查分类的执行科室\n\n2.1.1 功能详细说明\n整体交互：\n执行科室维护tab页分为左右两块区域，左侧为科室检索控件，右侧为显示已选科室区域\n鼠标选中某一分类后进入该tab页，左侧显示该分类使用院区的所有科室列表，右侧显示该分类已维护的执行科室\n勾选左侧科室点击【>>】按钮，科室来到已选科室列表，再点击【保存】按钮即为新增，左侧科室不能重复加入右侧\n勾选右侧已选科室点击【<<】按钮，科室从已选科室列表移除，再点击【保存】按钮即为删除\n右侧已选科室列表修改优先级再点击【保存】按钮即为编辑\n左右两侧的科室可以多选批量操作\n\n科室检索控件：\n数据源\n初始化查询\n默认按上述sql查询出所选分类的使用院区的科室\n检索条件\n\n点击图片可查看完整电子表格\n列表字段\n列表的科室名称按 “科室名称（院区名称）”拼接显示\n\n\n已选科室列表：\n数据源\n列表字段\n\n点击图片可查看完整电子表格\n2.1.2 数据流\n新增：\n新增：检查类别与执行科室对照表EXAM_VS_DEPT(clinic\clinic_dictionary\exam\exam_vs_department) \n\n点击图片可查看完整电子表格\n删除：\n删除科室时，删除表中该检查类别代码下该执行科室代码的数据\n删除：检查类别与执行科室对照表EXAM_VS_DEPT(clinic\clinic_dictionary\exam\exam_vs_department) \n编辑：\n修改：检查类别与执行科室对照表EXAM_VS_DEPT(clinic\clinic_dictionary\exam\exam_vs_department) \n"
},
{
"section":"3.检查部位字典维护",
"content":"此界面用于维护各检查一级分类的检查部位字典\n鼠标选中某一级分类后进入该tab页，显示该分类已维护的检查部位字典\n\n3.1 列表\n数据源\n列表字段\n\n点击图片可查看完整电子表格\n3.2 新增\n\n3.2.1 功能详细说明\n直接点击【新增】按钮，列表底部出现一行空白行，填写后点击【保存】，调用检查部位字典新增接口\n\n点击图片可查看完整电子表格\n3.2.2 接口流程图\n\n3.2.3 数据流\n新增： 检查部位字典EXAM_BODYS_DICT(clinic\clinic_dictionary\exam\exam_body_dictionary)\n\n点击图片可查看完整电子表格\n3.3 编辑\n\n3.3.1 功能详细说明\n鼠标单击选中一行后点击【编辑】按钮或者直接鼠标双击该行，都可进入编辑状态，填写后点击【保存】，调用检查部位字典编辑接口\n\n点击图片可查看完整电子表格\n3.3.2 数据流\n修改： 检查部位字典EXAM_BODYS_DICT(clinic\clinic_dictionary\exam\exam_body_dictionary)\n3.4 删除\n3.4.1 功能详细说明\n鼠标单击选中某一行，点击【删除】按钮，弹出确认弹窗，弹窗点击【确定】，调用删除接口，点击【取消】关闭弹窗\n删除未保存的前端缓存数据时，不需要弹窗提醒\n\n3.4.2 数据流\n删除： 检查部位字典EXAM_BODYS_DICT(clinic\clinic_dictionary\exam\exam_body_dictionary)\n"
}
]}
'''
split_text_prompt+='\n只需要给出json格式回答，其余任何多余的文字都不要输出.'

def split_when_greater_1k(doc_contents):
    global split_text_prompt
    
    short_doc_contents=[]
    for doc in doc_contents:
        if len(doc)<=1000:
            short_doc_contents.append(doc)
        else:
           result=call_gpt_json(user=doc,sys=split_text_prompt)
           for item in result['sections']:
                short_doc_contents.append(item)
    return short_doc_contents

def split_single_doc_when_greater_1k(doc):
    global split_text_prompt
    
    short_doc_contents=[]

    if len(doc)<=1000:
        short_doc_contents.append(doc)
    else:
        result=call_gpt_json(user=doc,sys=split_text_prompt)
        for item in result['sections']:
            short_doc_contents.append(item)
    return short_doc_contents
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
