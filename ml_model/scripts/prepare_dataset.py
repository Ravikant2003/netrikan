#!/usr/bin/env python3
"""
Prepare Bengaluru Safety Dataset for XGBoost Training
Uses real Karnataka crime data 2024 & 2025 from data.opencity.in
"""

import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "data"

BENGALURU_DISTRICT_COORDS = {
    "Bengaluru City": {"lat": 12.9716, "lon": 77.5946, "population_density": 18000},
    "Bengaluru Dist": {"lat": 13.0218, "lon": 77.5643, "population_density": 1500},
    "Bengaluru South": {"lat": 12.9173, "lon": 77.6785, "population_density": 3000},
    "Bengaluru North": {"lat": 13.0789, "lon": 77.5456, "population_density": 2500},
    "Mysuru City": {"lat": 12.2958, "lon": 76.6394, "population_density": 6000},
    "Hubballi Dharwad City": {"lat": 15.3647, "lon": 75.1248, "population_density": 4500},
    "Mangaluru City": {"lat": 12.9141, "lon": 74.8559, "population_density": 5000},
    "Belagavi City": {"lat": 15.8497, "lon": 74.4973, "population_density": 4000},
    "Kalaburagi City": {"lat": 17.3292, "lon": 76.8348, "population_density": 3500},
    "Tumakuru": {"lat": 13.3409, "lon": 77.1172, "population_density": 1200},
    "Kolar": {"lat": 13.1363, "lon": 78.1333, "population_density": 800},
    "Ramanagara": {"lat": 12.7167, "lon": 77.2833, "population_density": 600},
}

CRIME_WEIGHTS = {
    "theft": 0.3,
    "robbery": 0.7,
    "molestation": 0.6,  # Includes eve teasing
    "eve_teasing": 0.6,
    "woman_abuse": 0.8,  # Domestic violence
    "dowry_deaths": 0.9,
    "kidnapping": 0.85,
    "pocso": 0.8,
    "rape": 0.9,
    "dacoity": 0.8,
    "murder": 1.0,
    "burglary_day": 0.35,
    "burglary_night": 0.45,
    "riots": 0.5,
    "cases_of_hurt": 0.4,
}

def load_crime_2024():
    """Load 2024 district-wise crime data with categories"""
    path = DATA_DIR / "district_crime_2024.csv"
    df = pd.read_csv(path)
    
    df_clean = df.dropna(subset=["Sl No"]).copy()
    df_clean["Sl No"] = df_clean["Sl No"].astype(int)
    
    rows = []
    for _, row in df_clean.iterrows():
        district = str(row.get("DISTRICT/UNITS", "")).strip()
        exclude_terms = ["Commissionerates", "Central Range", "Eastern Range", "Western Range", "nan", ""]
        if district and district not in exclude_terms:
            rows.append({
                "district": district,
                "theft": int(row.get("THEFT", 0) or 0),
                "robbery": int(row.get("ROBBERY", 0) or 0),
                "molestation": int(row.get("MOLESTATION", 0) or 0),  # Includes eve teasing
                "eve_teasing": int(row.get("MOLESTATION", 0) or 0),  # Explicitly tracked
                "woman_abuse": int(row.get("CRUELTY BY HUSBAND", 0) or 0),  # Domestic violence
                "dowry_deaths": int(row.get("DOWRY DEATHS", 0) or 0),  # Dowry deaths
                "kidnapping": int(row.get("KIDNAPPING", 0) or 0),  # If available
                "pocso": int(row.get("POCSO", 0) or 0),
                "pocso_rape": int(row.get("POCSO RAPE", 0) or 0),
                "rape": int(row.get("RAPE", 0) or 0),
                "dacoity": int(row.get("DACOITY", 0) or 0),
                "murder": int(row.get("MURDER", 0) or 0),
                "burglary_day": int(row.get("BURGLARY-DAY", 0) or 0),
                "burglary_night": int(row.get("BURGLARY-NIGHT", 0) or 0),
                "riots": int(row.get("RIOTS", 0) or 0),
                "cases_of_hurt": int(row.get("CASES OF HURT", 0) or 0),
                "fatal_motor_accidents": int(row.get("FATAL MOTOR ACCIDENTS", 0) or 0),
                "non_fatal_motor_accidents": int(row.get("NON-FATAL MOTOR ACCIDENTS", 0) or 0),
            })
    
    result = pd.DataFrame(rows)
    print(f"    Loaded {len(result)} districts from 2024")
    return result

def load_crime_2025():
    """Load 2025 district-wise crime data (aggregate)"""
    path = DATA_DIR / "district_crime_2025.csv"
    df = pd.read_csv(path)
    
    df_clean = df.dropna(subset=["Sl No"]).copy()
    df_clean["Sl No"] = df_clean["Sl No"].astype(int)
    
    rows = []
    for _, row in df_clean.iterrows():
        district = str(row.get("Districts/Units", "")).strip()
        exclude_terms = ["Commissionerates", "Central Range", "Eastern Range", "Western Range", "nan", ""]
        if district and district not in exclude_terms:
            rows.append({
                "district": district,
                "ipc_bns_crimes_2025": int(row.get("IPC/BNS Crimes", 0) or 0),
                "sll_crimes_2025": int(row.get("SLL Crimes", 0) or 0)
            })
    
    result = pd.DataFrame(rows)
    print(f"    Loaded {len(result)} districts from 2025")
    return result

