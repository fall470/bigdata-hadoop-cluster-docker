#!/usr/bin/env python3
import sys

current_payment = None
current_amount = 0

for line in sys.stdin:

    # Séparer la clé et la valeur sur la tabulation
    payment, amount = line.strip().split("\t")

    # Convertir le montant en entier (centimes) pour pouvoir additionner
    amount = int(amount)

    if current_payment == payment:
        # Même moyen de paiement que la ligne précédente : cumuler
        current_amount = current_amount + amount
    else:
        # Nouveau moyen de paiement : afficher le total du précédent
        if current_payment is not None:
            print(f"{current_payment}\t{current_amount}")
        # Démarrer le cumul du nouveau moyen de paiement
        current_payment = payment
        current_amount = amount

# Afficher le total du dernier moyen de paiement
if current_payment is not None:
    print(f"{current_payment}\t{current_amount}")