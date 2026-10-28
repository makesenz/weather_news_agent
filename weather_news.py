"""AutoGen Weather News Agent.

Asks the user for a city, searches today's weather news with the keyless
DuckDuckGo search package (ddgs), and replies in exactly 3 short lines.
"""

import asyncio
import os

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from ddgs import DDGS
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("MODEL", "gpt-4o-mini")

SYSTEM_MESSAGE = (
    "You are a weather news reporter. For any city the user names, ALWAYS call "
    "the search_weather_news tool first, then answer using only those results. "
    "Reply in exactly 3 short lines separated by line breaks, one short "
    "sentence per line (under 20 words), no bullets, no numbering, no headings: "
    "line 1 = today's current conditions, line 2 = temperature or notable "
    "details, line 3 = what to expect later or any alerts. Never merge them into "
    "one paragraph. If the results are thin, say so honestly instead of "
    "inventing numbers."
)


def search_weather_news(city: str) -> str:
    """Search the web for TODAY'S weather news and forecast for a city.

    Use this tool whenever the user asks about current weather, rain, heat,
    storms, temperature or weather alerts in a specific city. It is not for
    general facts, history or trivia about the city.

    Args:
        city: Name of the city, e.g. "Chennai" or "London".

    Returns:
        Up to 5 recent news results (title, date, source and snippet) as text.
    """
    try:
        results = DDGS().news(query=f"{city} weather today", max_results=5)
    except Exception as exc:  # network errors or rate limits from DuckDuckGo
        return f"Search failed: {exc}"
    if not results:
        return f"No weather news found for {city} today."
    return "\n\n".join(
        f"Title: {r.get('title')}\nDate: {r.get('date')}\n"
        f"Source: {r.get('source')}\nSnippet: {r.get('body')}"
        for r in results
    )


def build_agent(model_client: OpenAIChatCompletionClient) -> AssistantAgent:
    return AssistantAgent(
        name="weather_news",
        model_client=model_client,
        tools=[search_weather_news],
        system_message=SYSTEM_MESSAGE,
        reflect_on_tool_use=True,
    )


def build_task(city: str) -> str:
    return f"What is the weather news in {city} today? Reply in exactly 3 short lines."


async def main() -> None:
    city = input("Which city? ").strip()
    model_client = OpenAIChatCompletionClient(model=MODEL)
    try:
        agent = build_agent(model_client)
        await Console(agent.run_stream(task=build_task(city)))
    finally:
        await model_client.close()


if __name__ == "__main__":
    asyncio.run(main())
