# main.py
from agent import Agent
from executor import execute_plan
from planner import make_plan,print_plan

def main() -> None:
    print("=== 我的第一个 Agent ===")
    print("输入 quit 退出\n")

    agent = Agent()

    while True:
        user_input = input("你：").strip()

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("再见！")
            break
        if user_input.lower() == "/clear":
            agent.clear()
            print("记忆已清除，开始新对话。\n")
            continue
        if user_input.startswith("/plan",0,5):
            task = user_input[6:].strip()
            result = agent.chat(task)
            print(f"Agent：{result}")
            plan = make_plan(result)
            print_plan(plan)
            confirm = input("\n确认执行？(y/n):").strip().lower()
            if confirm == "y":
                result = execute_plan(plan)
                print(f"\nagent:{result}\n")
            else:
                print("已取消。\n")
            print(f"（当前记忆：{agent.memory.count()} 条消息）\n")
            continue
        result = agent.chat(user_input)  
        print(f"Agent：{result}")
        print(f"（当前记忆：{agent.memory.count()} 条消息）\n")
        continue

if __name__ == "__main__":
    main()