# sheets.py - Simplified
import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta

@st.cache_data(ttl=300)
def load_data() -> pd.DataFrame:
    return create_sample_data()

def create_sample_data() -> pd.DataFrame:
    dates = pd.date_range(start='2024-01-01', periods=90, freq='D')
    modules = ['CNC Zone A', 'CNC Zone B', 'CNC Zone C']
    machines = ['Machine-01', 'Machine-02', 'Machine-03', 'Machine-04']
    operators = ['Operator-A', 'Operator-B', 'Operator-C', 'Operator-D']
    shifts = ['Morning', 'Afternoon', 'Night']
    
    data = []
    for date in dates:
        for shift in shifts:
            for module in modules:
                for machine in machines:
                    for operator in operators:
                        data.append({
                            'Date': date,
                            'ModuleName': module,
                            'MachineName': machine,
                            'OperatorName': operator,
                            'Shift': shift,
                            'Produced Qty': random.randint(50, 500),
                            'Order Qty': random.randint(300, 1000),
                            'Per Item Price': random.choice([100, 150, 200, 250, 300]),
                            'CutWt': random.randint(100, 500),
                            'Cycle Time': random.randint(5, 30)
                        })
    return pd.DataFrame(data)
