"""
=============================================================================
Africa Risk Score Analysis Script
=============================================================================

PURPOSE:
Fetches risk scores for Drought, Flood, and Wildfire for African countries 
(region=0 for sub-Saharan Africa and region=4 for North Africa) from the 
GO Risk API, calculates yearly averages, and categorizes using BOTH 
classification systems.

North African countries included: Morocco, Tunisia, Algeria, Libya, Egypt

=============================================================================
CLASSIFICATION SYSTEMS:
=============================================================================

1. GO PLATFORM CLASSIFICATION (5-point scale - as shown on GO website):
   Based on the screenshot showing "1: Very Low | 2: Low | 3: Medium | 4: High | 5: Very High"
   
   Score Range     Category Number     Category Name
   -----------     ---------------     -------------
   0.0 - 2.0            1              Very Low
   2.0 - 3.5            2              Low
   3.5 - 5.0            3              Medium
   5.0 - 6.5            4              High
   6.5 - 10.0           5              Very High

2. INFORM CLASSIFICATION (Text-based - used by INFORM Risk Index):
   Uses the same score ranges but without the 1-5 numbering system.
   
   Score Range     Category Name
   -----------     -------------
   0.0 - 2.0       Very Low
   2.0 - 3.5       Low
   3.5 - 5.0       Medium
   5.0 - 6.5       High
   6.5 - 10.0      Very High

=============================================================================
AVERAGE CALCULATION METHODOLOGY:
=============================================================================

The API provides monthly risk scores (january, february, ..., december).
There are THREE ways to calculate an "average":

1. YEARLY SUM (already in API as 'yearly_sum'):
   - Sum of all 12 monthly scores
   - Example: 4.1 + 3.9 + 4.1 + ... = 47.5
   - This represents CUMULATIVE annual exposure

2. YEARLY AVERAGE (Monthly Mean):
   - Yearly Sum ÷ 12
   - Example: 47.5 ÷ 12 = 3.96
   - This represents AVERAGE monthly risk level
   - USE THIS for category classification

3. PEAK MONTH SCORE:
   - Maximum score among all 12 months
   - Example: max(4.1, 3.9, 4.1, ...) = 4.2
   - This represents WORST month risk level

=============================================================================
"""

import requests
import pandas as pd
from datetime import datetime


# North African countries to include when fetching from region 4
NORTH_AFRICA_COUNTRIES = ['Morocco', 'Tunisia', 'Algeria', 'Libya', 'Egypt']

# Hazard types to include in the analysis
INCLUDED_HAZARDS = ['Drought', 'Flood', 'Wildfire']


def fetch_risk_scores(region=0, limit=9999):
    """
    Fetch risk scores from GO Risk API for a specific region.
    
    Parameters:
    -----------
    region : int
        Region code (0 = Sub-Saharan Africa, 4 = North Africa)
    limit : int
        Maximum number of records to fetch
        
    Returns:
    --------
    list : List of risk score records from API
    """
    url = f"https://go-risk.northeurope.cloudapp.azure.com/api/v1/risk-score/?region={region}&limit={limit}"
    
    print(f"Fetching data from: {url}")
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"API request failed with status code: {response.status_code}")
    
    data = response.json()
    print(f"Successfully fetched {data['count']} records")
    return data['results']


def fetch_all_africa_data():
    """
    Fetch risk scores for all of Africa by combining:
    - Region 0 (Sub-Saharan Africa)
    - Region 4 (North Africa) - filtered to specific countries
    
    North African countries: Morocco, Tunisia, Algeria, Libya, Egypt
    
    Returns:
    --------
    list : Combined list of risk score records for all African countries
    """
    # Fetch Sub-Saharan Africa data (region 0)
    print("\n--- Fetching Sub-Saharan Africa (region=0) ---")
    sub_saharan_results = fetch_risk_scores(region=0)
    print(f"Sub-Saharan Africa records: {len(sub_saharan_results)}")
    
    # Fetch North Africa data (region 4)
    print("\n--- Fetching North Africa (region=4) ---")
    north_africa_results = fetch_risk_scores(region=4)
    print(f"North Africa records (before filtering): {len(north_africa_results)}")
    
    # Filter North Africa to only include specific countries
    filtered_north_africa = [
        record for record in north_africa_results
        if record['country_details']['name'] in NORTH_AFRICA_COUNTRIES
    ]
    print(f"North Africa records (after filtering to {NORTH_AFRICA_COUNTRIES}): {len(filtered_north_africa)}")
    
    # Combine the datasets
    all_africa_results = sub_saharan_results + filtered_north_africa
    print(f"\nTotal Africa records: {len(all_africa_results)}")
    
    return all_africa_results


