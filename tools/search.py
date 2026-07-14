# tools/search.py
import os

import serpapi

def web_search(query: str, max_results: int = 3) -> str:
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        return "搜索出错：缺少 SERPAPI_KEY 环境变量"

    params = {
        "engine" : "duckduckgo",
        "q" : query,
        "api_key": api_key,
        "num": max_results,
    }
    try:
        client = serpapi.Client(api_key=api_key)
        response = client.search(params)
        data = response.get("organic_results",[])

        results = []
        for result in data:
            title = result.get("title")
            snippet = result.get("snippet")
            results.append(f"标题:{title}")
            results.append(f"部分内容:{snippet}")
        if results:
            return "\n".join(results)
        else:
            return f"没有找到关于「{query}」的搜索结果"
    except Exception as e:
        return f"搜索出错：{e}"
