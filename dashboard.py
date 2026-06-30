import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

PRIMARY_COLOR = "#2e8de8"
RED = "#cc1f24"


def build_job_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate stage-level rows up to one row per job (Document Number).

    Why min/max instead of sum: a job's rows represent sequential
    operations on the SAME physical pieces, not independent batches.
    Quantity can only stay flat or shrink stage to stage (scrap/rejects),
    never grow. So:
      - Completed Qty  = MIN(Produced Qty) across the job's stages
                         (the safest lower-bound estimate of what
                         actually made it through every logged stage)
      - Peak Qty       = MAX(Produced Qty) (qty at the earliest/best stage)
      - Yield Loss     = Peak Qty - Completed Qty (pieces lost somewhere
                         in the process, across whichever stages were logged)
      - Setup Count    = number of distinct stage rows for that job
                         (process complexity / changeover cost driver,
                         NOT a quantity multiplier)
    Revenue is calculated once per job, on Completed Qty only -- never
    summed across stage rows, or it would be inflated by however many
    operations the job went through.
    """
    grouped = df.groupby("Document Number").agg(
        Part_Name=("Part Name", "first"),
        Material_Grade=("Material Grade", "first"),
        ModuleName=("ModuleName", "first"),
        Order_Qty=("Order Qty", "first"),
        Per_Item_Price=("Per Item Price", "first"),
        Completed_Qty=("Produced Qty", "min"),
        Peak_Qty=("Produced Qty", "max"),
        Setup_Count=("Setup", "nunique"),
        Last_Date=("Date", "max"),
    ).reset_index()

    grouped["Yield_Loss"] = grouped["Peak_Qty"] - grouped["Completed_Qty"]
    grouped["Revenue"] = grouped["Completed_Qty"] * grouped["Per_Item_Price"]
    grouped["Fulfillment_%"] = grouped.apply(
        lambda r: (r["Completed_Qty"] / r["Order_Qty"] * 100) if r["Order_Qty"] > 0 else 0,
        axis=1
    )
    return grouped


def show_dashboard(df):
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # =====================================================
    # SIDEBAR FILTERS (applied to raw stage-level rows first)
    # =====================================================
    st.sidebar.title("📊 Filters")

    module_list = sorted(df["ModuleName"].dropna().unique())
    selected_module = st.sidebar.selectbox("🏢 Select Module / Zone", module_list)
    filtered_df = df[df["ModuleName"] == selected_module]

    st.sidebar.subheader("📅 Date Range")
    start_date = st.sidebar.date_input("Start Date", filtered_df["Date"].min())
    end_date = st.sidebar.date_input("End Date", filtered_df["Date"].max())
    filtered_df = filtered_df[
        (filtered_df["Date"] >= pd.to_datetime(start_date)) &
        (filtered_df["Date"] <= pd.to_datetime(end_date))
    ]

    shift_list = sorted(filtered_df["Shift"].dropna().unique())
    selected_shift = st.sidebar.multiselect("🌙 Select Shift", shift_list, default=shift_list)
    filtered_df = filtered_df[filtered_df["Shift"].isin(selected_shift)]

    machine_list = sorted(filtered_df["MachineName"].dropna().unique())
    selected_machine = st.sidebar.multiselect("⚙️ Select Machine", machine_list, default=machine_list)
    filtered_df = filtered_df[filtered_df["MachineName"].isin(selected_machine)]

    operator_list = sorted(filtered_df["OperatorName"].dropna().unique())
    selected_operator = st.sidebar.multiselect("👤 Select Operator", operator_list, default=operator_list)
    filtered_df = filtered_df[filtered_df["OperatorName"].isin(selected_operator)]

    setup_list = sorted(filtered_df["Setup"].dropna().unique())
    selected_setup = st.sidebar.multiselect("🔧 Select Operation / Setup", setup_list, default=setup_list,
                                             help="Facing, OD Turning, Drilling etc. Filtering this affects stage-level charts only.")
    filtered_df_stage = filtered_df[filtered_df["Setup"].isin(selected_setup)]

    if filtered_df_stage.empty:
        st.warning("No data for the selected filters.")
        return

    # =====================================================
    # JOB-LEVEL SUMMARY (the corrected, non-double-counted view)
    # Built from filtered_df (module/date/shift/machine/operator),
    # NOT from filtered_df_stage, so a job's full stage history stays
    # intact for min/max calculation even if a Setup filter is active.
    # =====================================================
    job_summary = build_job_summary(filtered_df)

    total_completed_qty = job_summary["Completed_Qty"].sum()
    total_revenue = job_summary["Revenue"].sum()
    total_order_qty = job_summary["Order_Qty"].sum()
    total_yield_loss = job_summary["Yield_Loss"].sum()
    achievement = (total_completed_qty / total_order_qty * 100) if total_order_qty > 0 else 0
    total_jobs = job_summary["Document Number"].nunique()
    active_machines = filtered_df_stage["MachineName"].nunique()
    active_operators = filtered_df_stage["OperatorName"].nunique()

    # =====================================================
    # TITLE
    # =====================================================
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("⚙️ Machining Analytics Dashboard")
        st.subheader(f"Zone: {selected_module}")
    with col2:
        st.metric("Last Updated", datetime.now().strftime("%H:%M:%S"), label_visibility="collapsed")

    # =====================================================
    # KPI SECTION
    # =====================================================
    st.subheader("📈 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Completed Qty", f"{total_completed_qty:,.0f}", help="Min produced qty across each job's logged stages -- the safest estimate of pieces that actually cleared every operation.")
    col2.metric("Revenue", f"₹ {total_revenue:,.0f}", help="Completed Qty × Price, calculated once per job.")
    col3.metric("Yield Loss", f"{total_yield_loss:,.0f} pcs", help="Peak stage qty minus completed qty, summed across jobs. Pieces lost somewhere in the process.")
    col4.metric("Achievement %", f"{achievement:.1f}%", delta="Target: 100%")

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Total Jobs", total_jobs)
    col6.metric("Active Machines", active_machines)
    col7.metric("Active Operators", active_operators)
    avg_setups = job_summary["Setup_Count"].mean() if total_jobs else 0
    col8.metric("Avg Setups / Job", f"{avg_setups:.1f}", help="Process complexity -- more setups per job means more changeover cost regardless of quantity.")

    st.divider()

    # =====================================================
    # STAGE BOTTLENECK / WIP VIEW
    # =====================================================
    st.subheader("🚧 Stage-wise Output (Bottleneck / WIP View)")
    st.caption("Compares total stage-level output across operations for the selected jobs. A large drop between stages usually means work-in-progress is piling up or pieces are being lost at that operation.")
    stage_perf = (
        filtered_df_stage.groupby("Setup")["Produced Qty"]
        .sum()
        .reset_index()
        .sort_values(by="Produced Qty", ascending=False)
    )
    fig_stage = px.bar(
        stage_perf, x="Setup", y="Produced Qty", color="Produced Qty",
        color_continuous_scale=["#ff9800", PRIMARY_COLOR, "#4caf50"],
        title="Total Output by Operation / Setup Stage",
        labels={"Setup": "Operation", "Produced Qty": "Stage Output (pcs)"}
    )
    fig_stage.update_layout(showlegend=False, height=380)
    st.plotly_chart(fig_stage, use_container_width=True)

    # =====================================================
    # YIELD LOSS - TOP JOBS
    # =====================================================
    st.subheader("📉 Top Yield-Loss Jobs")
    st.caption("Jobs with the largest gap between their peak stage output and final completed quantity -- where scrap/rejects are concentrated.")
    top_loss = job_summary.sort_values("Yield_Loss", ascending=False).head(10)
    if top_loss["Yield_Loss"].sum() > 0:
        fig_loss = px.bar(
            top_loss, x="Document Number", y="Yield_Loss", color="Yield_Loss",
            color_continuous_scale=["#4caf50", "#ff9800", RED],
            title="Top 10 Jobs by Yield Loss",
            labels={"Yield_Loss": "Pieces Lost", "Document Number": "Job"},
            hover_data=["Part_Name", "Material_Grade"]
        )
        fig_loss.update_layout(showlegend=False, height=380)
        st.plotly_chart(fig_loss, use_container_width=True)
    else:
        st.info("No yield loss detected for the selected filters.")

    st.divider()

    # =====================================================
    # MACHINE / OPERATOR STAGE THROUGHPUT
    # =====================================================
    st.subheader("🤖 Machine & Operator Stage Throughput")
    st.caption("These reflect operation-level (stage) throughput, not unique finished pieces -- a job touches multiple machines/operators across its stages.")
    col1, col2 = st.columns(2)
    with col1:
        machine_prod = (
            filtered_df_stage.groupby("MachineName")["Produced Qty"]
            .sum().reset_index().sort_values(by="Produced Qty", ascending=False)
        )
        fig_machine = px.bar(
            machine_prod, x="MachineName", y="Produced Qty", color="Produced Qty",
            color_continuous_scale=["#ff9800", PRIMARY_COLOR, "#4caf50"],
            title="Machine-wise Stage Output",
            labels={"MachineName": "Machine", "Produced Qty": "Stage Output (pcs)"}
        )
        fig_machine.update_layout(showlegend=False, height=380)
        st.plotly_chart(fig_machine, use_container_width=True)
    with col2:
        operator_prod = (
            filtered_df_stage.groupby("OperatorName")["Produced Qty"]
            .sum().reset_index().sort_values(by="Produced Qty", ascending=False)
        )
        fig_operator = px.bar(
            operator_prod, x="OperatorName", y="Produced Qty", color="Produced Qty",
            color_continuous_scale=["#ff9800", PRIMARY_COLOR, "#4caf50"],
            title="Operator-wise Stage Output",
            labels={"OperatorName": "Operator", "Produced Qty": "Stage Output (pcs)"}
        )
        fig_operator.update_layout(showlegend=False, height=380)
        st.plotly_chart(fig_operator, use_container_width=True)

    # =====================================================
    # JOB FULFILLMENT
    # =====================================================
    st.subheader("📦 Job Fulfillment (Order vs Completed)")
    fulfillment_view = job_summary.sort_values("Fulfillment_%", ascending=True).head(15)
    fig_fulfill = px.bar(
        fulfillment_view, x="Document Number", y=["Order_Qty", "Completed_Qty"],
        barmode="group", title="Lowest 15 Jobs by Fulfillment % (Order Qty vs Completed Qty)",
        labels={"value": "Quantity", "variable": "Metric"}
    )
    fig_fulfill.update_layout(height=380)
    st.plotly_chart(fig_fulfill, use_container_width=True)

    # =====================================================
    # DAILY STAGE-COMPLETION TREND
    # =====================================================
    st.subheader("📊 Daily Stage-Completion Trend")
    st.caption("Counts stage completions per day (operation-level throughput), not unique finished parts.")
    daily_prod = filtered_df_stage.groupby("Date")["Produced Qty"].sum().reset_index()
    fig_daily = px.line(
        daily_prod, x="Date", y="Produced Qty", markers=True,
        title="Daily Stage Output", labels={"Date": "Date", "Produced Qty": "Stage Output (pcs)"}
    )
    fig_daily.update_traces(line=dict(color=PRIMARY_COLOR, width=3), marker=dict(size=7))
    fig_daily.update_layout(hovermode="x unified", height=380)
    st.plotly_chart(fig_daily, use_container_width=True)

    st.divider()

    # =====================================================
    # JOB-LEVEL SUMMARY TABLE
    # =====================================================
    st.subheader("📋 Job Summary (one row per Document Number)")
    st.write(f"Total Jobs: {len(job_summary)}")
    st.dataframe(
        job_summary.sort_values("Last_Date", ascending=False),
        use_container_width=True, height=350
    )

    with st.expander("🔍 View raw stage-level rows"):
        st.dataframe(filtered_df_stage.sort_values("Date", ascending=False), use_container_width=True, height=350)

    col1, col2 = st.columns([3, 1])
    with col1:
        pass
    with col2:
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()

    # =====================================================
    # EXPORT
    # =====================================================
    st.divider()
    st.subheader("📥 Export Options")
    col1, col2 = st.columns(2)
    with col1:
        csv_jobs = job_summary.to_csv(index=False)
        st.download_button(
            "📄 Download Job Summary CSV", data=csv_jobs,
            file_name=f"job_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv"
        )
    with col2:
        csv_raw = filtered_df_stage.to_csv(index=False)
        st.download_button(
            "📄 Download Raw Stage Data CSV", data=csv_raw,
            file_name=f"stage_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv"
        )
