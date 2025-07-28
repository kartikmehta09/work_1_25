
import pandas as pd
import numpy as np

# Sample data with realistic overspend pattern (normal + outliers)
data = {
    'cost_center': ['IT', 'HR', 'Finance', 'Marketing', 'Operations', 'Legal', 'R&D', 'Sales', 
                   'Admin', 'Security', 'Manufacturing', 'Executive', 'Consulting'],
    'budget': [5000000, 1000000, 8000000, 2000000, 6000000, 500000, 3000000, 4000000,
              1500000, 750000, 12000000, 2000000, 15000000],
    'actual': [5250000, 1200000, 8500000, 2800000, 7500000, 650000, 3450000, 4800000,
              1680000, 850000, 32000000, 62000000, 95000000]
}

df = pd.DataFrame(data)

# STEP 1: Calculate actual overspend for each cost center
df['overspend_amount'] = df['actual'] - df['budget']

# STEP 2: Only work with departments that actually overspent (positive overspend)
df_overspend = df[df['overspend_amount'] > 0].copy()

print("=== EACH COST CENTER'S ACTUAL OVERSPEND ===")
for i, row in df_overspend.iterrows():
    print(f"{row['cost_center']}: ${row['overspend_amount']:,.0f}")

# STEP 3: Calculate IQR components to find the "normal" range
q1 = df_overspend['overspend_amount'].quantile(0.25)  # 25th percentile
q3 = df_overspend['overspend_amount'].quantile(0.75)  # 75th percentile
iqr = q3 - q1  # Interquartile Range (middle 50% spread)

print(f"\n=== IQR ANALYSIS ===")
print(f"Q1 (25th percentile): ${q1:,.0f}")
print(f"Q3 (75th percentile): ${q3:,.0f}")
print(f"IQR (Q3 - Q1): ${iqr:,.0f}")

# STEP 4: Calculate the target threshold (outlier detection)
iqr_target = q3 + (1.5 * iqr)
print(f"IQR Target (Q3 + 1.5*IQR): ${iqr_target:,.0f}")
print(f"Any department over ${iqr_target:,.0f} is considered a statistical outlier")

# STEP 5: Calculate potential savings for EACH cost center individually
print(f"\n=== POTENTIAL SAVINGS FOR EACH COST CENTER ===")

df_overspend['target_overspend'] = iqr_target  # What they should overspend (max)
df_overspend['potential_savings'] = 0  # Initialize savings column

total_potential_savings = 0

for i, row in df_overspend.iterrows():
    current_overspend = row['overspend_amount']
    
    if current_overspend > iqr_target:
        # This department is over the target - they can save money
        savings = current_overspend - iqr_target
        df_overspend.loc[i, 'potential_savings'] = savings
        total_potential_savings += savings
        
        print(f"{row['cost_center']}:")
        print(f"  Current overspend: ${current_overspend:,.0f}")
        print(f"  Target overspend:  ${iqr_target:,.0f}")
        print(f"  Potential savings: ${savings:,.0f}")
        print()
    else:
        # This department is already within target - no savings needed
        df_overspend.loc[i, 'potential_savings'] = 0
        print(f"{row['cost_center']}: Already within target (${current_overspend:,.0f} ≤ ${iqr_target:,.0f}) - No reduction needed")

print(f"\n=== SUMMARY OF ALL COST CENTERS ===")
print(f"{'Cost Center':<15} {'Current Overspend':<18} {'Target Overspend':<17} {'Potential Savings':<17}")
print("-" * 70)

for i, row in df_overspend.iterrows():
    print(f"{row['cost_center']:<15} ${row['overspend_amount']:<17,.0f} ${iqr_target:<16,.0f} ${row['potential_savings']:<16,.0f}")

print(f"\nTOTAL POTENTIAL SAVINGS: ${total_potential_savings:,.0f}")

# STEP 6: Show which departments need action vs which are already good
departments_need_action = df_overspend[df_overspend['potential_savings'] > 0]
departments_already_good = df_overspend[df_overspend['potential_savings'] == 0]

print(f"\n=== DEPARTMENTS THAT NEED TO REDUCE OVERSPEND ===")
print(f"Count: {len(departments_need_action)} out of {len(df_overspend)} departments")
for i, row in departments_need_action.iterrows():
    reduction_percentage = (row['potential_savings'] / row['overspend_amount']) * 100
    print(f"- {row['cost_center']}: Reduce by ${row['potential_savings']:,.0f} ({reduction_percentage:.1f}% reduction)")

