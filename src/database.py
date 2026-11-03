"""
FireCast AI — Local SQLite Prediction History Persistence
"""

import os
import sqlite3
import datetime
import pandas as pd
from typing import Dict, Any, List, Optional
from src.utils import logger, load_config

DEFAULT_DB_PATH = "dataset/processed/firecast_history.db"


def get_db_path() -> str:
    """Retrieve database filepath from central configuration."""
    config = load_config()
    db_path = config.get("database", {}).get("db_path", DEFAULT_DB_PATH)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return db_path


def get_connection() -> sqlite3.Connection:
    """Create a database connection with row factory."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes the SQLite schema for prediction history tracking."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            X INTEGER NOT NULL DEFAULT 7,
            Y INTEGER NOT NULL DEFAULT 5,
            month TEXT NOT NULL,
            day TEXT NOT NULL,
            temp REAL NOT NULL,
            RH REAL NOT NULL,
            wind REAL NOT NULL,
            rain REAL NOT NULL,
            FFMC REAL NOT NULL,
            DMC REAL NOT NULL,
            DC REAL NOT NULL,
            ISI REAL NOT NULL,
            predicted_ha REAL NOT NULL,
            severity_category TEXT NOT NULL,
            model_used TEXT NOT NULL,
            latency_ms REAL NOT NULL,
            notes TEXT
        )
    """)
    # Check if X and Y columns exist for backwards compatibility
    cursor.execute("PRAGMA table_info(predictions)")
    cols = [row[1] for row in cursor.fetchall()]
    if "X" not in cols:
        cursor.execute("ALTER TABLE predictions ADD COLUMN X INTEGER NOT NULL DEFAULT 7")
    if "Y" not in cols:
        cursor.execute("ALTER TABLE predictions ADD COLUMN Y INTEGER NOT NULL DEFAULT 5")
    conn.commit()
    conn.close()


def save_prediction_record(pred_result: Dict[str, Any], notes: str = "") -> int:
    """Saves a completed prediction result into the SQLite database."""
    init_db()
    inputs = pred_result["input_summary"]
    severity = pred_result["severity"]["name"]
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO predictions (
            timestamp, X, Y, month, day, temp, RH, wind, rain,
            FFMC, DMC, DC, ISI, predicted_ha, severity_category,
            model_used, latency_ms, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        now_str,
        int(inputs.get("X", 7)),
        int(inputs.get("Y", 5)),
        inputs["month"],
        inputs["day"],
        float(inputs["temp"]),
        float(inputs["RH"]),
        float(inputs["wind"]),
        float(inputs["rain"]),
        float(inputs["FFMC"]),
        float(inputs["DMC"]),
        float(inputs["DC"]),
        float(inputs["ISI"]),
        float(pred_result["burned_area_ha"]),
        severity,
        pred_result["model_used"],
        float(pred_result["inference_time_ms"]),
        notes
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    logger.info(f"Saved prediction #{new_id} ({pred_result['burned_area_ha']} ha, {severity}) to history.")
    return new_id


def seed_benchmark_history(force: bool = False) -> int:
    """
    Seeds representative Montesinho benchmark cases directly from forestfires.csv
    into the SQLite history database so history is populated and interactive upon launch.
    """
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM predictions")
    count = cursor.fetchone()[0]
    if count > 0 and not force:
        conn.close()
        return 0

    from src.predict import predict_burned_area

    # Curated historical benchmarks directly from forestfires.csv representing diverse conditions
    benchmarks = [
        {"X": 7, "Y": 5, "month": "mar", "day": "fri", "FFMC": 86.2, "DMC": 26.2, "DC": 94.3, "ISI": 5.1, "temp": 8.2, "RH": 51, "wind": 6.7, "rain": 0.0, "notes": "Spring Prescribed Burn (Low Severity)"},
        {"X": 8, "Y": 6, "month": "aug", "day": "sat", "FFMC": 92.2, "DMC": 81.8, "DC": 480.8, "ISI": 11.9, "temp": 20.1, "RH": 34, "wind": 4.5, "rain": 0.0, "notes": "Late Summer Active Ignition (Moderate)"},
        {"X": 4, "Y": 6, "month": "sep", "day": "sun", "FFMC": 93.5, "DMC": 149.3, "DC": 728.6, "ISI": 8.1, "temp": 28.3, "RH": 26, "wind": 3.1, "rain": 0.0, "notes": "Peak Seasonal Drought Anomaly (High)"},
        {"X": 6, "Y": 5, "month": "aug", "day": "tue", "FFMC": 94.8, "DMC": 108.3, "DC": 647.1, "ISI": 16.6, "temp": 30.3, "RH": 27, "wind": 4.9, "rain": 0.0, "notes": "Gale-Force Summer Outbreak (High)"},
        {"X": 7, "Y": 4, "month": "jul", "day": "wed", "FFMC": 91.7, "DMC": 113.8, "DC": 476.1, "ISI": 6.3, "temp": 19.6, "RH": 44, "wind": 4.0, "rain": 0.0, "notes": "Mid-Summer Controlled Response (Low)"},
        {"X": 2, "Y": 2, "month": "aug", "day": "sun", "FFMC": 92.4, "DMC": 124.1, "DC": 680.7, "ISI": 8.5, "temp": 24.9, "RH": 38, "wind": 2.2, "rain": 0.0, "notes": "Valley Inversion Weather Regime (Moderate)"}
    ]

    base_time = datetime.datetime.now() - datetime.timedelta(hours=6)
    seeded_count = 0
    for i, b in enumerate(benchmarks):
        notes = b.pop("notes")
        res = predict_burned_area(b, include_shap=False)
        sim_time = (base_time + datetime.timedelta(hours=i)).strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO predictions (
                timestamp, X, Y, month, day, temp, RH, wind, rain,
                FFMC, DMC, DC, ISI, predicted_ha, severity_category,
                model_used, latency_ms, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sim_time,
            int(b["X"]), int(b["Y"]), b["month"], b["day"],
            float(b["temp"]), float(b["RH"]), float(b["wind"]), float(b["rain"]),
            float(b["FFMC"]), float(b["DMC"]), float(b["DC"]), float(b["ISI"]),
            float(res["burned_area_ha"]), res["severity"]["name"],
            res["model_used"], float(res["inference_time_ms"]), notes
        ))
        seeded_count += 1

    conn.commit()
    conn.close()
    logger.info(f"Seeded {seeded_count} benchmark predictions into history.")
    return seeded_count


def get_prediction_history(limit: int = 200, severity_filter: Optional[str] = None) -> pd.DataFrame:
    """Retrieve historical prediction records as a pandas DataFrame."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM predictions")
    count = cursor.fetchone()[0]
    conn.close()
    
    if count == 0:
        seed_benchmark_history()

    conn = get_connection()
    query = "SELECT * FROM predictions"
    params = []
    
    if severity_filter and severity_filter != "All":
        query += " WHERE severity_category LIKE ?"
        params.append(f"%{severity_filter}%")
        
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def delete_prediction_record(record_id: int) -> bool:
    """Delete a single prediction record by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM predictions WHERE id = ?", (record_id,))
    rows = cursor.rowcount
    conn.commit()
    conn.close()
    return rows > 0


def clear_all_history() -> int:
    """Clears all records from the prediction history table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM predictions")
    rows = cursor.rowcount
    conn.commit()
    conn.close()
    logger.info("Cleared all prediction history.")
    return rows

