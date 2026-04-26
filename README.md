<p align="center">
  <img src="https://em-content.zobj.net/source/apple/391/speech-balloon_1f4ac.png" width="120" />
</p>

<h1 align="center">justaskit</h1>

<p align="center">
  <strong>upload csv → ask question → get answer. that's it.</strong>
</p>

<p align="center">
  <a href="https://github.com/lastejhenpames/justaskit/stargazers"><img src="https://img.shields.io/github/stars/lastejhenpames/justaskit?style=flat&color=yellow&cacheSeconds=0" alt="Stars"></a>
  <a href="https://github.com/lastejhenpames/justaskit/commits/main"><img src="https://img.shields.io/github/last-commit/lastejhenpames/justaskit?style=flat&cacheSeconds=0" alt="Last Commit"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/lastejhenpames/justaskit?style=flat&color=blue&cacheSeconds=0" alt="License"></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Next.js-15-000000?style=flat&logo=next.js&logoColor=white" alt="Next.js">
  <img src="https://img.shields.io/badge/LangGraph-FF6B6B?style=flat" alt="LangGraph">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white" alt="Docker">
</p>

<p align="center">
  <a href="#what-it-do">what it do</a> •
  <a href="#quick-start">quick start</a> •
  <a href="#how-it-works">how it works</a> •
  <a href="#tech-stack">stack</a> •
  <a href="#deploy">deploy</a>
</p>

---

## what it do

most data tools make you learn sql or click through 47 menus. this one? just ask.

```
you: "show me top 3 products by revenue"

copilot: *generates pandas code*
         *runs it safely*
         *makes you a chart*
         *explains what it means*
         
         done in 8 seconds.
```

**what you get:**
- 🧠 multi-agent system (analysis + viz + insights working together)
- 👀 full transparency (see the code it generates)
- 📊 interactive charts (visx, not some crusty matplotlib)
- ⚡ actually fast (5-15s including LLM calls)
- �p docker ready (one command deploy)

**what you don't need:**
- sql knowledge ❌
- python knowledge ❌
- data science degree ❌
- 3 hour tutorial ❌

---

## before / after

<table>
<tr>
<td width="50%">

### normal bi tools

1. import data (15 clicks)
2. create connection (configure 8 fields)
3. build query (learn proprietary syntax)
4. make visualization (drag drop pray)
5. export to share (another 10 clicks)

time: 30 minutes  
frustration: maximum

</td>
<td width="50%">

### justaskit

1. upload csv
2. ask "top 3 products by revenue"
3. get answer + chart

time: 8 seconds  
frustration: zero

</td>
</tr>
</table>

---

## quick start