def add_coordinates(df):
    """Add lat/lon and population density to districts"""
    coords = []
    for _, row in df.iterrows():
        district = row["district"]
        if district in BENGALURU_DISTRICT_COORDS:
            info = BENGALURU_DISTRICT_COORDS[district]
            coords.append({
                "latitude": info["lat"],
                "longitude": info["lon"],
                "population_density": info["population_density"]
            })
        else:
            coords.append({
                "latitude": 12.9716 + np.random.uniform(-0.1, 0.1),
                "longitude": 77.5946 + np.random.uniform(-0.1, 0.1),
                "population_density": 1500
            })
    
    coords_df = pd.DataFrame(coords)
    return pd.concat([df.reset_index(drop=True), coords_df], axis=1)

def calculate_weighted_crime_score(row):
    """Calculate weighted crime score based on crime types"""
    score = 0
    
    for crime_type, weight in CRIME_WEIGHTS.items():
        score += row.get(crime_type, 0) * weight
    
    return score

def calculate_safety_index(row, max_score):
    """Calculate safety index (0-1) - higher is safer"""
    if max_score == 0:
        return 0.5
    
    raw_score = row.get("weighted_crime_score", 0)
    normalized = raw_score / max_score
    
    pop_factor = 1 + np.log10(row.get("population_density", 1000) / 1000)
    adjusted = normalized * pop_factor
    
    safety_index = 1.0 - min(1.0, adjusted)
    return round(safety_index, 4)

def add_time_features(df):
    """Add synthetic time-based features for training"""
    np.random.seed(42)
    
    df["hour_of_day"] = np.random.choice(range(24), size=len(df))
    df["is_night"] = ((df["hour_of_day"] >= 22) | (df["hour_of_day"] <= 5)).astype(int)
    df["is_weekend"] = np.random.choice([0, 1], size=len(df), p=[0.7, 0.3])
    
    return df

def main():
    print("Loading Karnataka Crime Data 2024...")
    df_2024 = load_crime_2024()
    print(f"  Loaded {len(df_2024)} districts from 2024 data")
    
    print("Loading Karnataka Crime Data 2025...")
    df_2025 = load_crime_2025()
    print(f"  Loaded {len(df_2025)} districts from 2025 data")
    
    print("\nMerging datasets...")
    df = pd.merge(df_2024, df_2025, on="district", how="outer")
    
    print("Adding coordinates...")
    df = add_coordinates(df)
    
    print("Calculating weighted crime scores...")
    df["weighted_crime_score"] = df.apply(calculate_weighted_crime_score, axis=1)
    
    max_score = df["weighted_crime_score"].max()
    print(f"  Max crime score: {max_score}")
    
    print("Calculating safety index...")
    df["safety_index"] = df.apply(lambda row: calculate_safety_index(row, max_score), axis=1)
    
    print("Generating training samples...")
    
    # Generate multiple samples per district with different conditions
    samples = []
    hours = [6, 10, 14, 18, 22, 2]
    speeds = [20, 40, 60, 80]
    route_devs = [0, 1]
    severities = ["low", "medium", "high"]
    
    np.random.seed(42)
    
    for _, row in df.iterrows():
        for hour in hours:
            for speed in speeds:
                for route_dev in route_devs:
                    for severity in severities:
                        is_night = 1 if hour >= 22 or hour <= 5 else 0
                        is_weekend = np.random.choice([0, 1], p=[0.7, 0.3])
                        
                        # Adjust safety index based on conditions
                        base_safety = row["safety_index"]
                        
                        # Night increases risk
                        if is_night:
                            adjusted_safety = base_safety * 0.85
                        else:
                            adjusted_safety = base_safety
                        
                        # High speed increases risk
                        if speed > 60:
                            adjusted_safety *= 0.90
                        elif speed > 40:
                            adjusted_safety *= 0.95
                        
                        # Route deviation increases risk
                        if route_dev:
                            adjusted_safety *= 0.85
                        
                        # Severity affects risk
                        if severity == "high":
                            adjusted_safety *= 0.80
                        elif severity == "medium":
                            adjusted_safety *= 0.90
                        
                        adjusted_safety = max(0.0, min(1.0, adjusted_safety))
                        
                        samples.append({
                            "district": row["district"],
                            "latitude": row["latitude"],
                            "longitude": row["longitude"],
                            "population_density": row["population_density"],
                            "theft": row.get("theft", 0),
                            "robbery": row.get("robbery", 0),
                            "molestation": row.get("molestation", 0),
                            "cruelty_by_husband": row.get("cruelty_by_husband", 0),
                            "pocso": row.get("pocso", 0),
                            "rape": row.get("rape", 0),
                            "dacoity": row.get("dacoity", 0),
                            "murder": row.get("murder", 0),
                            "weighted_crime_score": row["weighted_crime_score"],
                            "safety_index": round(adjusted_safety, 4),
                            "hour_of_day": hour,
                            "is_night": is_night,
                            "is_weekend": is_weekend,
                            "speed": speed,
                            "route_deviation": route_dev,
                            "severity": severity,
                        })
    
    final_df = pd.DataFrame(samples)
    
    output_path = OUTPUT_DIR / "bengaluru_safety_training_data.csv"
    final_df.to_csv(output_path, index=False)
    print(f"\nDataset saved to: {output_path}")
    print(f"Total records: {len(final_df)}")
    print(f"\nSafety Index distribution:")
    print(final_df["safety_index"].describe())
    print(f"\nSample records:")
    print(final_df.head(10).to_string())

if __name__ == "__main__":
    main()