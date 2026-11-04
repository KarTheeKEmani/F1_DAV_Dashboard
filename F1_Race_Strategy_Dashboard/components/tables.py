import streamlit as st
import pandas as pd
from typing import Optional


def render_interactive_table(
    df: pd.DataFrame,
    title: Optional[str] = None,
    download_filename: str = "f1_data_export.csv",
    use_container_width: bool = True,
    height: Optional[int] = 400
):
    """Renders a styled interactive table with search, sorting, and CSV download button."""
    if title:
        st.markdown(f"#### {title}")

    if df.empty:
        st.info("No records matching the selected filters.")
        return

    # Clean display copy
    display_df = df.copy()

    # Format numeric floats
    for col in display_df.select_dtypes(include=['float']).columns:
        if "Sec" in col or "Time" in col or "Duration" in col or "Pace" in col:
            display_df[col] = display_df[col].apply(lambda x: f"{x:.3f}" if pd.notna(x) else "-")
        elif "Pct" in col or "CV" in col:
            display_df[col] = display_df[col].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "-")
        else:
            display_df[col] = display_df[col].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "-")

    # Display dataframe with Streamlit native interactivity
    st.dataframe(
        display_df,
        use_container_width=use_container_width,
        height=height,
        hide_index=True
    )

    # CSV Download Button
    csv_bytes = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"📥 Download Data ({len(df):,} rows as CSV)",
        data=csv_bytes,
        file_name=download_filename,
        mime="text/csv",
        key=f"dl_{download_filename}_{hash(title or '')}"
    )
