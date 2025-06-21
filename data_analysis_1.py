import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# Load sample data
df = pd.read_csv('peter_2024_period_capability_actuals.csv', parse_dates=['period'])
df['month_num'] = df['period'].dt.month


df.head()


# Function to calculate variance metrics
def calculate_variance_metrics(df):
    df = df.copy()
    df['variance'] = df['actual_cost'] - df['budget_cost']
    df['variance_pct'] = np.where(
        df['budget_cost'] != 0,
        (df['variance'] / df['budget_cost']) * 100,
        0
    ).round(2)
    return df


variance_df = calculate_variance_metrics(df)
variance_df.head()


# Function to calculate YTD variance contribution
def calculate_ytd_variance_contribution(df):
    df = df.sort_values(['year', 'business_capability_name', 'month_num'])
    df['ytd_variance_contribution'] = df.groupby(
        ['year', 'business_capability_name']
    )['variance'].cumsum().round(2)
    return df


variance_ytd_df = calculate_ytd_variance_contribution(variance_df)

variance_ytd_df.head()


# Function to rank by YTD variance
def rank_by_ytd_variance_contribution(df):
    latest_ytd = df.loc[df.groupby(
        ['year', 'business_capability_name']
    )['month_num'].idxmax()].copy()
    latest_ytd['ytd_variance_rank'] = latest_ytd.groupby('year')[
        'ytd_variance_contribution'
    ].rank(ascending=False, method='dense').astype(int)
    rank_map = latest_ytd.set_index(['year', 'business_capability_name'])['ytd_variance_rank'].to_dict()
    df['ytd_variance_rank'] = df.apply(
        lambda x: rank_map.get((x['year'], x['business_capability_name']), np.nan),
        axis=1
    )
    return df


variance_ytd_df_ranked = rank_by_ytd_variance_contribution(variance_ytd_df)


# Function to create YTD variance visualization
def create_ytd_variance_chart(df):
    latest_year = df['year'].max()
    yearly_data = df[df['year'] == latest_year]
    
    # Aggregate to business capability level
    agg_data = yearly_data.groupby(
        ['business_capability_name', 'month_num', 'month_name']
    ).agg({'ytd_variance_contribution': 'sum'}).reset_index()
    
    fig = go.Figure()
    capabilities = agg_data['business_capability_name'].unique()
    
    for capability in capabilities:
        cap_data = agg_data[agg_data['business_capability_name'] == capability]
        fig.add_trace(go.Scatter(
            x=cap_data['month_name'],
            y=cap_data['ytd_variance_contribution'] / 1e6,
            mode='lines+markers',
            name=capability
        ))
    
    fig.update_layout(
        title=f'YTD Variance Contribution by Business Capability ({latest_year})',
        xaxis_title='Month',
        yaxis_title='YTD Variance (Millions USD)',
        hovermode='x unified',
        height=600
    )
    fig.add_hline(y=0, line_dash="dash", line_color="black")
    return fig


fig_1 = create_ytd_variance_chart(variance_ytd_df_ranked)


fig_1.show()


def analyze_financial_performance(df):
    # Calculate metrics
    variance_df = calculate_variance_metrics(df)
    ytd_df = calculate_ytd_variance_contribution(variance_df)
    ranked_df = rank_by_ytd_variance_contribution(ytd_df)
    
    # Generate visualization
    fig = create_ytd_variance_chart(ranked_df)
    
    # Display key metrics
    total_budget = df['budget_cost'].sum()
    total_actual = df['actual_cost'].sum()
    net_variance = total_actual - total_budget
    net_variance_pct = (net_variance / total_budget) * 100
    
    print(f"Total Budget: ${total_budget/1e6:.2f}M")
    print(f"Total Actual: ${total_actual/1e6:.2f}M")
    print(f"Net Variance: ${net_variance/1e6:.2f}M ({net_variance_pct:.1f}%)")
    
    return ranked_df, fig


# Execute analysis
analysis_df, visualization = analyze_financial_performance(df)
visualization.show()


