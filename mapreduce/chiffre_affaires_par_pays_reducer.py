#!/usr/bin/env python3
import sys

current_country = None
current_amount = 0

for line in sys.stdin:

    # Séparer la clé et la valeur sur la tabulation
    country, amount = line.strip().split("\t")

    # Convertir le montant en entier (centimes) pour pouvoir additionner
    amount = int(amount)

    if current_country == country:
        # Même pays que la ligne précédente : cumuler
        current_amount = current_amount + amount
    else:
        # Nouveau pays : afficher le total du pays précédent
        if current_country is not None:
            print(f"{current_country}\t{current_amount}")
        # Démarrer le cumul du nouveau pays
        current_country = country
        current_amount = amount

# Afficher le total du dernier pays
if current_country is not None:
    print(f"{current_country}\t{current_amount}")