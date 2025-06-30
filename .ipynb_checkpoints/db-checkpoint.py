{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "f910a918-9ca8-404b-b9b6-7231ce98b200",
   "metadata": {},
   "outputs": [],
   "source": [
    "# db.py\n",
    "import sqlite3\n",
    "from datetime import datetime\n",
    "\n",
    "def init_db():\n",
    "    conn = sqlite3.connect(\"claims.db\")\n",
    "    c = conn.cursor()\n",
    "    c.execute(\"\"\"\n",
    "    CREATE TABLE IF NOT EXISTS decisions (\n",
    "        claim_id TEXT,\n",
    "        decision TEXT,\n",
    "        reviewer_role TEXT,\n",
    "        timestamp TEXT\n",
    "    )\n",
    "    \"\"\")\n",
    "    conn.commit()\n",
    "    conn.close()\n",
    "\n",
    "def log_decision(claim_id, decision, role):\n",
    "    conn = sqlite3.connect(\"claims.db\")\n",
    "    c = conn.cursor()\n",
    "    c.execute(\"INSERT INTO decisions (claim_id, decision, reviewer_role, timestamp) VALUES (?, ?, ?, ?)\",\n",
    "              (claim_id, decision, role, datetime.now().isoformat()))\n",
    "    conn.commit()\n",
    "    conn.close()"
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
