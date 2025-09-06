# Add to your FastAPI service
from sklearn.ensemble import IsolationForest
import pandas as pd
import numpy as np

@api.post("/detect-anomalies")
async def detect_data_anomalies(request_data: dict):
    """
    Automatically detects unusual patterns in data
    Perfect for fraud detection, outlier analysis, etc.
    """
    try:
        # Get the SQL result data
        sql_data = request_data.get('sql_result', [])
        
        if not sql_data or len(sql_data) < 10:
            return {"message": "Need at least 10 rows for anomaly detection"}
        
        # Convert to DataFrame
        df = pd.DataFrame(sql_data)
        
        # Auto-detect numeric columns for analysis
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) == 0:
            return {"message": "No numeric columns found for analysis"}
        
        # Use Isolation Forest for anomaly detection
        isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        anomaly_labels = isolation_forest.fit_predict(df[numeric_cols])
        
        # Find anomalous rows
        anomalies = df[anomaly_labels == -1]
        
        # Generate insights
        insights = []
        for col in numeric_cols:
            col_anomalies = anomalies[col]
            if len(col_anomalies) > 0:
                insights.append({
                    "column": col,
                    "anomaly_count": len(col_anomalies),
                    "normal_mean": float(df[col].mean()),
                    "anomaly_values": col_anomalies.tolist(),
                    "severity": "HIGH" if len(col_anomalies) > len(df) * 0.05 else "MEDIUM"
                })
        
        # AI-generated explanation
        explanation = generate_anomaly_explanation(insights, df)
        
        return {
            "anomalies_detected": len(anomalies),
            "total_rows": len(df),
            "anomaly_percentage": round((len(anomalies) / len(df)) * 100, 2),
            "insights": insights,
            "explanation": explanation,
            "anomalous_rows": anomalies.to_dict('records'),
            "recommendations": generate_anomaly_recommendations(insights)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Anomaly detection failed: {str(e)}")

def generate_anomaly_explanation(insights, df):
    """Generate human-readable explanation of anomalies"""
    if not insights:
        return "No significant anomalies detected in the data."
    
    explanation = f"🚨 Detected unusual patterns in {len(insights)} columns. "
    
    high_severity = [i for i in insights if i['severity'] == 'HIGH']
    if high_severity:
        explanation += f"High-priority anomalies found in: {', '.join([i['column'] for i in high_severity])}. "
    
    explanation += "This could indicate data quality issues, unusual business events, or potential fraud."
    
    return explanation

def generate_anomaly_recommendations(insights):
    """Generate actionable recommendations"""
    recommendations = []
    
    for insight in insights:
        if insight['severity'] == 'HIGH':
            recommendations.append(f"Investigate {insight['column']} - {insight['anomaly_count']} outliers detected")
        else:
            recommendations.append(f"Monitor {insight['column']} for trends")
    
    recommendations.append("Consider setting up automated alerts for future anomalies")
    recommendations.append("Review data collection processes for these columns")
    
    return recommendations