def filter_by_hazard_type(results, hazard_types=None):
    """
    Filter results to only include specified hazard types.
    
    Parameters:
    -----------
    results : list
        List of risk score records
    hazard_types : list
        List of hazard types to include (e.g., ['Drought', 'Flood', 'Wildfire'])
        If None, uses INCLUDED_HAZARDS constant
        
    Returns:
    --------
    list : Filtered list of risk score records
    """
    if hazard_types is None:
        hazard_types = INCLUDED_HAZARDS
    
    filtered_results = [
        record for record in results
        if record['hazard_type_display'] in hazard_types
    ]
    
    print(f"Filtered to hazards {hazard_types}: {len(filtered_results)} records")
    return filtered_results


def categorize_go_platform(score):
    """
    Categorize risk score using GO Platform methodology (5-point numbered scale).
    
    This is the classification shown on the GO website:
    "1: Very Low | 2: Low | 3: Medium | 4: High | 5: Very High"
    
    Parameters:
    -----------
    score : float
        Risk score (0-10 scale)
        
    Returns:
    --------
    tuple : (category_number, category_name)
    """
    if score is None or pd.isna(score):
        return (0, "No Data")
    elif score < 2.0:
        return (1, "Very Low")
    elif score < 3.5:
        return (2, "Low")
    elif score < 5.0:
        return (3, "Medium")
    elif score < 6.5:
        return (4, "High")
    else:
        return (5, "Very High")


def categorize_inform(score):
    """
    Categorize risk score using INFORM methodology (text-based categories).
    
    This is the standard INFORM Risk Index classification:
    - Very Low: 0 - 2.0
    - Low: 2.0 - 3.5
    - Medium: 3.5 - 5.0
    - High: 5.0 - 6.5
    - Very High: 6.5 - 10.0
    
    Parameters:
    -----------
    score : float
        Risk score (0-10 scale)
        
    Returns:
    --------
    str : Category name
    """
    if score is None or pd.isna(score):
        return "No Data"
    elif score < 2.0:
        return "Very Low"
    elif score < 3.5:
        return "Low"
    elif score < 5.0:
        return "Medium"
    elif score < 6.5:
        return "High"
    else:
        return "Very High"


def process_risk_data(results):
    """
    Process raw API results into structured data with calculations.
    
    This function:
    1. Extracts country and hazard information
    2. Retrieves all 12 monthly scores
    3. Calculates Yearly Sum and Yearly Average
    4. Applies BOTH classification methods
    
    Parameters:
    -----------
    results : list
        Raw API results
        
    Returns:
    --------
    list : Processed data records
    """
    
    processed_data = []
    
    for record in results:
        # =====================================================================
        # STEP 1: Extract basic country and hazard information
        # =====================================================================
        country_name = record['country_details']['name']
        country_iso3 = record['country_details']['iso3'].upper()
        hazard_type = record['hazard_type_display']  # "Cyclone", "Drought", or "Flood"
        
        # =====================================================================
        # STEP 2: Extract all 12 monthly risk scores
        # =====================================================================
        months = ['january', 'february', 'march', 'april', 'may', 'june',
                  'july', 'august', 'september', 'october', 'november', 'december']
        
        # Get monthly scores (default to 0 if None)
        monthly_scores = [record.get(month, 0) or 0 for month in months]
        
        # =====================================================================
        # STEP 3: Calculate averages
        # =====================================================================
        
        # YEARLY SUM: Total of all 12 monthly scores (already provided by API)
        yearly_sum = record.get('yearly_sum', sum(monthly_scores))
        
        # YEARLY AVERAGE: Mean of monthly scores (Sum ÷ 12)
        # This is what we use for category classification
        yearly_avg = yearly_sum / 12 if yearly_sum else 0
        
        # PEAK MONTH: Maximum score in any single month
        peak_month_score = max(monthly_scores) if monthly_scores else 0
        
        # =====================================================================
        # STEP 4: Apply BOTH classification systems
        # =====================================================================
        
        # GO Platform Classification (numbered 1-5)
        go_cat_num, go_cat_name = categorize_go_platform(yearly_avg)
        
        # INFORM Classification (text only)
        inform_category = categorize_inform(yearly_avg)
        
        # Also categorize the peak month score
        peak_go_num, peak_go_name = categorize_go_platform(peak_month_score)
        peak_inform = categorize_inform(peak_month_score)
        
        # =====================================================================
        # STEP 5: Get additional vulnerability metrics from API
        # =====================================================================
        lcc = record.get('lcc', 0)  # Lack of Coping Capacity
        vulnerability = record.get('vulnerability', 0)
        population = record.get('population_in_thousands', 0)
        
        # =====================================================================
        # STEP 6: Build the processed record
        # =====================================================================
        processed_data.append({
            # Country info
            'Country': country_name,
            'ISO3': country_iso3,
            'Hazard_Type': hazard_type,
            
            # Monthly scores
            'January': monthly_scores[0],
            'February': monthly_scores[1],
            'March': monthly_scores[2],
            'April': monthly_scores[3],
            'May': monthly_scores[4],
            'June': monthly_scores[5],
            'July': monthly_scores[6],
            'August': monthly_scores[7],
            'September': monthly_scores[8],
            'October': monthly_scores[9],
            'November': monthly_scores[10],
            'December': monthly_scores[11],
            
            # Calculated values
            'Yearly_Sum': round(yearly_sum, 2),
            'Yearly_Average': round(yearly_avg, 2),
            'Peak_Month_Score': round(peak_month_score, 2),
            
            # GO Platform Classification (1-5 scale)
            'GO_Category_Num': go_cat_num,
            'GO_Category': go_cat_name,
            
            # INFORM Classification (text-based)
            'INFORM_Category': inform_category,
            
            # Peak month classifications
            'Peak_GO_Num': peak_go_num,
            'Peak_GO_Category': peak_go_name,
            'Peak_INFORM_Category': peak_inform,
            
            # Vulnerability metrics
            'LCC': lcc,
            'Vulnerability': vulnerability,
            'Population_Thousands': population
        })
    
    return processed_data


