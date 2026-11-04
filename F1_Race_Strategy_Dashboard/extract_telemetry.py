import os
import zipfile
import pandas as pd
import numpy as np

def extract_fastest_laps_telemetry():
    zip_path = r'G:\DAV\F1.zip'
    out_dir = r'G:\DAV\F1_Race_Strategy_Dashboard\cache\telemetry'
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, 'fastest_laps_telemetry.parquet')

    print("Opening F1.zip...")
    with zipfile.ZipFile(zip_path) as z:
        with z.open('Fastest_Laps.csv') as f:
            fl_df = pd.read_csv(f)
        
        fl_windows = {}
        for _, row in fl_df.iterrows():
            key = (int(row['RoundNumber']), int(row['DriverNumber']))
            fl_windows[key] = {
                'start': str(row['LapStartTime']),
                'end': str(row['Time']),
                'event': row['EventName'],
                'driver': row['Driver'],
                'lap_num': row['LapNumber'],
                'lap_time': row['LapTime']
            }
        print(f"Tracking {len(fl_windows)} fastest lap windows...")

        matched_records = []
        with z.open('Telemetry.csv') as f:
            chunk_iter = pd.read_csv(f, chunksize=1000000)
            for i, chunk in enumerate(chunk_iter):
                chunk_rounds = chunk['RoundNumber'].unique()
                for r in chunk_rounds:
                    for (rnd, dnum), meta in fl_windows.items():
                        if rnd == r:
                            sub = chunk[(chunk['RoundNumber'] == rnd) & (chunk['DriverNumber'] == dnum)]
                            if not sub.empty:
                                sub_lap = sub[(sub['Time'] >= meta['start']) & (sub['Time'] <= meta['end'])].copy()
                                if not sub_lap.empty:
                                    sub_lap['DriverCode'] = meta['driver']
                                    sub_lap['LapNumber'] = meta['lap_num']
                                    sub_lap['LapTimeString'] = meta['lap_time']
                                    matched_records.append(sub_lap)

        if matched_records:
            all_fl_telem = pd.concat(matched_records, ignore_index=True)
            
            # calculate distance per lap
            processed_groups = []
            for (rnd, dnum), grp in all_fl_telem.groupby(['RoundNumber', 'DriverNumber']):
                grp = grp.copy().sort_values('Time')
                t_sec = pd.to_timedelta(grp['Time']).dt.total_seconds()
                grp['TimeSec'] = t_sec - t_sec.min()
                dt = grp['TimeSec'].diff().fillna(0).clip(lower=0, upper=2.0)
                grp['Distance'] = (grp['Speed'] / 3.6 * dt).cumsum()
                processed_groups.append(grp)
                
            final_df = pd.concat(processed_groups, ignore_index=True)
            final_df.to_parquet(out_file, index=False)
            print(f"SUCCESS! Saved {len(final_df):,} rows across {final_df['RoundNumber'].nunique()} rounds to {out_file}")

if __name__ == '__main__':
    extract_fastest_laps_telemetry()
