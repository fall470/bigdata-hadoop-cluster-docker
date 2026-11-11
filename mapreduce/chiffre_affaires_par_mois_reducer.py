#!/usr/bin/env python3
import sys

current_month = None
current_amount = 0

for line in sys.stdin:

    # Séparer la clé et la valeur sur la tabulation
    month, amount = line.strip().split("\t")

    # Convertir le montant en entier (centimes) pour pouvoir additionner
    amount = int(amount)

    if current_month == month:
        # Même mois que la ligne précédente : cumuler
        current_amount = current_amount + amount
    else:
        # Nouveau mois : afficher le total du mois précédent
        if current_month is not None:
            print(f"{current_month}\t{current_amount}")
        # Démarrer le cumul du nouveau mois
        current_month = month
        current_amount = amount

# Afficher le total du dernier mois
if current_month is not None:
    print(f"{current_month}\t{current_amount}")
    