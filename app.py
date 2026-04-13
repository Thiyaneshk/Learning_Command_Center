import json
import webbrowser
from datetime import date, timedelta
from pathlib import Path

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
    sync_resources_from_json,
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


def compute_streaks(sessions_df: pd.DataFrame):
    if sessions_df.empty:
        return 0, 0

    dates = pd.to_datetime(sessions_df["session_date"]).dt.date.dropna().unique()
    if len(dates) == 0:
        return 0, 0

    dates = sorted(dates)
    today = date.today()
    date_set = set(dates)

    current = 0
    day = today
    while day in date_set:
        current += 1
        day -= timedelta(days=1)

    longest = 1
    streak = 1
    for i in range(1, len(dates)):
        if dates[i] == dates[i - 1] + timedelta(days=1):
            streak += 1
        else:
            longest = max(longest, streak)
            streak = 1
    longest = max(longest, streak)

    return current, longest


def compute_roadmap_completion(techs: list[dict]):
    if not techs:
        return {}, 0.0, {}

    df = pd.DataFrame(techs)
    df = df.copy()
    df["target_expertise"] = df["target_expertise"].replace(0, 1)
    df["completion_ratio"] = df["current_expertise"] / df["target_expertise"]

    by_cat = df.groupby("category")["completion_ratio"].mean().to_dict()
    overall = float(df["completion_ratio"].mean())
    mastered_by_cat = df[df["status"] == "mastered"].groupby("category").size().to_dict()

    return by_cat, overall, mastered_by_cat


def sidebar_filters(cfg):
    st.sidebar.header("Filters")

    topics_df = pd.DataFrame(list_topics(), columns=["id", "name"])
    topic_map = {row["name"]: row["id"] for _, row in topics_df.iterrows()} if not topics_df.empty else {}

    default_topics = ["Data Engineering"] if "Data Engineering" in topic_map else list(topic_map.keys())
    selected_topics = st.sidebar.multiselect("Topic", options=list(topic_map.keys()), default=default_topics)
    topic_ids = [topic_map[name] for name in selected_topics]

    providers = get_providers_from_config(cfg)
    selected_providers = st.sidebar.multiselect("Provider", options=providers, default=providers)

    statuses = get_statuses_from_config(cfg)
    selected_statuses = st.sidebar.multiselect("Status", options=statuses, default=statuses)

    search_text = st.sidebar.text_input("Search in title/tags")

    return topic_ids, selected_providers, selected_statuses, search_text


def sidebar_import_resources(cfg):
    st.sidebar.markdown("---")
    st.sidebar.subheader("Import resources")

    resources_file = Path("resources.json")
    if resources_file.exists():
        st.sidebar.write("Found `resources.json` in app folder.")
        if st.sidebar.button("Sync resources from resources.json"):
            inserted, skipped = sync_resources_from_json(resources_file)
            if inserted or skipped:
                st.sidebar.success(f"Imported {inserted} resources, skipped {skipped} existing ones.")
            else:
                st.sidebar.info("No new resources matched or the file was empty.")
    else:
        st.sidebar.warning("No resources.json file found in the app folder.")

    uploaded_file = st.sidebar.file_uploader("Upload resource JSON", type=["json"])
    if uploaded_file:
        try:
            content = json.load(uploaded_file)
            temp_path = Path("resources.json")
            with temp_path.open("w", encoding="utf-8") as f:
                json.dump(content, f, indent=2)
            inserted, skipped = sync_resources_from_json(temp_path)
            st.sidebar.success(f"Uploaded and synced {inserted} resources, skipped {skipped} existing ones.")
        except Exception as exc:
            st.sidebar.error(f"Failed to load JSON: {exc}")


