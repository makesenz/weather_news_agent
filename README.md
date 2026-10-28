# 🌦️ AutoGen Weather News Agent

Week 5 · Day 2 assignment. An AutoGen agent that takes a city from the user, searches today's weather news with the free, keyless DuckDuckGo search package (`ddgs`), and replies in **exactly 3 short lines**.

It also includes a **Streamlit frontend** as an extra.

## ⚙️ Tech Stack

- Python
- AutoGen (`autogen-agentchat`, `autogen-ext[openai]`)
- `ddgs` (DuckDuckGo search, no API key needed)
- OpenAI `gpt-4o-mini`
- Streamlit (frontend)
- python-dotenv

## 📁 Project Structure

```text
autogen-weather-news-agent/
├── weather_news.py     # The assignment: tool + agent + terminal app
├── app.py              # Streamlit frontend (reuses weather_news.py)
├── requirements.txt
├── .env.example
└── README.md
```

## 🚀 Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # then put your OpenAI key in .env
```

## ▶️ Run (terminal, the assignment version)

```bash
python weather_news.py
```

```text
Which city? Chennai
---------- ToolCallRequestEvent (weather_news) ----------
[FunctionCall(... name='search_weather_news', arguments='{"city":"Chennai"}')]
---------- ToolCallExecutionEvent (weather_news) ----------
...
---------- TextMessage (weather_news) ----------
<line 1: today's conditions>
<line 2: temperature / details>
<line 3: what to expect later / alerts>
```

Try two cities and check that the lines really change.

## 🖥️ Run (Streamlit frontend)

```bash
streamlit run app.py
```

Enter a city and click **Get news**. Each answer card shows the 3-line reply, the tool call the agent made, and the raw search results in an expander. Earlier cities stay on the page so you can compare them.

## 🧠 How it works

- `search_weather_news(city: str) -> str` is a plain Python function. AutoGen turns its **name, type hints and docstring** into a tool schema for the model.
- The function is passed to the agent with `tools=[search_weather_news]`.
- `reflect_on_tool_use=True` makes the agent make a second model call that turns the search results into a written answer.
- The model client is closed at the end, and the API key comes from an environment variable (`.env`).

## 💭 Think it through

**What makes the docstring clearly about today's weather news, not trivia?**
It says *when* to use the tool ("current weather, rain, heat, storms, temperature or weather alerts in a specific city"), says what it is *not* for ("not for general facts, history or trivia"), and describes the argument and the return value. The system message also tells the agent to always call the tool first.

**What would the agent print if `reflect_on_tool_use` were off?**
It would stop after running the tool and return a `ToolCallSummaryMessage`: the raw search-result text, not a 3-line answer written by the model.
