import webbrowser
from datetime import date

import pandas as pd
import streamlit as st

from config_loader import (
    get_difficulties_from_config,
    get_providers_from_config,
    get_statuses_from_config,
    get_technologies_from_config,
    get_topics_from_config,
    load_config,
)
from db import (
    init_db,
    insert_resource,
    insert_session,
    list_resources,
    list_sessions,
    list_technologies,
    list_topics,
    sync_technologies_from_config,
    sync_topics_from_config,
    update_last_accessed,
    update_resource_status,
    update_technology_expertise,
)
st.set_page_config(
    page_title="Learning Command Center",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.set_page_config(page_title="Learning Command Center", layout="wide")


def init_app():
    cfg = load_config()

    # Initialize and sync DB
    init_db()
    sync_topics_from_config(get_topics_from_config(cfg))
    sync_technologies_from_config(get_technologies_from_config(cfg))

    return cfg


cfg = init_app()


def sidebar_filters(cfg):
    st.sidebar.header("Filters")

    topics_df = pd.DataFrame(list_topics(), columns=["id", "name"])
    topic_map = {row["name"]: row["id"] for _, row in topics_df.iterrows()} if not topics_df.empty else {}

    selected_topics = st.sidebar.multiselect(
        "Topic", options=list(topic_map.keys()), default=list(topic_map.keys())
    )
    topic_ids = [topic_map[name] for name in selected_topics]

    providers = get_providers_from_config(cfg)
    selected_providers = st.sidebar.multiselect(
        "Provider", options=providers, default=providers
    )

    statuses = get_statuses_from_config(cfg)
    selected_statuses = st.sidebar.multiselect(
        "Status", options=statuses, default=statuses
    )

    search_text = st.sidebar.text_input("Search in title/tags")

    return topic_ids, selected_providers, selected_statuses, search_text


def sidebar_add_resource(cfg):
    st.sidebar.markdown("---")
    st.sidebar.subheader("Add new resource")

    with st.sidebar.form("add_resource_form", clear_on_submit=True):
        title = st.text_input("Title", placeholder="Columbia Data Engineering Course")
        url = st.text_input("URL", placeholder="https://...")

        providers = get_providers_from_config(cfg)
        provider = st.selectbox("Provider", options=providers)

        resource_type = st.selectbox(
            "Type", options=["Course", "Article", "Docs", "Video", "Playlist", "Other"]
        )

        topics_df = pd.DataFrame(list_topics(), columns=["id", "name"])
        topic_name = None
        topic_id = None
        if not topics_df.empty:
            topic_name = st.selectbox("Topic", options=topics_df["name"].tolist())
            topic_id = int(topics_df[topics_df["name"] == topic_name]["id"].iloc[0])

        difficulties = get_difficulties_from_config(cfg)
        difficulty = st.selectbox("Difficulty", options=difficulties)

        statuses = get_statuses_from_config(cfg)
        status = st.selectbox("Status", options=statuses)

        tags = st.text_input("Tags (comma separated)")
        notes = st.text_area("Notes", height=80)
        rating = st.slider("Rating", min_value=0, max_value=5, value=0)

        submitted = st.form_submit_button("Add resource")

        if submitted:
            if not title or not url:
                st.sidebar.error("Title and URL are required")
            else:
                insert_resource(
                    {
                        "title": title,
                        "url": url,
                        "provider": provider,
                        "resource_type": resource_type,
                        "topic_id": topic_id,
                        "difficulty": difficulty,
                        "status": status,
                        "tags": tags,
                        "notes": notes,
                        "rating": rating or None,
                    }
                )
                st.sidebar.success("Resource added")


def main_resources_view(topic_ids, providers, statuses, search_text):
    st.title("Bookmarks & Resources")
    st.caption("Track DE / ML / DS learning resources and study sessions")

    st.subheader("Daily work launchpad")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Jira Board"):
            webbrowser.open("https://your-jira-url-here")

    with col2:
        if st.button("Outlook Web"):
            webbrowser.open("https://outlook.office.com/mail")

    with col3:
        if st.button("Org Wiki"):
            webbrowser.open("https://your-confluence-or-wiki-url")

    st.markdown("---")  # separator

    st.title("Learning Command Center")
    st.caption("Track DE / ML / DS learning resources and study sessions")

    df = list_resources(
        topic_ids=topic_ids or None,
        providers=providers or None,
        statuses=statuses or None,
        search_text=search_text or None,
    )

    if df.empty:
        st.info("No resources yet. Add one from the sidebar.")
        return

    st.subheader("Resources")

    # Show a trimmed view for browsing
    display_cols = [
        "id",
        "title",
        "provider",
        "resource_type",
        "topic",
        "difficulty",
        "status",
        "tags",
        "last_accessed_at",
    ]

    st.dataframe(df[display_cols], use_container_width=True, hide_index=True)

    with st.expander("Update status / open resource"):
        selected_id = st.number_input(
            "Resource ID", min_value=int(df["id"].min()), max_value=int(df["id"].max()), step=1
        )

        row = df[df["id"] == selected_id]
        if not row.empty:
            st.markdown(f"**Selected:** {row['title'].iloc[0]}")
            st.write(f"URL: {row['url'].iloc[0]}")

            col1, col2 = st.columns(2)
            with col1:
                new_status = st.selectbox(
                    "New status",
                    options=get_statuses_from_config(cfg),
                    index=get_statuses_from_config(cfg).index(row["status"].iloc[0])
                    if row["status"].iloc[0] in get_statuses_from_config(cfg)
                    else 0,
                    key="status_select",
                )

                if st.button("Update status"):
                    update_resource_status(int(selected_id), new_status)
                    st.success("Status updated. Rerun the app to see changes.")

            with col2:
                if st.button("Open in browser"):
                    webbrowser.open(row["url"].iloc[0])
                    update_last_accessed(int(selected_id))
                    st.success("Opened and updated last accessed time.")
        else:
            st.warning("No resource with that ID in the current filter.")


def sessions_view():
    st.header("Study sessions")

    resources_df = list_resources()
    if resources_df.empty:
        st.info("Add some resources first, then you can log sessions.")
        return

    with st.form("add_session_form", clear_on_submit=True):
        resource_title = st.selectbox("Resource", options=resources_df["title"].tolist())
        resource_id = int(
            resources_df[resources_df["title"] == resource_title]["id"].iloc[0]
        )
        session_date = st.date_input("Date", value=date.today())
        duration = st.number_input("Duration (minutes)", min_value=0, max_value=600, value=30)
        notes = st.text_area("Notes", height=80)

        submitted = st.form_submit_button("Log session")
        if submitted:
            insert_session(
                {
                    "resource_id": resource_id,
                    "session_date": session_date,
                    "duration_minutes": duration,
                    "notes": notes,
                }
            )
            st.success("Session logged")

    st.subheader("Recent sessions")
    sessions_df = list_sessions()
    if sessions_df.empty:
        st.info("No sessions logged yet.")
    else:
        st.dataframe(sessions_df, use_container_width=True, hide_index=True)


def progress_view():
    st.header("Learning Progress")
    st.caption("Track your expertise in DE/DS/ML technologies")

    techs = list_technologies()
    if not techs:
        st.info("No technologies configured yet.")
        return

    # Group by category
    categories = {}
    for tech in techs:
        cat = tech['category'].replace('_', ' ').title()
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(tech)

    for cat_name, cat_techs in categories.items():
        st.subheader(cat_name)
        
        for tech in cat_techs:
            with st.expander(f"{tech['name']} ({tech['priority']} priority)"):
                st.write(f"**Description:** {tech['description']}")
                st.write(f"**Current Expertise:** {tech['current_expertise']}/5")
                st.write(f"**Target:** {tech['target_expertise']}/5")
                st.write(f"**Status:** {tech['status'].replace('_', ' ').title()}")
                
                # Progress bar
                progress = tech['current_expertise'] / tech['target_expertise']
                st.progress(progress)
                
                # Update form
                with st.form(f"update_{tech['id']}", clear_on_submit=True):
                    new_expertise = st.slider(
                        "Update Expertise (0-5)", 
                        min_value=0, 
                        max_value=5, 
                        value=tech['current_expertise'],
                        key=f"expertise_{tech['id']}"
                    )
                    status_options = ["to_learn", "learning", "mastered"]
                    new_status = st.selectbox(
                        "Status", 
                        options=status_options,
                        index=status_options.index(tech['status']) if tech['status'] in status_options else 0,
                        key=f"status_{tech['id']}"
                    )
                    
                    if st.form_submit_button("Update"):
                        update_technology_expertise(tech['id'], new_expertise, new_status)
                        st.success("Updated!")
                        st.rerun()


def main():
    page = st.sidebar.radio("View", ["Resources", "Sessions", "Progress"])
    topic_ids, providers, statuses, search_text = sidebar_filters(cfg)
    sidebar_add_resource(cfg)

    if page == "Resources":
        main_resources_view(topic_ids, providers, statuses, search_text)
    elif page == "Sessions":
        sessions_view()
    else:
        progress_view()


if __name__ == "__main__":
    main()