def create_summary_by_country(df):
    """
    Create a summary view with all hazard types per country in columns.
    
    This creates a wide-format table where each row is a country
    and columns contain data for each hazard type.
    """
    
    summary_data = []
    countries = df['Country'].unique()
    
    for country in sorted(countries):
        country_data = df[df['Country'] == country]
        
        row = {
            'Country': country,
            'ISO3': country_data['ISO3'].iloc[0],
            'Population_Thousands': country_data['Population_Thousands'].iloc[0],
            'LCC': country_data['LCC'].iloc[0],
            'Vulnerability': country_data['Vulnerability'].iloc[0],
        }
        
        # Add data for each hazard type (Drought, Flood, Wildfire)
        for hazard in INCLUDED_HAZARDS:
            hazard_row = country_data[country_data['Hazard_Type'] == hazard]
            if not hazard_row.empty:
                row[f'{hazard}_Sum'] = hazard_row['Yearly_Sum'].values[0]
                row[f'{hazard}_Avg'] = hazard_row['Yearly_Average'].values[0]
                row[f'{hazard}_Peak'] = hazard_row['Peak_Month_Score'].values[0]
                row[f'{hazard}_GO_Num'] = hazard_row['GO_Category_Num'].values[0]
                row[f'{hazard}_GO_Cat'] = hazard_row['GO_Category'].values[0]
                row[f'{hazard}_INFORM'] = hazard_row['INFORM_Category'].values[0]
            else:
                row[f'{hazard}_Sum'] = 0
                row[f'{hazard}_Avg'] = 0
                row[f'{hazard}_Peak'] = 0
                row[f'{hazard}_GO_Num'] = 0
                row[f'{hazard}_GO_Cat'] = 'No Data'
                row[f'{hazard}_INFORM'] = 'No Data'
        
        # Calculate overall average across all hazards
        hazard_avgs = [row.get(f'{h}_Avg', 0) for h in INCLUDED_HAZARDS]
        total_avg = sum(hazard_avgs) / len(INCLUDED_HAZARDS)
        row['Overall_Avg'] = round(total_avg, 2)
        
        # Classify overall average using both methods
        go_num, go_cat = categorize_go_platform(total_avg)
        row['Overall_GO_Num'] = go_num
        row['Overall_GO_Cat'] = go_cat
        row['Overall_INFORM'] = categorize_inform(total_avg)
        
        summary_data.append(row)
    
    return pd.DataFrame(summary_data)


