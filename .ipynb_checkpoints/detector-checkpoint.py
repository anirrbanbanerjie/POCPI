{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "bfff4c07-95a1-4197-bd90-15289224dbd2",
   "metadata": {},
   "outputs": [],
   "source": [
    "# detector.py\n",
    "import pandas as pd\n",
    "import numpy as np\n",
    "from sklearn.ensemble import IsolationForest\n",
    "\n",
    "def detect_anomalies(df):\n",
    "    df = df.copy()\n",
    "    df['claim_month'] = pd.to_datetime(df['claim_date']).dt.to_period('M')\n",
    "\n",
    "    # Cost stats\n",
    "    stats = df.groupby('procedure')['cost'].agg(['mean','std']).reset_index()\n",
    "    df = df.merge(stats, on='procedure', how='left')\n",
    "    df['cost_outlier'] = ~df['cost'].between(df['mean'] - 3*df['std'], df['mean'] + 3*df['std'])\n",
    "\n",
    "    # Frequency anomaly\n",
    "    freq = df.groupby(['pet_id','claim_month']).size().reset_index(name='cnt')\n",
    "    freq_set = set(zip(freq['pet_id'], freq['claim_month'][freq['cnt']>5]))\n",
    "    df['freq_anomaly'] = df.apply(lambda r: (r['pet_id'], r['claim_month']) in freq_set, axis=1)\n",
    "\n",
    "    # Rule-based flags\n",
    "    def flag_reasons(r):\n",
    "        rs = []\n",
    "        if r['cost_outlier']: rs.append('Cost outlier')\n",
    "        if r['freq_anomaly']: rs.append('High frequency')\n",
    "        return \"; \".join(rs) if rs else None\n",
    "    df['flag_reason'] = df.apply(flag_reasons, axis=1)\n",
    "\n",
    "    # ML flags\n",
    "    df['proc_enc'] = pd.factorize(df['procedure'])[0]\n",
    "    feat = df[['cost','proc_enc']]\n",
    "    model = IsolationForest(contamination=0.05, random_state=42)\n",
    "    df['ml_flag'] = model.fit_predict(feat) == -1\n",
    "\n",
    "    # Final status\n",
    "    df['status'] = np.where(df['flag_reason'].notnull() | df['ml_flag'], 'flagged_for_review', 'approved')\n",
    "    return df\n"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.12.4"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