def sidebar_add_resource(cfg):
    st.sidebar.markdown("---")
    st.sidebar.subheader("Add new resource")

    with st.sidebar.form("add_resource_form", clear_on_submit=True):
        title = st.text_input("Title", placeholder="Columbia Data Engineering Course")
        url = st.text_input("URL", placeholder="https://...")

        providers = get_providers_from_config(cfg)
        provider = st.selectbox("Provider", options=providers)

        resource_type = st.selectbox("Type", options=["Course", "Article", "Docs", "Video", "Playlist", "Other"])

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
    st.title("Bookmarks & Resources ~ Learning Command Center TK")
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
        selected_id = st.number_input("Resource ID", min_value=int(df["id"].min()), max_value=int(df["id"].max()), step=1)

        row = df[df["id"] == selected_id]
        if not row.empty:
            st.markdown(f"**Selected:** {row['title'].iloc[0]}")
            st.write(f"URL: {row['url'].iloc[0]}")

            col1, col2 = st.columns(2)
            with col1:
                new_status = st.selectbox(
                    "New status",
                    options=get_statuses_from_config(cfg),
                    index=(
                        get_statuses_from_config(cfg).index(row["status"].iloc[0])
                        if row["status"].iloc[0] in get_statuses_from_config(cfg)
                        else 0
                    ),
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
        resource_id = int(resources_df[resources_df["title"] == resource_title]["id"].iloc[0])
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
        st.caption("Log your first study session above to start tracking streaks and minutes.")
    else:
        sessions_df["session_date"] = pd.to_datetime(sessions_df["session_date"]).dt.date
        current_streak, longest_streak = compute_streaks(sessions_df)

        last_7 = date.today() - timedelta(days=7)
        last_30 = date.today() - timedelta(days=30)
        recent_7 = sessions_df[sessions_df["session_date"] >= last_7]
        recent_30 = sessions_df[sessions_df["session_date"] >= last_30]

        minutes_7 = int(recent_7["duration_minutes"].sum()) if not recent_7.empty else 0
        minutes_30 = int(recent_30["duration_minutes"].sum()) if not recent_30.empty else 0
        resources_7 = recent_7["resource_title"].nunique() if not recent_7.empty else 0

        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            st.metric("Current streak", f"{current_streak} days")
        with col_b:
            st.metric("Longest streak", f"{longest_streak} days")
        with col_c:
            st.metric("Minutes last 7 days", minutes_7)
        with col_d:
            st.metric("Minutes last 30 days", minutes_30)

        if not resources_df.empty:
            merged = sessions_df.merge(
                resources_df[["title", "topic", "provider", "resource_type"]],
                left_on="resource_title",
                right_on="title",
                how="left",
            )
            if "topic" in merged.columns and not merged["topic"].dropna().empty:
                topic_chart = merged.groupby("topic")["duration_minutes"].sum().sort_values(ascending=False)
                if not topic_chart.empty:
                    st.subheader("Time spent by topic")
                    st.bar_chart(topic_chart)

        st.dataframe(sessions_df, use_container_width=True, hide_index=True)


def progress_view():
    st.header("Learning Progress")
    st.caption("Track your expertise in DE/DS/ML technologies")

    techs = list_technologies()
    if not techs:
        st.info("No technologies configured yet.")
        return

    by_cat, overall_completion, mastered_by_cat = compute_roadmap_completion(techs)

    st.subheader("Roadmap summary")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Overall completion", f"{overall_completion * 100:.0f}%")
    with col2:
        total_mastered = sum(mastered_by_cat.values()) if mastered_by_cat else 0
        st.metric("Technologies mastered", total_mastered)

    for cat, ratio in by_cat.items():
        nice_cat = cat.replace("_", " ").title()
        mastered = mastered_by_cat.get(cat, 0)
        st.write(f"{nice_cat} — {ratio * 100:.0f}% complete, {mastered} mastered")
        st.progress(ratio)

    st.markdown("---")

    # Group by category
    categories = {}
    for tech in techs:
        cat = tech["category"].replace("_", " ").title()
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
                progress = tech["current_expertise"] / tech["target_expertise"]
                st.progress(progress)

                # Update form
                with st.form(f"update_{tech['id']}", clear_on_submit=True):
                    new_expertise = st.slider(
                        "Update Expertise (0-5)",
                        min_value=0,
                        max_value=5,
                        value=tech["current_expertise"],
                        key=f"expertise_{tech['id']}",
                    )
                    status_options = ["to_learn", "learning", "mastered"]
                    new_status = st.selectbox(
                        "Status",
                        options=status_options,
                        index=status_options.index(tech["status"]) if tech["status"] in status_options else 0,
                        key=f"status_{tech['id']}",
                    )

                    if st.form_submit_button("Update"):
                        update_technology_expertise(tech["id"], new_expertise, new_status)
                        st.success("Updated!")
                        st.rerun()


def main():
    page = st.sidebar.radio("View", ["Resources", "Sessions", "Progress"])
    topic_ids, providers, statuses, search_text = sidebar_filters(cfg)
    sidebar_import_resources(cfg)
    sidebar_add_resource(cfg)

    if page == "Resources":
        main_resources_view(topic_ids, providers, statuses, search_text)
    elif page == "Sessions":
        sessions_view()
    else:
        progress_view()


if __name__ == "__main__":
    main()
