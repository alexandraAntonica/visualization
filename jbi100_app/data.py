import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def get_data():
    df = pd.read_csv('ITA Case Detail Data 2023 through 8-31-2023.csv', low_memory=False)

    #Remove Uneccessary columns/Null values to reduce data loaded
    df = df.drop(columns=["ein", "date_of_death"], errors='ignore')
    df.replace("NULL", np.nan, inplace=True)
    df.dropna(inplace=True)

    #Convert date columns to DateTime format
    df['date_of_incident'] = pd.to_datetime(df['date_of_incident'], errors='coerce')
    df['time_started_work'] = pd.to_timedelta(df['time_started_work'], errors='coerce')
    df['time_of_incident'] = pd.to_timedelta(df['time_of_incident'], errors='coerce')

    #Keep only valid US states, add column for full state name
    state_abbrev_to_name = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
    "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire",
    "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York", "NC": "North Carolina",
    "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
    "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee",
    "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
    "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming"
    }
    valid_states = {
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA",
        "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT",
        "VA", "WA", "WV", "WI", "WY"
    }
    df = df[df["state"].isin(valid_states)]
    df["state_full_name"] = df["state"].map(state_abbrev_to_name)

    #Extract Industry Group
    df["industry_group"] = df["naics_code"].astype(str).str[:2]  

    #Group incident counts
    incident_counts = df.groupby('establishment_id')['case_number'].nunique().reset_index()
    incident_counts.rename(columns={'case_number': 'total_incidents'}, inplace=True)

    #Avoid summing Total hours worked across establishments 
    hours_worked = df.groupby('establishment_id', as_index=False)['total_hours_worked'].first()

    df = df.merge(incident_counts, on='establishment_id', how='left')
    df = df.merge(hours_worked, on='establishment_id', how='left')

    #Check for duplicated columns and remove, in case above section doesn't work properly
    if 'total_hours_worked_x' in df.columns and 'total_hours_worked_y' in df.columns:
        df.drop(columns=['total_hours_worked_x'], inplace=True)
        df.rename(columns={'total_hours_worked_y': 'total_hours_worked'}, inplace=True)

    #Calculate incident rate following formula
    df['incident_rate'] = (df['total_incidents'] * 200000) / df['total_hours_worked'].replace(0, np.nan)

    #Maps sizes to different bin groups
    size_mapping = {
        1: 'Small (0-19)',
        21: 'Medium (20-99)',
        22: 'Large (100-249)',
        3: 'Huge (250+)',
    }
    df['size_category'] = df['size'].map(size_mapping)

    #Additional features - Feature Engineering
    df['severity_index'] = df['dafw_num_away'] + df['djtr_num_tr']
    df['employee_exposure_rate'] = df['total_hours_worked'] / df['annual_average_employees']

    company_counts = df["state"].value_counts()
    df["num_companies_in_state"] = df["state"].map(company_counts)

    #Scale
    scaler = MinMaxScaler()
    df[['total_hours_worked']] = scaler.fit_transform(df[['total_hours_worked']])


    return df