print(f"\n=== DEPARTMENTS ALREADY WITHIN TARGET ===")
print(f"Count: {len(departments_already_good)} out of {len(df_overspend)} departments")
for i, row in departments_already_good.iterrows():
    print(f"- {row['cost_center']}: ${row['overspend_amount']:,.0f} (no action needed)")

# STEP 7: Calculate company-wide impact
total_current_overspend = df_overspend['overspend_amount'].sum()
total_after_savings = total_current_overspend - total_potential_savings
savings_percentage = (total_potential_savings / total_current_overspend) * 100

print(f"\n=== COMPANY-WIDE IMPACT ===")
print(f"Current total overspend: ${total_current_overspend:,.0f}")
print(f"Total after reductions:  ${total_after_savings:,.0f}")
print(f"Total potential savings: ${total_potential_savings:,.0f}")
print(f"Overall savings rate:    {savings_percentage:.1f}%")

## Method 2

import pandas as pd
import numpy as np

# Sample data representing cost centers with realistic overspend pattern
# Most departments: 50K - 2M range, Few outliers: 20M - 80M range
data = {
    'cost_center': ['IT', 'HR', 'Finance', 'Marketing', 'Operations', 'Legal', 'R&D', 'Sales', 
                   'Admin', 'Security', 'Facilities', 'Procurement', 'Customer_Service', 
                   'Quality', 'Manufacturing', 'Logistics', 'Training', 'Compliance',
                   'Executive', 'Consulting'],
    'budget': [5000000, 1000000, 8000000, 2000000, 6000000, 500000, 3000000, 4000000,
              1500000, 750000, 2500000, 1800000, 1200000, 900000, 12000000, 3500000,
              600000, 800000, 2000000, 15000000],
    'actual': [5250000, 1200000, 8500000, 2800000, 7500000, 650000, 3450000, 4800000,
              1680000, 850000, 2750000, 1980000, 1350000, 1080000, 32000000, 4200000,
              750000, 950000, 62000000, 95000000]
}

# Create DataFrame
df = pd.DataFrame(data)

# Calculate overspend amounts for each cost center
df['overspend_amount'] = df['actual'] - df['budget']

# Remove any departments that are under budget (negative overspend) for this analysis
# We only want to analyze departments that actually overspent
df_overspend = df[df['overspend_amount'] > 0].copy()

# Get the total actual overspend across all cost centers
total_actual_overspend = df_overspend['overspend_amount'].sum()

# Calculate IQR (Interquartile Range) components
# Q1 = 25th percentile, Q3 = 75th percentile
q1 = df_overspend['overspend_amount'].quantile(0.25)  # 25th percentile
q3 = df_overspend['overspend_amount'].quantile(0.75)  # 75th percentile
iqr = q3 - q1  # Interquartile Range

# Calculate IQR-based target using 1.5 * IQR above Q3
# This is the standard statistical method for detecting outliers
iqr_target = q3 + (1.5 * iqr)

# Identify departments that exceed the IQR target (these are statistical outliers)
departments_above_iqr = df_overspend[df_overspend['overspend_amount'] > iqr_target].copy()
departments_within_iqr = df_overspend[df_overspend['overspend_amount'] <= iqr_target].copy()

# Calculate how much each outlier department exceeds the IQR target
departments_above_iqr['excess_over_iqr'] = departments_above_iqr['overspend_amount'] - iqr_target

# Total potential savings if all outlier departments reduce to IQR target level
total_potential_savings = departments_above_iqr['excess_over_iqr'].sum()

# Calculate what total overspend would be if all departments hit IQR target
# Departments already within target stay the same, outliers reduce to target
total_if_iqr_target = departments_within_iqr['overspend_amount'].sum() + (len(departments_above_iqr) * iqr_target)

# Create summary of departments that need to reduce overspend
priority_departments = departments_above_iqr[['cost_center', 'overspend_amount', 'excess_over_iqr']].copy()
priority_departments = priority_departments.sort_values('excess_over_iqr', ascending=False)

# Calculate some additional statistics for context
median_overspend = df_overspend['overspend_amount'].median()
mean_overspend = df_overspend['overspend_amount'].mean()
max_overspend = df_overspend['overspend_amount'].max()
min_overspend = df_overspend['overspend_amount'].min()

