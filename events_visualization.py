# events_visualization.py
# Multi-Source Events Data Visualization with Seaborn
# Compares: IDMC (GIDD), CRED (EM-DAT), IFRC (DREF+EA+EAP), UN Flash Appeals

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ============================================================
# DATA
# ============================================================
data = {
    'Year': [2020, 2021, 2022, 2023, 2024],
    'IDMC (GIDD)': [1800, 1200, 2400, 4000, 5000],
    'CRED (EM-DAT)': [507, 589, 594, 607, 565],
    'IFRC (DREF + EA + EAP)': [135, 162, 193, 210, 224],
    'UN Flash Appeals (OCHA-FTS)': [3, 7, 6, 7, 10]
}

df = pd.DataFrame(data)

# Melt for seaborn (long format)
df_long = df.melt(id_vars=['Year'], var_name='Source', value_name='Events')

# Set style
sns.set_theme(style="whitegrid", palette="deep")

# Color palette for sources (pleasant, accessible colors)
colors = {
    'IDMC (GIDD)': '#6366F1',              # Indigo - pleasant purple-blue
    'CRED (EM-DAT)': '#10B981',             # Emerald green
    'IFRC (DREF + EA + EAP)': '#F59E0B',    # Amber/Orange
    'UN Flash Appeals (OCHA-FTS)': '#3B82F6' # Sky blue
}


