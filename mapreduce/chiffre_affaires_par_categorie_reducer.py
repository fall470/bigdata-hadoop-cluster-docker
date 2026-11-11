#!/usr/bin/env python3
import sys

current_category = None
current_amount = 0

for line in sys.stdin:

    # Séparer la clé et la valeur sur la tabulation
    category, amount = line.strip().split("\t")

    # Convertir le montant en entier (centimes) pour pouvoir additionner
    amount = int(amount)

    if current_category == category:
        # Même catégorie que la ligne précédente : cumuler
        current_amount = current_amount + amount
    else:
        # Nouvelle catégorie : afficher le total de la catégorie précédente
        if current_category is not None:
            print(f"{current_category}\t{current_amount}")
        # Démarrer le cumul de la nouvelle catégorie
        current_category = category
        current_amount = amount

# Afficher le total de la dernière catégorie
if current_category is not None:
    print(f"{current_category}\t{current_amount}")