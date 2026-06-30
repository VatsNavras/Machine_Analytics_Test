# dashboard.py - Enhanced dashboard
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

PRIMARY_COLOR = "#2e8de8"

def show_dashboard(df):

    # DATA CLEANING
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # CALCULATED COLUMNS
    df["Revenue"] = (
        df["Produced Qty"] *
        df["Per Item Price"]
    )

    df["Tonnage"] = (
        df["Produced Qty"] *
        df["CutWt"]
    ) / 1000

    # SIDEBAR FILTERS
    st.sidebar.title("📊 Filters")

    module_list = sorted(
        df["ModuleName"].dropna().unique()
    )

    selected_module = st.sidebar.selectbox(
        "🏢 Select Module / Zone",
        module_list,
        help="Filter data by manufacturing zone"
    )

    filtered_df = df[
        df["ModuleName"] == selected_module
    ]

    # DATE FILTER
    st.sidebar.subheader("📅 Date Range")
    
    start_date = st.sidebar.date_input(
        "Start Date",
        filtered_df["Date"].min()
    )

    end_date = st.sidebar.date_input(
        "End Date",
        filtered_df["Date"].max()
    )

    filtered_df = filtered_df[
        (filtered_df["Date"] >= pd.to_datetime(start_date)) &
        (filtered_df["Date"] <= pd.to_datetime(end_date))
    ]

    # SHIFT FILTER
    shift_list = sorted(
        filtered_df["Shift"].dropna().unique()
    )

    selected_shift = st.sidebar.multiselect(
        "🌙 Select Shift",
        shift_list,
        default=shift_list,
        help="Select one or more shifts"
    )

    filtered_df = filtered_df[
        filtered_df["Shift"].isin(selected_shift)
    ]

    # MACHINE FILTER
    machine_list = sorted(
        filtered_df["MachineName"].dropna().unique()
    )

    selected_machine = st.sidebar.multiselect(
        "⚙️ Select Machine",
        machine_list,
        default=machine_list,
        help="Select one or more machines"
    )

    filtered_df = filtered_df[
        filtered_df["MachineName"].isin(selected_machine)
    ]

    # OPERATOR FILTER
    operator_list = sorted(
        filtered_df["OperatorName"].dropna().unique()
    )

    selected_operator = st.sidebar.multiselect(
        "👤 Select Operator",
        operator_list,
        default=operator_list,
        help="Select one or more operators"
    )

    filtered_df = filtered_df[
        filtered_df["OperatorName"].isin(selected_operator)
    ]

    # KPI CALCULATIONS
    total_qty = filtered_df["Produced Qty"].sum()
    total_revenue = filtered_df["Revenue"].sum()
    total_tonnage = filtered_df["Tonnage"].sum()
    total_orders = filtered_df["Order Qty"].sum()
    
    achievement = 0
    if total_orders > 0:
        achievement = (total_qty / total_orders) * 100
    
    active_machines = filtered_df["MachineName"].nunique()
    active_operators = filtered_df["OperatorName"].nunique()

    # TITLE
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("⚙️ Machining Analytics Dashboard")
        st.subheader(f"Zone: {selected_module}")
    
    with col2:
        st.metric("Last Updated", datetime.now().strftime("%H:%M:%S"), label_visibility="collapsed")

    # KPI SECTION
    st.subheader("📈 Key Performance Indicators")
    
    col1, col2, col3 = st.columns(3)

    col1.metric("Produced Qty", f"{total_qty:,.0f}", delta="Units", label_visibility="visible")
    col2.metric("Revenue", f"₹ {total_revenue:,.0f}", label_visibility="visible")
    col3.metric("Tonnage", f"{total_tonnage:,.2f}", delta="Ton", label_visibility="visible")

    col4, col5, col6 = st.columns(3)

    col4.metric("Achievement %", f"{achievement:.1f}%", delta="Target: 100%", label_visibility="visible")
    col5.metric("Active Machines", active_machines, label_visibility="visible")
    col6.metric("Active Operators", active_operators, label_visibility="visible")

    st.divider()

    # MACHINE ANALYTICS
    st.subheader("🤖 Machine Performance")
    
    col1, col2 = st.columns(2)

    with col1:
        machine_prod = (
            filtered_df.groupby("MachineName")
            ["Produced Qty"]
            .sum()
            .reset_index()
            .sort_values(by="Produced Qty", ascending=False)
        )

        fig_machine = px.bar(
            machine_prod,
            x="MachineName",
            y="Produced Qty",
            color="Produced Qty",
            color_continuous_scale=["#ff9800", "#2e8de8", "#4caf50"],
            title="Machine-wise Production Output",
            labels={"MachineName": "Machine", "Produced Qty": "Quantity"}
        )
        fig_machine.update_layout(hovermode="x unified", showlegend=False, height=400)
        
        st.plotly_chart(fig_machine, use_container_width=True)

    with col2:
        machine_revenue = (
            filtered_df.groupby("MachineName")
            ["Revenue"]
            .sum()
            .reset_index()
            .sort_values(by="Revenue", ascending=False)
        )

        fig_machine_rev = px.bar(
            machine_revenue,
            x="MachineName",
            y="Revenue",
            color="Revenue",
            color_continuous_scale=["#ff9800", "#2e8de8", "#4caf50"],
            title="Machine-wise Revenue Generation",
            labels={"MachineName": "Machine", "Revenue": "Revenue (₹)"}
        )
        fig_machine_rev.update_layout(hovermode="x unified", showlegend=False, height=400)
        
        st.plotly_chart(fig_machine_rev, use_container_width=True)

    # OPERATOR ANALYTICS
    st.subheader("👥 Operator Performance")
    
    col1, col2 = st.columns(2)

    with col1:
        operator_prod = (
            filtered_df.groupby("OperatorName")
            ["Produced Qty"]
            .sum()
            .reset_index()
            .sort_values(by="Produced Qty", ascending=False)
        )

        fig_operator = px.bar(
            operator_prod,
            x="OperatorName",
            y="Produced Qty",
            color="Produced Qty",
            color_continuous_scale=["#ff9800", "#2e8de8", "#4caf50"],
            title="Operator-wise Production",
            labels={"OperatorName": "Operator", "Produced Qty": "Quantity"}
        )
        fig_operator.update_layout(hovermode="x unified", showlegend=False, height=400)
        
        st.plotly_chart(fig_operator, use_container_width=True)

    with col2:
        operator_revenue = (
            filtered_df.groupby("OperatorName")
            ["Revenue"]
            .sum()
            .reset_index()
        )

        fig_operator_rev = px.pie(
            operator_revenue,
            names="OperatorName",
            values="Revenue",
            hole=0.4,
            title="Operator Revenue Contribution",
            labels={"Revenue": "Revenue (₹)"}
        )
        fig_operator_rev.update_layout(height=400)
        
        st.plotly_chart(fig_operator_rev, use_container_width=True)

    # DAILY TREND
    st.subheader("📊 Production Trends")
    
    daily_prod = (
        filtered_df.groupby("Date")
        ["Produced Qty"]
        .sum()
        .reset_index()
    )

    fig_daily = px.line(
        daily_prod,
        x="Date",
        y="Produced Qty",
        markers=True,
        title="Daily Production Trend",
        labels={"Date": "Date", "Produced Qty": "Quantity"}
    )
    fig_daily.update_traces(line=dict(color=PRIMARY_COLOR, width=3), marker=dict(size=8))
    fig_daily.update_layout(hovermode="x unified", height=400)
    
    st.plotly_chart(fig_daily, use_container_width=True)

    # DATA TABLE
    st.divider()
    st.subheader("📋 Production Data")

    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.write(f"Total Records: {len(filtered_df)}")
    
    with col2:
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()

    st.dataframe(
        filtered_df.sort_values("Date", ascending=False),
        use_container_width=True,
        height=400
    )

    # EXPORT
    st.divider()
    st.subheader("📥 Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📄 Download CSV",
            data=csv,
            file_name=f"production_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col2:
        if st.button("📊 View Summary"):
            st.info("Summary statistics for selected filters")
            st.write(filtered_df.describe())