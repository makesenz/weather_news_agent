"""Streamlit frontend for the AutoGen Weather News Agent.

Run with:  streamlit run app.py
"""

import asyncio
import os

import streamlit as st
from autogen_agentchat.messages import (
    TextMessage,
    ToolCallExecutionEvent,
    ToolCallRequestEvent,
)
from autogen_ext.models.openai import OpenAIChatCompletionClient

from weather_news import MODEL, build_agent, build_task

st.set_page_config(page_title="Weather News Agent", page_icon="🌦️", layout="centered")

st.title("🌦️ AutoGen Weather News Agent")
st.caption("Type a city. The agent searches today's weather news with DuckDuckGo and replies in 3 short lines.")

if not os.getenv("OPENAI_API_KEY"):
    st.error("OPENAI_API_KEY is not set. Add it to a `.env` file in this folder and restart the app.")
    st.stop()

if "history" not in st.session_state:
    st.session_state.history = []


async def ask_agent(city: str) -> dict:
    """Run the agent once and collect the tool call, tool output and final reply."""
    model_client = OpenAIChatCompletionClient(model=MODEL)
    run = {"city": city, "tool_calls": [], "tool_results": [], "reply": "", "usage": None}
    try:
        agent = build_agent(model_client)
        async for event in agent.run_stream(task=build_task(city)):
            if isinstance(event, ToolCallRequestEvent):
                run["tool_calls"] += [f"{c.name}({c.arguments})" for c in event.content]
            elif isinstance(event, ToolCallExecutionEvent):
                run["tool_results"] += [r.content for r in event.content]
            elif isinstance(event, TextMessage) and event.source == agent.name:
                run["reply"] = event.content
                if event.models_usage:
                    run["usage"] = event.models_usage.prompt_tokens + event.models_usage.completion_tokens
    finally:
        await model_client.close()
    return run


def show_run(run: dict) -> None:
    with st.container(border=True):
        st.subheader(f"📍 {run['city']}")
        lines = [line for line in run["reply"].splitlines() if line.strip()]
        for line in lines:
            st.markdown(f"- {line}")
        if run["tool_calls"]:
            st.caption("🔧 Tool call: " + ", ".join(f"`{c}`" for c in run["tool_calls"]))
        else:
            st.caption("⚠️ The agent answered without calling the search tool.")
        with st.expander("Raw search results"):
            for result in run["tool_results"]:
                st.text(result)
        if run["usage"]:
            st.caption(f"Model: {MODEL} · {run['usage']} tokens")


with st.form("city_form", clear_on_submit=True):
    col1, col2 = st.columns([4, 1], vertical_alignment="bottom")
    city = col1.text_input("Which city?", placeholder="e.g. Chennai")
    submitted = col2.form_submit_button("Get news", use_container_width=True)

if submitted:
    if not city.strip():
        st.warning("Please enter a city name.")
    else:
        with st.spinner(f"Searching today's weather news for {city.strip()}..."):
            try:
                st.session_state.history.insert(0, asyncio.run(ask_agent(city.strip())))
            except Exception as exc:
                st.error(f"Something went wrong: {exc}")

for past_run in st.session_state.history:
    show_run(past_run)

if st.session_state.history:
    if st.button("Clear history"):
        st.session_state.history = []
        st.rerun()
