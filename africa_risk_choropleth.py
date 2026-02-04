# africa_risk_choropleth.py
# Population-Normalized Choropleth Maps for Africa Risk Scores
# Uses choropleth_mapbox with custom IFRC Mapbox tileset

import pandas as pd
import numpy as np
import json
import requests
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# MAPBOX CONFIGURATION - IFRC Custom Tileset
# ============================================================
MAPBOX_TOKEN = "pk.eyJ1IjoiZ28taWZyYyIsImEiOiJjbWYwdXhyaXIxYTk3MnJzNzliM3B4cHozIn0.lu7cqSPDHP4Mm2i00PcBQw"
MAPBOX_STYLE_URL = "mapbox://styles/go-ifrc/ckrfe16ru4c8718phmckdfjh0"

# Vector tile info (for reference)
# VECTOR_TILE = "mapbox://go-ifrc.go-countries"
# SOURCE_LAYER = "go-countries"
# VECTOR_PROPERTY = "iso3"

# Africa GeoJSON URL (with ISO3 codes)
GEOJSON_URL = "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"

# ============================================================
# DATA LOADING
# ============================================================
def load_geojson():
    """Load Africa countries GeoJSON from web."""
    print("Downloading world countries GeoJSON...")
    response = requests.get(GEOJSON_URL)
    world_geojson = response.json()
    
    # Filter to Africa countries (we'll use our data ISO3 codes to match)
    print(f"Loaded GeoJSON with {len(world_geojson['features'])} countries")
    return world_geojson


def load_and_normalize_data(excel_path="africa_risk_scores_analysis.xlsx"):
    """Load the summary data and calculate normalized scores."""
    
    # Read the country summary sheet
    summary_df = pd.read_excel(excel_path, sheet_name='Country_Summary')
    
    viz_df = summary_df.copy()
    
    # Calculate sqrt of population for normalization
    # Formula: Normalized Score = Yearly Average / sqrt(Population in Thousands)
    viz_df['Pop_Sqrt'] = np.sqrt(viz_df['Population_Thousands'])
    
    # Normalize each hazard and overall average
    viz_df['Drought_Norm'] = (viz_df['Drought_Avg'] / viz_df['Pop_Sqrt']).round(4)
    viz_df['Flood_Norm'] = (viz_df['Flood_Avg'] / viz_df['Pop_Sqrt']).round(4)
    viz_df['Overall_Norm'] = (viz_df['Overall_Avg'] / viz_df['Pop_Sqrt']).round(4)
    
    # Remove rows with missing ISO3 codes
    viz_df = viz_df[viz_df['ISO3'].notna() & (viz_df['ISO3'] != '')]
    
    print(f"Loaded {len(viz_df)} countries with normalized scores")
    return viz_df


# ============================================================
# COLOR SCALES
# ============================================================
# Sequential orange color scale (user preference)
RISK_COLOR_SCALE = [
    (0, "#fee6ce"),     # Light orange - Low risk
    (0.5, "#fdae6b"),   # Medium orange  
    (1, "#e6550d"),     # Dark orange - High risk
]

DROUGHT_COLOR_SCALE = [
    (0, "#fee6ce"),
    (0.5, "#fdae6b"),
    (1, "#e6550d"),
]

FLOOD_COLOR_SCALE = "Blues"  # Plotly built-in Blues


# ============================================================
# CHOROPLETH MAP FUNCTIONS (using choropleth_mapbox)
# ============================================================
def create_drought_map(viz_df, geojson_data):
    """Create Drought Risk choropleth map using Mapbox."""
    
    fig = px.choropleth_mapbox(
        viz_df,
        geojson=geojson_data,
        locations='ISO3',
        featureidkey='properties.ISO3166-1-Alpha-3',  # Match to GeoJSON property
        color='Drought_Norm',
        hover_name='Country',
        hover_data={
            'ISO3': True,
            'Drought_Avg': ':.2f',
            'Drought_Norm': ':.4f',
            'Population_Thousands': ':.0f',
            'Drought_GO_Cat': True
        },
        color_continuous_scale=DROUGHT_COLOR_SCALE,
        mapbox_style=MAPBOX_STYLE_URL,
        zoom=2.3,
        center={"lat": 0, "lon": 20},
        opacity=0.7,
    )
    
    fig.update_layout(
        mapbox=dict(accesstoken=MAPBOX_TOKEN),
        height=700,
        width=800,
        title_text="<b>Drought Risk Score (Population-Normalized)</b>",
        coloraxis_colorbar=dict(
            title="Score",
            orientation="h",
            x=0.5,
            y=-0.1,
            xanchor="center",
            tickvals=[viz_df['Drought_Norm'].min(), viz_df['Drought_Norm'].max()],
            ticktext=["Low", "High"]
        )
    )
    
    return fig


def create_flood_map(viz_df, geojson_data):
    """Create Flood Risk choropleth map using Mapbox."""
    
    fig = px.choropleth_mapbox(
        viz_df,
        geojson=geojson_data,
        locations='ISO3',
        featureidkey='properties.ISO3166-1-Alpha-3',
        color='Flood_Norm',
        hover_name='Country',
        hover_data={
            'ISO3': True,
            'Flood_Avg': ':.2f',
            'Flood_Norm': ':.4f',
            'Population_Thousands': ':.0f',
            'Flood_GO_Cat': True
        },
        color_continuous_scale=FLOOD_COLOR_SCALE,
        mapbox_style=MAPBOX_STYLE_URL,
        zoom=2.3,
        center={"lat": 0, "lon": 20},
        opacity=0.7,
    )
    
    fig.update_layout(
        mapbox=dict(accesstoken=MAPBOX_TOKEN),
        height=700,
        width=800,
        title_text="<b>Flood Risk Score (Population-Normalized)</b>",
        coloraxis_colorbar=dict(
            title="Score",
            orientation="h",
            x=0.5,
            y=-0.1,
            xanchor="center",
            tickvals=[viz_df['Flood_Norm'].min(), viz_df['Flood_Norm'].max()],
            ticktext=["Low", "High"]
        )
    )
    
    return fig


