from pathlib import Path

import streamlit as st

from experiment_tracker.storage import create_experiment, list_experiments

DB_PATH = Path("data/experiments.db")


def render_dashboard() -> None:
    st.set_page_config(page_title="Experiment Tracker", layout="wide")
    st.title("Experiment Tracker")
    st.caption("Track hypotheses, evidence, and decisions across engineering experiments.")

    experiments = list_experiments(DB_PATH)
    if not experiments:
        st.info("No experiments yet. Create the first one below.")
    else:
        st.dataframe(experiments, use_container_width=True, hide_index=True)

    with st.expander("Create experiment", expanded=not experiments):
        with st.form("create_experiment"):
            title = st.text_input("Title")
            category = st.text_input("Category", value="architecture")
            hypothesis = st.text_area("Hypothesis")
            baseline = st.text_area("Baseline")
            success_criteria = st.text_area("Success criteria")
            submitted = st.form_submit_button("Create experiment")
        if submitted:
            try:
                create_experiment(DB_PATH, title, category, hypothesis, baseline, success_criteria)
            except ValueError as error:
                st.error(str(error))
            else:
                st.success("Experiment created.")
                st.rerun()


if __name__ == "__main__":
    render_dashboard()
