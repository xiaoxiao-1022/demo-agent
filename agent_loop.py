# agent_loop.py
import json
import re
from llm import chat
from tool_registry import get_tools_description, execute_tool
from memory.short_term import ShortTermMemory

REACT_SYSTEM_PROMPT = """你是一个能完成复杂任务的智能助手，可以反复使用工具直到任务完成。

{tools_description}

每次回复必须是 JSON，三种格式之一：

1. 需要使用工具（可以多次使用）：
{{"type": "tool_call", "tool": "工具名", "params": {{"参数名": "参数值"}}, "thought": "我为什么用这个工具"}}

2. 任务已完成：
{{"type": "final_answer", "content": "最终答案内容"}}

3. 需要向用户提问：
{{"type": "ask_user", "question": "你的问题"}}

规则：
- 最多使用工具 {max_steps} 次
- 收集到足够信息后，必须给出 final_answer
- 不要用相同参数重复调用同一个工具
- 只返回 JSON"""


def safe_parse_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {"type": "final_answer", "content": text}


class ReactAgent:
    def __init__(self, max_steps: int = 5) -> None:
        self.max_steps = max_steps

    def run(self, user_task: str) -> str:
        """运行 ReAct 循环完成任务，返回最终答案。"""
        # 每次任务新建一个记忆实例（不跨任务保留中间步骤）
        memory = ShortTermMemory(max_messages=40)
        memory.add("system", REACT_SYSTEM_PROMPT.format(
            tools_description=get_tools_description(),
            max_steps=self.max_steps,
        ))
        memory.add("user", f"请帮我完成这个任务：{user_task}")

        for step in range(1, self.max_steps + 1):
            print(f"\n{'─'*40}")
            print(f"[步骤 {step}/{self.max_steps}]")

            ai_response = chat(memory.to_api_format())
            print(f"[AI 思考]: {ai_response}")
            memory.add("assistant", ai_response)

            decision = safe_parse_json(ai_response)
            resp_type = decision.get("type")

            # 任务完成
            if resp_type == "final_answer":
                print(f"[任务完成，共 {step} 步]")
                return decision.get("content", "（无内容）")

            # 使用工具
            if resp_type == "tool_call":
                tool_name = decision.get("tool", "")
                params    = decision.get("params", {})
                thought   = decision.get("thought", "")
                print(f"[调用工具]: {tool_name}")
                if thought:
                    print(f"[理由]: {thought}")
                result = execute_tool(tool_name, params)
                # 只打印前300字，避免终端被刷屏
                preview = result[:300] + "..." if len(result) > 300 else result
                print(f"[工具结果]: {preview}")
                # 把工具结果作为"观察"加入记忆
                memory.add("user", f"工具 {tool_name} 返回结果：\n{result}")
                continue

            # 向用户提问
            if resp_type == "ask_user":
                question = decision.get("question", "")
                user_answer = input(f"\nAgent 问你：{question}\n你：")
                memory.add("user", user_answer)
                continue

            # 未知类型，结束
            return str(decision)

        # 达到步骤上限，强制要求给出答案
        print(f"\n[已达步骤上限 {self.max_steps}，要求给出最终答案]")
        memory.add("user", "你已用完所有步骤，请立即基于已有信息给出最终答案。")
        final_response = chat(memory.to_api_format())
        final = safe_parse_json(final_response)
        return final.get("content", final_response)