# ============================================================
# 1. GROUPED BAR CHART (Linear Scale)
# ============================================================
def plot_grouped_bar():
    fig, ax = plt.subplots(figsize=(12, 6))
    
    bar_width = 0.2
    years = df['Year'].values
    x = np.arange(len(years))
    
    sources = ['IDMC (GIDD)', 'CRED (EM-DAT)', 'IFRC (DREF + EA + EAP)', 'UN Flash Appeals (OCHA-FTS)']
    
    for i, source in enumerate(sources):
        ax.bar(x + i * bar_width, df[source], bar_width, 
               label=source, color=colors[source], edgecolor='white')
    
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Number of Events Recorded', fontsize=12)
    ax.set_title('Events Recorded by Data Source (2020-2024)', fontsize=14, fontweight='bold')
    ax.set_xticks(x + bar_width * 1.5)
    ax.set_xticklabels(years)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=4, frameon=True)
    
    plt.tight_layout()
    plt.savefig('events_grouped_bar.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("Saved: events_grouped_bar.png")


# ============================================================
# 2. STACKED AREA CHART (Cumulative Trends)
# ============================================================
def plot_stacked_area():
    fig, ax = plt.subplots(figsize=(12, 6))
    
    sources = ['UN Flash Appeals (OCHA-FTS)', 'IFRC (DREF + EA + EAP)', 'CRED (EM-DAT)', 'IDMC (GIDD)']
    color_list = [colors[s] for s in sources]
    
    ax.stackplot(df['Year'], 
                 [df[s] for s in sources],
                 labels=sources,
                 colors=color_list,
                 alpha=0.8)
    
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Cumulative Events', fontsize=12)
    ax.set_title('Cumulative Events by Data Source (Stacked Area)', fontsize=14, fontweight='bold')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=4, frameon=True)
    
    plt.tight_layout()
    plt.savefig('events_stacked_area.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("Saved: events_stacked_area.png")


# ============================================================
# 3. NORMALIZED 100% STACKED BAR (Proportions)
# ============================================================
def plot_normalized_stacked():
    fig, ax = plt.subplots(figsize=(12, 6))
    
    sources = ['IDMC (GIDD)', 'CRED (EM-DAT)', 'IFRC (DREF + EA + EAP)', 'UN Flash Appeals (OCHA-FTS)']
    
    # Calculate percentages
    df_pct = df.copy()
    totals = df_pct[sources].sum(axis=1)
    for source in sources:
        df_pct[source] = (df_pct[source] / totals) * 100
    
    bottom = np.zeros(len(df['Year']))
    
    for source in sources:
        ax.bar(df['Year'], df_pct[source], bottom=bottom, 
               label=source, color=colors[source], edgecolor='white', width=0.6)
        bottom += df_pct[source].values
    
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Percentage of Total Events (%)', fontsize=12)
    ax.set_title('Proportion of Events by Data Source (100% Stacked)', fontsize=14, fontweight='bold')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=4, frameon=True)
    ax.set_ylim(0, 100)
    
    plt.tight_layout()
    plt.savefig('events_normalized_stacked.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("Saved: events_normalized_stacked.png")


# ============================================================
# 4. SMALL MULTIPLES (Faceted Line Charts)
# ============================================================
def plot_small_multiples():
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    sources = ['IDMC (GIDD)', 'CRED (EM-DAT)', 'IFRC (DREF + EA + EAP)', 'UN Flash Appeals (OCHA-FTS)']
    
    for i, source in enumerate(sources):
        ax = axes[i]
        ax.plot(df['Year'], df[source], marker='o', linewidth=2.5, 
                markersize=8, color=colors[source])
        ax.fill_between(df['Year'], df[source], alpha=0.2, color=colors[source])
        
        ax.set_title(source, fontsize=12, fontweight='bold')
        ax.set_xlabel('Year')
        ax.set_ylabel('Events')
        ax.set_xticks(df['Year'])
        
        # Add value labels
        for x, y in zip(df['Year'], df[source]):
            ax.annotate(f'{y:,}', (x, y), textcoords="offset points", 
                       xytext=(0, 10), ha='center', fontsize=9)
        
        ax.grid(True, alpha=0.3)
    
    plt.suptitle('Events Recorded by Source (2020-2024)', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('events_small_multiples.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("Saved: events_small_multiples.png")


# ============================================================
# 5. SLOPE CHART (2020 vs 2024 Comparison)
# ============================================================
def plot_slope_chart():
    fig, ax = plt.subplots(figsize=(8, 8))
    
    sources = ['IDMC (GIDD)', 'CRED (EM-DAT)', 'IFRC (DREF + EA + EAP)', 'UN Flash Appeals (OCHA-FTS)']
    
    for source in sources:
        start = df[df['Year'] == 2020][source].values[0]
        end = df[df['Year'] == 2024][source].values[0]
        
        ax.plot([0, 1], [start, end], marker='o', linewidth=2.5, 
                markersize=10, color=colors[source], label=source)
        
        # Labels
        ax.annotate(f'{start:,}', (0, start), textcoords="offset points", 
                   xytext=(-30, 0), ha='right', fontsize=10)
        ax.annotate(f'{end:,}', (1, end), textcoords="offset points", 
                   xytext=(30, 0), ha='left', fontsize=10)
    
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['2020', '2024'], fontsize=12)
    ax.set_ylabel('Number of Events', fontsize=12)
    ax.set_title('Change in Events: 2020 → 2024', fontsize=14, fontweight='bold')
    ax.set_yscale('log')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=2, frameon=True)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('events_slope_chart.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("Saved: events_slope_chart.png")


# ============================================================
# 6. LINE CHART WITH LOG SCALE (Similar to Original)
# ============================================================
def plot_log_line():
    fig, ax = plt.subplots(figsize=(12, 6))
    
    sources = ['IDMC (GIDD)', 'CRED (EM-DAT)', 'IFRC (DREF + EA + EAP)', 'UN Flash Appeals (OCHA-FTS)']
    
    for source in sources:
        ax.plot(df['Year'], df[source], marker='o', linewidth=2.5, 
                markersize=8, color=colors[source], label=source)
    
    ax.set_yscale('log')
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Number of Events (Log Scale)', fontsize=12)
    ax.set_title('Events Recorded by Data Source - Log Scale', fontsize=14, fontweight='bold')
    ax.set_xticks(df['Year'])
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=4, frameon=True)
    ax.grid(True, alpha=0.3, which='both')
    
    plt.tight_layout()
    plt.savefig('events_log_line.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("Saved: events_log_line.png")


# ============================================================
# MAIN EXECUTION
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("MULTI-SOURCE EVENTS VISUALIZATION")
    print("=" * 60)
    print("\nData Sources:")
    print(df.to_string(index=False))
    
    print("\n" + "-" * 60)
    print("Generating visualizations...\n")
    
    print("\n1. Grouped Bar Chart (Linear Scale)")
    plot_grouped_bar()
    
    print("\n2. Stacked Area Chart")
    plot_stacked_area()
    
    print("\n3. Normalized 100% Stacked Bar")
    plot_normalized_stacked()
    
    print("\n4. Small Multiples (Faceted)")
    plot_small_multiples()
    
    print("\n5. Slope Chart (2020 vs 2024)")
    plot_slope_chart()
    
    print("\n6. Log Scale Line Chart")
    plot_log_line()
    
    print("\n" + "=" * 60)
    print("✓ All visualizations generated and saved!")
    print("=" * 60)
