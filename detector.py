# detector.py
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

def detect_anomalies(df):
    df = df.copy()
    df['claim_month'] = pd.to_datetime(df['claim_date']).dt.to_period('M')

    # Cost stats
    stats = df.groupby('procedure')['cost'].agg(['mean','std']).reset_index()
    df = df.merge(stats, on='procedure', how='left')
    df['cost_outlier'] = ~df['cost'].between(df['mean'] - 3*df['std'], df['mean'] + 3*df['std'])

    # Frequency anomaly
    freq = df.groupby(['pet_id','claim_month']).size().reset_index(name='cnt')
    freq_set = set(zip(freq['pet_id'], freq['claim_month'][freq['cnt']>5]))
    df['freq_anomaly'] = df.apply(lambda r: (r['pet_id'], r['claim_month']) in freq_set, axis=1)

    # Rule-based flags
    def flag_reasons(r):
        rs = []
        if r['cost_outlier']: rs.append('Cost outlier')
        if r['freq_anomaly']: rs.append('High frequency')
        return "; ".join(rs) if rs else None
    df['flag_reason'] = df.apply(flag_reasons, axis=1)

    # ML flags
    df['proc_enc'] = pd.factorize(df['procedure'])[0]
    feat = df[['cost','proc_enc']]
    model = IsolationForest(contamination=0.05, random_state=42)
    df['ml_flag'] = model.fit_predict(feat) == -1

    # Final status
    df['status'] = np.where(df['flag_reason'].notnull() | df['ml_flag'], 'flagged_for_review', 'approved')
    return df