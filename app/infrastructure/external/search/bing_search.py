#!/usr/bin/eny python
# -*- coding: utf-8 -*-
"""
@Time    :2025/12/10 22:57
#Author  :Emcikem
@File    :bing_search.py
"""
import logging
import re
import time
from typing import Optional

import httpx
from bs4 import BeautifulSoup

from app.domain.external.search import SearchEngine
from app.domain.models.search import SearchResults, SearchResultItem
from app.domain.models.tool_result import ToolResult

logger = logging.getLogger(__name__)


class BingSearchEngine(SearchEngine):
    """bing搜索引擎"""

    def __init__(self):
        """构造函数，初始化bing搜索引擎的相关信息"""
        self.base_url = "https://www.bing.com/search"
        self.headers = {
            "User-Agent": "",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        self.cookies = httpx.Cookies()

    async def invoke(self, query: str, date_range: Optional[str] = None) -> ToolResult[SearchResults]:
        """根据传递的query+date_range调用bing搜索获取搜索内容"""
        # 1.构建请求参数
        params = {"q": query}

        # 2.判断date_range是否存在并提取真实数据
        if date_range and date_range != "all":
            # 3.获取当前日期距离1970-01-01的天数
            days_since_epoch = int(time.time() / (24 * 60 * 60))

            # 4.创建日期检索数据类型映射
            date_mapping = {
                "past_hour": "ex1%3a\"ez1\"",
                "past_day": "ex1%33a\"ez1\"",
                "past_week": "ex1%3a\"ez2\"",
                "past_month": "ex1%3a\"ez3\"",
                "past_year": f"ex1%3a\"ez5_{days_since_epoch - 365}_{days_since_epoch}"
            }

            # 5.判断是否传递了date_range并且在date_mapping中可以找到
            if date_range in date_mapping:
                params["filters"] = date_mapping[date_range]

            try:
                # 6.使用httpx创建一个异步客户端上下文
                async with httpx.AsyncClient(
                        headers=self.headers,
                        cookies=self.cookies,
                        timeout=60,
                        follow_redirects=True,
                ) as client:
                    # 7.调用客户端发起请求
                    response = await client.get(self.base_url, params=params)
                    response.raise_for_status()

                    # 8.更新cookie信息
                    self.cookies.update(response.cookies)

                    # 9.使用bs4解析html内容
                    soup = BeautifulSoup(response.text, "html.parser")

                    # 10.定义搜索结果并解析li.b_algo对应的dom元素
                    search_results = []
                    result_items = soup.find_all("li", class_="b_algo")

                    # 11.循环遍历所有匹配的元素
                    for item in result_items:
                        try:
                            # 12.定义变量存储标题+url链接
                            title, url = ("", "")
                            title_tag = item.find("h2")
                            if title_tag:
                                a_tag = title_tag.find("a")
                                if a_tag:
                                    title = a_tag.get_text(strip=True)
                                    url = a_tag.get("href", "")

                            # 14.判断标题是否存在，如果不存在则提取该dom下a标签的href+text作为标题和链接
                            if not title:
                                a_tag = item.find_all("a")
                                for a_tag in a_tag:
                                    # 15.提取标签中的文本并判断长度是否大于10
                                    text = a_tag.get_text(strip=True)
                                    if len(text) > 10 and not text.startswith("http"):
                                        title = text
                                        url = a_tag.get("href", "")
                                        break

                            # 16.如果用两种方式还是没有标题
                            if not title:
                                continue

                            # 17.提取检索条目的摘要信息
                            snippet = ""
                            snippet_items = item.find_all(
                                ["p", "div"],
                                class_=re.compile(r"b_lineclamp|b_descript|b_caption"),
                            )
                            if snippet_items:
                                snippet = snippet_items[0].get_text(strip=True)

                            # 18.如果这个情况还找不到摘要则查询所有的p标签，同时获取文本内容，并判断内容长度是否大于20
                            if not snippet:
                                p_tags = item.find_all("p")
                                for p in p_tags:
                                    text = p.get_text(strip=True)
                                    if len(text) > 20:
                                        snippet = text
                                        break

                            # 19.如果还找不到摘要信息，可以提起元素下的所有文本，并使用常记的分割符进行分割，例如: .!。\n?等等
                            if not snippet:
                                all_text = item.get_text(strip=True)

                                # 20.将所有文本按常记的句子结尾标识进行拆分
                                sentences = re.split(r"[.!?\n。！]]", all_text)
                                for sentence in sentences:
                                    clean_sentence = sentence.strip()
                                    if len(clean_sentence) > 20 and clean_sentence != title:
                                        snippet = clean_sentence
                                        break

                            # 21.补全相对路径的url链接或者是缺失的协议
                            if url and not url.startswith("http"):
                                if url.startswith("//"):
                                    url = "https:" + url
                                elif url.startswith("/"):
                                    url = "https://www.bing.com" + url

                            # 22.如果标题和链接都存在则添加数据
                            search_results.append(SearchResultItem(
                                url=url,
                                title=title,
                                snippet=snippet,
                            ))
                        except Exception as e:
                            # 单挑搜索信息出错则记录日志并跳过该条数据
                            logger.warning(f"Bing搜索结果解析失败: {str(e)}")
                            continue

                    # 24.提取整个页面的内容并查找`results`对应的文本
                    total_results = 0
                    result_status = soup.find_all(string=re.compile(r"\d+[,\d+]\s*results"))
                    if result_status:
                        for stat in result_status:
                            # 25.匹配厨对应的数字分组
                            match = re.search(r"([\d,]+)\s*results", stat)
                            if match:
                                try:
                                    # 26.取出匹配的分组内容，去除逗号后转换为整型
                                    total_results = int(match.group(1).replace(",", ""))
                                    break
                                except Exception as e:
                                    continue

                    # 27.如果使用正则匹配找不到results（可能是页面不一致导致的）则使用新逻辑
                    if total_results == 0:
                        # 28.使用类元素查找器
                        count_elements = soup.find_all(
                            ["span", "p", "div"],
                            class_=re.compile(r"sb_count|b_focusTextMedium"),
                        )
                        for element in count_elements:
                            # 29.提取dom的文本并获取数字
                            text = element.get_text(strip=True)
                            match = re.search(r"([\d,]+)\s*results", text)
                            if match:
                                try:
                                    total_results = int(match.group(1).replace(",", ""))
                                    break
                                except Exception as e:
                                    continue
                    # 30.以及有对应结果了则直接返回ToolResult
                    results = SearchResults(
                        query=query,
                        date_range=date_range,
                        total_results=total_results,
                        results=search_results,
                    )
                    return ToolResult(success=True, data=results)
            except Exception as e:
                # 31.记录下异常信息
                logger.error(f"Bing搜索出错: {str(e)}")
                error_results = SearchResults(
                    query=query,
                    date_range=date_range,
                    total_results=0,
                    results=[],
                )
                return ToolResult(
                    success=False,
                    message=f"Bing搜索出错: {str(e)}",
                    data=error_results,
                )


if __name__ == "__main__":
    import asyncio


    async def test():
        search_engine = BingSearchEngine()
        result = await search_engine.invoke("gemini", "past_day")

        print(result)
        for item in result.data.results:
            print(item)


    asyncio.run(test())