def create_overall_map(viz_df, geojson_data):
    """Create Overall Risk choropleth map using Mapbox."""
    
    fig = px.choropleth_mapbox(
        viz_df,
        geojson=geojson_data,
        locations='ISO3',
        featureidkey='properties.ISO3166-1-Alpha-3',
        color='Overall_Norm',
        hover_name='Country',
        hover_data={
            'ISO3': True,
            'Overall_Avg': ':.2f',
            'Overall_Norm': ':.4f',
            'Drought_Avg': ':.2f',
            'Flood_Avg': ':.2f',
            'Population_Thousands': ':.0f',
            'Overall_GO_Cat': True
        },
        color_continuous_scale=RISK_COLOR_SCALE,
        mapbox_style=MAPBOX_STYLE_URL,
        zoom=2.3,
        center={"lat": 0, "lon": 20},
        opacity=0.7,
    )
    
    fig.update_layout(
        mapbox=dict(accesstoken=MAPBOX_TOKEN),
        height=700,
        width=800,
        title_text="<b>Overall Risk Score (Population-Normalized)</b>",
        coloraxis_colorbar=dict(
            title="Score",
            orientation="h",
            x=0.5,
            y=-0.1,
            xanchor="center",
            tickvals=[viz_df['Overall_Norm'].min(), viz_df['Overall_Norm'].max()],
            ticktext=["Low", "High"]
        )
    )
    
    return fig


def create_raw_overall_map(viz_df, geojson_data):
    """Create Raw (non-normalized) Overall Risk choropleth for comparison."""
    
    fig = px.choropleth_mapbox(
        viz_df,
        geojson=geojson_data,
        locations='ISO3',
        featureidkey='properties.ISO3166-1-Alpha-3',
        color='Overall_Avg',
        hover_name='Country',
        hover_data={
            'ISO3': True,
            'Overall_Avg': ':.2f',
            'Drought_Avg': ':.2f',
            'Flood_Avg': ':.2f',
            'Population_Thousands': ':.0f'
        },
        color_continuous_scale="Reds",
        mapbox_style=MAPBOX_STYLE_URL,
        zoom=2.3,
        center={"lat": 0, "lon": 20},
        opacity=0.7,
    )
    
    fig.update_layout(
        mapbox=dict(accesstoken=MAPBOX_TOKEN),
        height=700,
        width=800,
        title_text="<b>Overall Risk Score</b>",
        coloraxis_colorbar=dict(
            title="Score",
            orientation="h",
            x=0.5,
            y=-0.1,
            xanchor="center",
            tickvals=[viz_df['Overall_Avg'].min(), viz_df['Overall_Avg'].max()],
            ticktext=["Low", "High"]
        )
    )
    
    return fig


def print_summary_statistics(viz_df):
    """Print summary statistics for normalized scores."""
    print("=" * 60)
    print("POPULATION-NORMALIZED RISK SCORE SUMMARY")
    print("=" * 60)
    print("\nFormula: Score_Normalized = Yearly_Avg / sqrt(Population_Thousands)")
    print("\n" + "-" * 60)
    
    for score_type in ['Drought', 'Flood', 'Overall']:
        norm_col = f'{score_type}_Norm'
        print(f"\n{score_type.upper()} (Normalized):")
        print(f"  Min: {viz_df[norm_col].min():.4f}")
        print(f"  Max: {viz_df[norm_col].max():.4f}")
        print(f"  Mean: {viz_df[norm_col].mean():.4f}")
        top = viz_df.nlargest(3, norm_col)[['Country', norm_col]]
        print(f"  Top 3: {', '.join(top['Country'].tolist())}")


# ============================================================
# MAIN EXECUTION
# ============================================================
if __name__ == "__main__":
    print("Loading GeoJSON and data...")
    geojson_data = load_geojson()
    viz_df = load_and_normalize_data()
    
    print("\nTop 10 countries by Overall Normalized Score:")
    print(viz_df.nlargest(10, 'Overall_Norm')[
        ['Country', 'ISO3', 'Population_Thousands', 
         'Drought_Avg', 'Drought_Norm',
         'Flood_Avg', 'Flood_Norm',
         'Overall_Avg', 'Overall_Norm']
    ].to_string(index=False))
    
    print_summary_statistics(viz_df)
    
    print("\n" + "=" * 60)
    print("GENERATING CHOROPLETH MAPS (saving as HTML)...")
    print("=" * 60)
    
    # Create and save all maps
    print("\n1. Drought Risk Map")
    fig_drought = create_drought_map(viz_df, geojson_data)
    fig_drought.write_html("drought_map.html", auto_open=True)
    print("   Saved: drought_map.html")
    
    print("\n2. Flood Risk Map")
    fig_flood = create_flood_map(viz_df, geojson_data)
    fig_flood.write_html("flood_map.html", auto_open=True)
    print("   Saved: flood_map.html")
    
    print("\n3. Overall Risk Map (Normalized)")
    fig_overall = create_overall_map(viz_df, geojson_data)
    fig_overall.write_html("overall_map.html", auto_open=True)
    print("   Saved: overall_map.html")
    
    print("\n4. Raw Overall Risk Map (for comparison)")
    fig_raw = create_raw_overall_map(viz_df, geojson_data)
    fig_raw.write_html("raw_overall_map.html", auto_open=True)
    print("   Saved: raw_overall_map.html")
    
    print("\n✓ All maps generated and saved as HTML files!")
