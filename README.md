# Learning Command Center

Personal Streamlit app to track Data Engineering / ML / DS learning resources using DuckDB as a local store.

## Vision

To create a comprehensive personal learning management system that empowers Data Engineering, Data Science, and Machine Learning professionals to:
- Systematically track and organize learning resources across DE/DS/ML domains
- Monitor personal expertise progression in key technologies and tools
- Maintain accountability through study session logging and progress visualization
- Plan structured learning paths based on career goals and current skill levels
- Achieve continuous professional development in the rapidly evolving data field

## Resource Updates

### Summary of Changes Made

| # | Title Added | Why It Was Added | Category Gap Filled |
|---|-------------|------------------|---------------------|
| 1 | Python for Data Science, AI & Development | Your original list had Python mentioned in composite courses but lacked a dedicated, structured Python foundation. This IBM course covers pandas, APIs, and basic scripting—critical before you write Airflow DAGs or Spark jobs. | Python Basics |
| 2 | Docker Tutorial for Beginners (Mosh) | Docker is tagged in Zoomcamp but can be a steep learning curve. This concise, visual tutorial is specifically noted as a pre‑Zoomcamp primer. It prevents you from getting stuck on Week 1 environment issues. | Containerization / DevOps |
| 3 | dbt Fundamentals | You tagged dbt but had no resource for it. dbt is the industry standard for transformations inside BigQuery/Snowflake. This official free course pairs perfectly with Zoomcamp Week 4. | Analytics Engineering |
| 4 | AWS Data Engineering (3‑Hour) | Zoomcamp uses GCP. The market is split between AWS and GCP. This short, free video gives you exposure to AWS equivalents (Glue/Athena) so you can translate your skills across clouds without paying for another full certification. | Multi‑Cloud Awareness |
| 5 | Git and GitHub Crash Course | Not a DE tool per se, but essential for employability. You need to push your Zoomcamp homework to GitHub to create a portfolio. This ensures you don't just code locally and lose it. | Version Control |

**Advisory Note on Using the Updated JSON**  
Do not try to consume all 21 resources linearly.  
Use the Phase 1 → Phase 2 → Phase 3 approach outlined earlier. The new entries are enablers for the main course (Zoomcamp).

**Next Step:**  
I recommend you start with entry #17 (Docker Tutorial) followed immediately by entry #1 (Zoomcamp Overview) . The rest of the list is your reference library for when you hit a specific tool week (e.g., pull up the dbt course when you reach Week 4 of Zoomcamp).

**Practical Project Integration Advice**  
The biggest mistake learners make is resource hoarding (collecting 50 links but never building). Here is a concrete plan using only free resources from your list + the additions:

**Setup Environment (Free):**

- Install VS Code, Docker Desktop (free), Git, and Python 3.10.
- Create a GitHub Repo named data-engineering-zoomcamp-2026.

**Follow the Zoomcamp Modules (Week-by-Week):**

- Week 1: Docker + Terraform (Use the Mosh Docker video if stuck).
- Week 2: Workflow Orchestration (Airflow).
- Week 3: Data Warehouse (BigQuery). Important: Set a GCP Budget Alert to $1 to avoid surprise charges. Stick to free tier datasets (NYC Taxi).
- Week 4: Analytics Engineering (dbt). Use the dbt Fundamentals course link above in parallel.
- Week 5-6: Batch Processing (Spark).
- Week 7-8: Streaming (Kafka).

**The "Interview-Ready" Modification:**

After completing the Zoomcamp, change the data source. Instead of NYC Taxi data, use a free API (e.g., OpenWeatherMap free tier or CoinGecko Crypto API).

Ingest that data into GCP using Airflow.

Transform it with dbt.

This shows you can apply the tools, not just follow a tutorial.

- ✅ Resource management: Add, browse, filter, and update learning resources (courses, articles, videos, etc.)
- ✅ Study session tracking: Log study time and notes per resource
- ✅ Multi-criteria filtering: By topic, provider, status, and text search
- ✅ Status workflow: Track resource progress (Backlog → In-Progress → Completed/Dropped)
- ✅ Local database storage: DuckDB for lightweight, file-based persistence
- ✅ Quick launch shortcuts: Direct links to work tools (Jira, Outlook, Wiki)

