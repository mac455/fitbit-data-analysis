# backend/seed.py
import pandas as pd
from database import supabase


def seed_database_multi_client():
    print("Starting Dynamic Multi-Client Seeding Pipeline...")
    
    clients_response = supabase.table("clients").select("id, first_name, last_name").execute()
    db_clients = clients_response.data
    
    # Add a defensive check right here to stop the script if the database is empty
    if not db_clients:
        print(" Error: The 'clients' table is completely empty! Run the SQL insert first.")
        return

    # 3. Load the multi-person tracking data
    try:
        raw_data = pd.read_csv("../data/master_hourly.csv")
        print("Multi-user hourly dataset loaded successfully.")
    except FileNotFoundError:
        print(" Error: Could not find 'master_hourly.csv'. Check your path.")
        return

    # Extract the unique person IDs found natively inside the CSV
    unique_csv_ids = raw_data['Id'].unique()
    print(f"Found {len(unique_csv_ids)} distinct user profiles inside the source CSV.")

    # 4. CREATE THE TRANSLATION MAP
    # We map each unique integer ID from the CSV to a unique UUID from our database
    id_translation_map = {}
    for index, csv_id in enumerate(unique_csv_ids):
        # Prevent index out of bounds if there are more IDs in the CSV than profiles in our DB
        db_client_index = index % len(db_clients)
        assigned_db_client = db_clients[db_client_index]
        
        id_translation_map[csv_id] = assigned_db_client["id"]
        print(f" Mapping CSV User {csv_id}  DB Client {assigned_db_client['first_name']} ({assigned_db_client['id'][:8]}...)")

    # 5. AGGREGATE HOURLY ROWS INTO DAILY TOTALS (Grouping by BOTH Id and Date)
    print("\n Executing daily aggregations across all user segments...")
    daily_df = raw_data.groupby(['Id', 'ActivityDate']).agg(
        Total_Calories=('Calories', 'sum'), 
        Total_Intensity=('TotalIntensity', 'sum'),
        Max_Intensity=('TotalIntensity', 'max'),
        Avg_Intensity=('AverageIntensity', 'mean')
    ).reset_index()

    # Calculate the synthetic feature ratio
    daily_df['Calorie_Intensity_Ratio'] = daily_df['Total_Calories'] / (daily_df['Total_Intensity'] + 1)

    # 6. COMPILE THE BULK PAYLOAD
    telemetry_batch = []
    for _, row in daily_df.iterrows():
        csv_user_id = row["Id"]
        
        # Translate the integer ID to our secure relational UUID
        target_uuid = id_translation_map[csv_user_id]
        
        telemetry_batch.append({
            "client_id": target_uuid,
            "activity_date": str(row["ActivityDate"]),
            "total_calories": float(row["Total_Calories"]),
            "max_intensity": float(row["Max_Intensity"]),
            "calorie_intensity_ratio": float(row["Calorie_Intensity_Ratio"])
        })

    # 7. BULK INSERT HETEROGENEOUS DATA
    print(f"\n Uploading {len(telemetry_batch)} distinct historical rows to Supabase...")
    try:
        supabase.table("client_telemetry").insert(telemetry_batch).execute()
        print(" Success! The database is populated with distinct user histories.")
    except Exception as e:
        print(f" Database bulk insert failed: {str(e)}")

if __name__ == "__main__":
    seed_database_multi_client()