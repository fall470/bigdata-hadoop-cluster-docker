#!/usr/bin/env python3
import sys

for transaction in sys.stdin:

    # Supprimer le retour à la ligne puis découper la ligne sur les virgules
    fields = transaction.strip().split(",")

    # Ignorer les lignes qui n'ont pas exactement 9 valeurs
    if len(fields) != 9:
        continue

    # Donner un nom à chaque élément de la liste
    transaction_id, date, country, city, product, category, quantity, unit_price, payment_method = fields

    # Ignorer l'en-tête du fichier
    if transaction_id == "transaction_id":
        continue

    # Les champs sont des chaînes : convertir la quantité en entier pour pouvoir calculer
    quantity = int(quantity)

    # Convertir le prix unitaire en centimes entiers (round évite les erreurs de flottants)
    unit_price_cents = round(float(unit_price) * 100)

    # Émettre la paire clé<TAB>valeur : pays et montant de la vente en centimes
    print(f"{country}\t{quantity * unit_price_cents}")