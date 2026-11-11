#!/usr/bin/env python3
import csv
import sys
from collections import defaultdict

# Clé de regroupement de chaque job
JOBS = {
    "pays": "country",
    "categorie": "category",
    "paiement": "payment_method",
    "mois": "date",   # le mois est extrait de la date (voir plus bas)
}

job = sys.argv[1]
column = JOBS[job]

totals = defaultdict(int)

with open("/data/transactions.csv", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        key = row[column]
        if job == "mois":
            key = key[:7]  # AAAA-MM, à adapter si le format de date est différent
        cents = round(float(row["unit_price"]) * 100)
        totals[key] += int(row["quantity"]) * cents

for key in sorted(totals):
    print(f"{key}\t{totals[key]}")
    