### you need
- Python 3.12+
- Node.js 20+
- [OpenRouter API key](https://openrouter.ai/keys) (free tier works)

### backend (2 minutes)

```bash
cd backend

# make venv
python -m venv venv
source venv/bin/activate  # windows: venv\Scripts\activate

# install stuff
pip install -r requirements.txt

# add your api key
cp .env.example .env
# edit .env, paste your OpenRouter key

# run it
uvicorn app.main:app --reload
```

backend lives at `http://localhost:8000`

### frontend (1 minute)

```bash
cd frontend

npm install
npm run dev
```

frontend lives at `http://localhost:3000`

### try it

1. go to `http://localhost:3000`
2. upload `test_data/sample_sales.csv`
3. ask stuff:
   - "what's the total revenue?"
   - "show me top 3 products by revenue"
   - "which region has highest sales?"

---

## how it works

```
                    your question
                         │
                         ▼
              ┌──────────────────┐
              │   orchestrator   │
              │  (the conductor) │
              └────────┬─────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   ┌────────┐     ┌────────┐    ┌────────┐
   │analysis│     │  viz   │    │insight │
   │ agent  │     │ agent  │    │ agent  │
   │        │     │        │    │        │
   │writes  │     │makes   │    │explains│
   │pandas  │     │charts  │    │in plain│
   │code    │     │        │    │english │
   └────────┘     └────────┘    └────────┘
        │              │              │
        └──────────────┴──────────────┘
                       │
                       ▼
            📊 answer + chart + code
```

**the agents:**
1. **analysis agent** — writes pandas code, runs it safely
2. **visualization agent** — makes interactive charts (when needed)
3. **insight agent** — explains what it means in human words

**why this is cool:**
- you see the code it generates (trust but verify)
- agents specialize (better than one agent doing everything)
- if something breaks, you know which agent messed up

---

## example

**query:** "show me top 3 products by revenue with a chart"

**what happens:**

```python
# analysis agent writes this
df.groupby('product')['revenue'].sum().nlargest(3)

# result
Laptop     $6,000
Desk       $1,350
Monitor    $900
```

**visualization agent makes chart:**
```
📊 interactive bar chart appears
```

**insight agent explains:**
```
"Laptop dominates with $6,000 revenue (67% of top 3). 
Consider expanding laptop inventory."
```

**time:** 8.5 seconds  
**agents used:** analysis → visualization → insight  
**you:** happy

---

## tech stack

### backend
- **FastAPI** — fast python web framework
- **LangGraph** — multi-agent orchestration
- **OpenRouter** — llm api (gpt-4, claude, etc)
- **pandas** — data crunching
- **SQLite** — stores your datasets

### frontend
- **Next.js 15** — react but better
- **shadcn/ui** — pretty components
- **visx** — interactive charts (by airbnb)
- **Tailwind** — makes it look good

### why these?
- all modern (2026 stack)
- all production-ready
- all actually good
- no legacy garbage

---

## features

### multi-agent system
- 3 specialized agents
- orchestrator routes between them
- each agent does one thing well

### data analysis
- natural language queries
- auto-generates pandas code
- safe execution (no eval() nonsense)
- interactive visualizations

### transparency
- see generated code
- track which agents ran
- execution time shown
- errors explained clearly

### production ready
- health checks (`/health`, `/ready`, `/metrics`)
- structured logging
- error handling
- docker support
- api docs auto-generated

---

## deploy

### option 1: docker (easiest)

```bash
# set your api key
export OPENAI_API_KEY=your-key
export OPENAI_BASE_URL=https://openrouter.ai/api/v1
export OPENAI_MODEL=openai/gpt-4o-mini

# run it
docker-compose up -d

# check it
curl http://localhost:8000/health
```

### option 2: railway (one click)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

### option 3: manual

see [DEPLOYMENT.md](DEPLOYMENT.md) for:
- railway
- render
- aws
- vercel (frontend)

---

## api

| endpoint | what it do |
|----------|------------|
| `/api/upload` | upload csv/excel |
| `/api/query` | ask questions |
| `/health` | is it alive |
| `/ready` | is it ready |
| `/metrics` | system stats |
| `/docs` | interactive api docs |

---

## project structure

```
.
├── backend/
│   ├── app/
│   │   ├── agents/          # the brain
│   │   ├── api/             # the endpoints
│   │   ├── core/            # the plumbing
│   │   └── main.py          # the entry point
│   └── requirements.txt
├── frontend/
│   ├── app/                 # next.js pages
│   ├── components/          # ui components
│   └── package.json
├── test_data/               # sample csv
└── docker-compose.yml       # one command deploy
```

---

## performance

```
┌─────────────────────────────────────┐
│  Query Response      ████░░ 5-15s   │
│  File Upload         █████░ <1s     │
│  Concurrent Users    ████░░ 4+      │
│  Vibes               ██████ immac   │
└─────────────────────────────────────┘
```

---

## what this shows

**for portfolio/interviews:**

- **ai engineering** — multi-agent orchestration, prompt engineering, llm integration
- **backend** — fastapi, async patterns, middleware, logging
- **frontend** — modern next.js, component design, data viz
- **system design** — agent architecture, error handling, production thinking
- **devops** — docker, health checks, deployment

basically: you know how to build real stuff, not just tutorials.

---

## roadmap

- [ ] export results (pdf, csv, excel)
- [ ] save queries/datasets
- [ ] database connectors (postgres, mysql)
- [ ] scheduled reports
- [ ] collaboration features
- [ ] predictive analytics
- [ ] more chart types

---

## why this exists

built this to show i can:
1. design multi-agent systems
2. build production-ready apis
3. create modern frontends
4. deploy real applications
5. write code that doesn't suck

if you're hiring, [let's talk](https://github.com/lastejhenpames).

---

## contributing

this is a portfolio project but if you want to:
1. fork it
2. make it better
3. send pr
4. ???
5. profit

---

## license

MIT — do whatever you want with it

---

## built with

- [FastAPI](https://fastapi.tiangolo.com/) — modern python web
- [LangGraph](https://github.com/langchain-ai/langgraph) — multi-agent magic
- [Next.js](https://nextjs.org/) — react framework
- [shadcn/ui](https://ui.shadcn.com/) — beautiful components
- [visx](https://airbnb.io/visx/) — data viz by airbnb
- [OpenRouter](https://openrouter.ai/) — llm access

---

<div align="center">

### ⭐ if this helped you, star it

made with 🧠 to show what's possible in 2026

[⬆ back to top](#justaskit)

</div>