# Show distribution of overspend amounts
overspend_distribution = {
    'total_departments': len(df_overspend),
    'departments_within_normal_range': len(departments_within_iqr),
    'departments_statistical_outliers': len(departments_above_iqr),
    'q1_25th_percentile': q1,
    'median_50th_percentile': median_overspend,
    'q3_75th_percentile': q3,
    'iqr_range': iqr,
    'iqr_target_threshold': iqr_target
}

# Results summary
analysis_results = {
    'total_actual_overspend': total_actual_overspend,
    'total_potential_savings': total_potential_savings,
    'total_if_all_hit_target': total_if_iqr_target,
    'savings_percentage': (total_potential_savings / total_actual_overspend) * 100,
    'iqr_target_amount': iqr_target
}

## Visualization 

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Sample data with realistic overspend pattern
data = {
    'cost_center': ['IT', 'HR', 'Finance', 'Marketing', 'Operations', 'Legal', 'R&D', 'Sales', 
                   'Admin', 'Security', 'Facilities', 'Procurement', 'Manufacturing', 'Executive', 'Consulting'],
    'budget': [5000000, 1000000, 8000000, 2000000, 6000000, 500000, 3000000, 4000000,
              1500000, 750000, 2500000, 1800000, 12000000, 2000000, 15000000],
    'actual': [5250000, 1200000, 8500000, 2800000, 7500000, 650000, 3450000, 4800000,
              1680000, 850000, 2750000, 1980000, 32000000, 62000000, 95000000]
}

# Create DataFrame and calculate overspend
df = pd.DataFrame(data)
df['overspend_amount'] = df['actual'] - df['budget']

# Only show departments that overspent (positive values)
df_overspend = df[df['overspend_amount'] > 0].copy()

# Sort by overspend amount for better visualization
df_overspend = df_overspend.sort_values('overspend_amount', ascending=True)

# Create simple bar chart
fig = px.bar(df_overspend, 
             x='overspend_amount', 
             y='cost_center',
             orientation='h',
             title='Cost Center Overspend Analysis',
             labels={'overspend_amount': 'Overspend Amount ($)', 'cost_center': 'Cost Center'},
             color='overspend_amount',
             color_continuous_scale='Reds')

# Format the chart
fig.update_layout(
    width=900,
    height=600,
    showlegend=False,
    title_font_size=20,
    title_x=0.5
)

# Format x-axis to show money format
fig.update_xaxes(tickformat='$,.0f')

# Add value labels on bars
fig.update_traces(texttemplate='$%{x:,.0f}', textposition='outside')

# Show the chart
fig.show()

# Alternative: Vertical bar chart (if you prefer)
fig2 = px.bar(df_overspend.sort_values('overspend_amount', ascending=False), 
              x='cost_center', 
              y='overspend_amount',
              title='Cost Center Overspend - Vertical View',
              labels={'overspend_amount': 'Overspend Amount ($)', 'cost_center': 'Cost Center'},
              color='overspend_amount',
              color_continuous_scale='Oranges')

# Rotate x-axis labels for better readability
fig2.update_layout(
    width=1000,
    height=600,
    showlegend=False,
    title_font_size=20,
    title_x=0.5,
    xaxis_tickangle=-45
)

# Format y-axis to show money format
fig2.update_yaxes(tickformat='$,.0f')

# Add value labels on top of bars
fig2.update_traces(texttemplate='$%{y:,.0f}', textposition='outside')

# Show the second chart
fig2.show()

# Simple scatter plot to show relationship between budget and overspend
fig3 = px.scatter(df_overspend, 
                  x='budget', 
                  y='overspend_amount',
                  text='cost_center',
                  title='Budget vs Overspend by Cost Center',
                  labels={'budget': 'Budget Amount ($)', 'overspend_amount': 'Overspend Amount ($)'},
                  size='overspend_amount',
                  color='overspend_amount',
                  color_continuous_scale='Viridis')

# Format the scatter plot
fig3.update_layout(
    width=900,
    height=600,
    showlegend=False,
    title_font_size=20,
    title_x=0.5
)

# Format axes to show money format
fig3.update_xaxes(tickformat='$,.0f')
fig3.update_yaxes(tickformat='$,.0f')

# Position text labels
fig3.update_traces(textposition="top center")

# Show the third chart
fig3.show()