## Planned Features

- 🔄 Technology progress tracking: Monitor expertise levels in DE/DS/ML technologies
- 🔄 Predefined learning roadmaps: Structured paths for skill development
- 🔄 Progress visualization: Charts and metrics for learning advancement
- 🔄 CI/CD pipeline: Automated deployment to Streamlit Cloud on GitHub push

## Upcoming Features

- 📅 Advanced analytics: Study time trends, completion rates, learning velocity
- 📅 Learning recommendations: AI-powered suggestions based on goals and progress
- 📅 Integration with learning platforms: Import resources from Coursera, Udemy, etc.
- 📅 Goal setting and milestones: Define and track learning objectives
- 📅 Export capabilities: Generate learning reports and portfolios

## Tech Stack Roadmap (14-year DE Background)

Based on your strong foundation in databases (PLSQL, Oracle, Db2, MSSQL) and intermediate Python skills, here's your personalized learning plan for transitioning to Data Engineering and Data Science:

### Phase 1: Data Engineering Foundation (3-6 months)
**Priority Technologies:**
- **dbt (High)**: Transform your SQL expertise into modern data modeling
- **Airflow (High)**: Orchestrate data pipelines using your workflow knowledge
- **AWS/GCP (High)**: Cloud platforms for scalable data solutions
- **Databricks/Snowflake (High)**: Next-gen data warehouses beyond traditional RDBMS
- **Python (Medium)**: Advance from 3/5 to 5/5 for ETL scripting
- **Apache Spark (Medium)**: Distributed processing for big data

**Learning Approach:** Leverage your DB experience - focus on how these tools extend traditional database concepts.

### Phase 2: Data Science Analytics (6-9 months)
**Priority Technologies:**
- **Pandas/NumPy (High)**: Data manipulation libraries
- **Matplotlib/Seaborn (High)**: Data visualization
- **SQL for Analytics (High)**: Advanced querying for insights
- **Jupyter Notebooks (Medium)**: Interactive analysis environment
- **Statistics/Probability (Medium)**: Mathematical foundations
- **A/B Testing (Medium)**: Experimental design

**Learning Approach:** Build on your analytical mindset from Power BI experience.

### Phase 3: Machine Learning (9-12 months)
**Priority Technologies:**
- **Scikit-learn (High)**: Traditional ML algorithms
- **TensorFlow/PyTorch (High)**: Deep learning frameworks
- **Feature Engineering (High)**: Creating effective ML features
- **Model Evaluation (High)**: Metrics and validation techniques
- **MLOps (Medium)**: ML deployment and monitoring
- **Computer Vision/NLP (Medium)**: Specialized ML domains

**Learning Approach:** Start with structured data ML, then explore neural networks.

### General Recommendations
- **Weekly Commitment:** 10-15 hours of focused learning
- **Project-Based Learning:** Build real projects (ETL pipelines, data dashboards, ML models)
- **Community:** Join data engineering communities, attend meetups
- **Certification:** Consider AWS Certified Data Analytics, dbt certifications
- **Current Strengths to Leverage:** Your deep DB knowledge gives you an edge in data engineering

## Setup

Make sure you have [uv](https://github.com/astral-sh/uv) installed, then:

```bash
# Install dependencies and create virtual environment
uv sync

# Activate the virtual environment (optional, uv run handles this automatically)
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Run the app
uv run streamlit run app.py
```

### Development Setup

```bash
# Install dev dependencies
uv sync --dev

# Run tests
uv run pytest

# Run linting
uv run flake8

# Format code
uv run black .

# Update dependencies
uv lock --upgrade
```

### Project Structure

- `pyproject.toml`: Project configuration and dependencies
- `uv.lock`: Lock file for reproducible builds
- `.venv/`: Virtual environment (created by uv sync)