def export_to_excel(detailed_df, summary_df, output_path):
    """Export data to Excel with multiple sheets and formatting."""
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Sheet 1: Country Summary (all hazards per country)
        summary_df.to_excel(writer, sheet_name='Country_Summary', index=False)
        
        # Sheet 2: Detailed Data (all monthly scores)
        detailed_df.to_excel(writer, sheet_name='Detailed_Monthly', index=False)
        
        # Create separate sheets for each hazard type
        for hazard in INCLUDED_HAZARDS:
            hazard_df = detailed_df[detailed_df['Hazard_Type'] == hazard].copy()
            hazard_df.to_excel(writer, sheet_name=hazard, index=False)
        
        # Sheet 6: Classification Reference (BOTH systems explained)
        classification_data = {
            'Score_Range': ['0.0 - 2.0', '2.0 - 3.5', '3.5 - 5.0', '5.0 - 6.5', '6.5 - 10.0'],
            'GO_Platform_Number': [1, 2, 3, 4, 5],
            'GO_Platform_Category': ['Very Low', 'Low', 'Medium', 'High', 'Very High'],
            'INFORM_Category': ['Very Low', 'Low', 'Medium', 'High', 'Very High'],
            'Description': [
                'Minimal seasonal hazard risk',
                'Low seasonal hazard risk - some monitoring needed',
                'Moderate seasonal hazard risk - preparedness recommended',
                'Significant seasonal hazard risk - action required',
                'Severe seasonal hazard risk - immediate attention needed'
            ]
        }
        classification_df = pd.DataFrame(classification_data)
        classification_df.to_excel(writer, sheet_name='Classification_Reference', index=False)
        
        # Sheet 7: Methodology explanation
        methodology_data = {
            'Metric': [
                'Monthly Score',
                'Yearly Sum',
                'Yearly Average',
                'Peak Month Score',
                'GO Classification',
                'INFORM Classification'
            ],
            'Formula': [
                'Direct from API (0-10 scale)',
                'Sum of 12 monthly scores',
                'Yearly Sum ÷ 12',
                'Maximum of 12 monthly scores',
                'Based on Yearly Average (1-5 scale)',
                'Based on Yearly Average (text labels)'
            ],
            'Example': [
                'January: 4.1',
                '4.1+3.9+4.1+...= 47.5',
                '47.5 ÷ 12 = 3.96',
                'max(4.1, 3.9, 4.2...) = 4.2',
                '3.96 → Category 3 (Medium)',
                '3.96 → Medium'
            ],
            'Purpose': [
                'Risk level for specific month',
                'Cumulative annual exposure',
                'Average monthly risk level (USED FOR CLASSIFICATION)',
                'Worst-case monthly risk',
                'Matches GO platform display',
                'Standard INFORM terminology'
            ]
        }
        methodology_df = pd.DataFrame(methodology_data)
        methodology_df.to_excel(writer, sheet_name='Methodology', index=False)
    
    print(f"Excel file saved to: {output_path}")


def main():
    """Main function to orchestrate the data processing pipeline."""
    
    print("=" * 70)
    print("AFRICA RISK SCORE ANALYSIS")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Step 1: Fetch data from API (both Sub-Saharan and North Africa)
    print("\n[1/5] Fetching risk scores from GO Risk API...")
    all_results = fetch_all_africa_data()
    
    # Step 2: Filter to only include specific hazard types
    print("\n[2/5] Filtering to selected hazard types...")
    filtered_results = filter_by_hazard_type(all_results)
    
    # Step 3: Process and calculate
    print("\n[3/5] Processing data and calculating averages...")
    processed_data = process_risk_data(filtered_results)
    detailed_df = pd.DataFrame(processed_data)
    
    # Step 4: Create summary
    print("\n[4/5] Creating country summary...")
    summary_df = create_summary_by_country(detailed_df)
    
    # Step 5: Export to Excel
    print("\n[5/5] Exporting to Excel...")
    output_path = "africa_risk_scores_analysis.xlsx"
    export_to_excel(detailed_df, summary_df, output_path)
    
    # Print summary statistics
    print("\n" + "=" * 70)
    print("SUMMARY STATISTICS")
    print("=" * 70)
    print(f"Total countries analyzed: {len(summary_df)}")
    print(f"Total records processed: {len(detailed_df)}")
    
    print("\n" + "-" * 70)
    print("RISK CATEGORY DISTRIBUTION (Based on Yearly Average)")
    print("-" * 70)
    
    for hazard in INCLUDED_HAZARDS:
        print(f"\n{hazard.upper()}:")
        hazard_df = detailed_df[detailed_df['Hazard_Type'] == hazard]
        
        print("  GO Platform (1-5):")
        go_counts = hazard_df['GO_Category'].value_counts()
        for cat in ['Very Low', 'Low', 'Medium', 'High', 'Very High']:
            count = go_counts.get(cat, 0)
            print(f"    {cat}: {count} countries")
    
    print("\n" + "-" * 70)
    print("TOP 5 COUNTRIES BY OVERALL RISK")
    print("-" * 70)
    top_5 = summary_df.nlargest(5, 'Overall_Avg')[
        ['Country', 'Overall_Avg', 'Overall_GO_Num', 'Overall_GO_Cat', 'Overall_INFORM']
    ]
    print(top_5.to_string(index=False))
    
    print("\n" + "=" * 70)
    print("✅ Analysis complete! Check 'africa_risk_scores_analysis.xlsx'")
    print("=" * 70)
    
    return detailed_df, summary_df


if __name__ == "__main__":
    detailed_df, summary_df = main()
