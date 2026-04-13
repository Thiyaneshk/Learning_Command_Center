# Learning Command Center

Personal Streamlit app to track Data Engineering / ML / DS learning resources using DuckDB as a local store.

## Vision

To create a comprehensive personal learning management system that empowers Data Engineering, Data Science, and Machine Learning professionals to:
- Systematically track and organize learning resources across DE/DS/ML domains
- Monitor personal expertise progression in key technologies and tools
- Maintain accountability through study session logging and progress visualization
- Plan structured learning paths based on career goals and current skill levels
- Achieve continuous professional development in the rapidly evolving data field

## Completed Features

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
