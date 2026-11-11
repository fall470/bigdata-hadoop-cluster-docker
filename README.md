# Hadoop distribué & MapReduce

Cluster Hadoop 3.4.1 sur Docker Compose : 1 NameNode, 3 DataNodes, 1 ResourceManager, 3 NodeManagers, réplication HDFS = 2, taille de bloc = 1 Mio. Quatre traitements MapReduce en Python (Hadoop Streaming) sur `transactions.csv` (100 000 transactions synthétiques).

## Prérequis

- Docker Desktop (Docker Compose v2)
- PowerShell (les commandes ci-dessous ont été testées sous Windows)
- Environ 8 Go de RAM disponibles
- Accès Internet au premier `docker build` (image de base et dépôts CentOS 7 archivés)

## Structure du projet

```
.
├── Dockerfile                  # image commune (Hadoop 3.4.1 + Python 3)
├── compose.yaml                # 8 conteneurs, volumes nommés
├── conf/
│   ├── core-site.xml
│   ├── hdfs-site.xml
│   ├── mapred-site.xml
│   └── yarn-site.xml
├── data/
│   └── transactions.csv        # monté sur /data dans le NameNode
├── mapreduce/                  # monté sur /mapreduce dans le NameNode
│   ├── chiffre_affaires_par_pays_mapper.py / _reducer.py
│   ├── chiffre_affaires_par_categorie_mapper.py / _reducer.py
│   ├── chiffre_affaires_par_paiement_mapper.py / _reducer.py
│   ├── chiffre_affaires_par_mois_mapper.py / _reducer.py
│   └── validate.py             # validation indépendante
├── results/                    # sorties des 4 jobs (part-00000)
├── Rapport_Hadoop_distribué _et_MapReduce.pdf
└── README.md
```

## 1. Construire l'image et démarrer le cluster

Depuis le dossier du projet :

```powershell
docker build -t hadoop-python:3.4.1 .
docker compose up -d
docker compose ps
```

Le `build` est nécessaire une première fois, puis après toute modification du `Dockerfile` ou des fichiers de `conf/` (copiés dans l'image). Les 8 conteneurs doivent être `Up`.

## 2. Vérifier le cluster

Attendre environ 30 secondes après le démarrage, puis :

```powershell
docker exec hadoop-namenode hdfs dfsadmin -report
docker exec hadoop-resourcemanager yarn node -list
```

Attendu : `Live datanodes (3)` et `Total Nodes:3` (tous `RUNNING`).

Interfaces web :

- NameNode : http://localhost:9870 (onglet Datanodes)
- ResourceManager : http://localhost:8088 (menu Nodes)

## 3. Importer les données dans HDFS

```powershell
docker exec hadoop-namenode hdfs dfs -mkdir -p /assignment/transactions
docker exec hadoop-namenode hdfs dfs -put /data/transactions.csv /assignment/transactions/
docker exec hadoop-namenode hdfs dfs -ls -h /assignment/transactions
docker exec hadoop-namenode hdfs fsck /assignment/transactions/transactions.csv -files -blocks -locations
```

Attendu : 7 blocs, `Live_repl=2` pour chaque bloc, `HEALTHY`. La taille de bloc est appliquée à l'écriture : importer le fichier après le démarrage du cluster configuré.

## 4. Lancer les quatre traitements MapReduce

Chaque job suit la même commande Hadoop Streaming. Supprimer d'abord la sortie existante (Hadoop refuse d'écrire dans un dossier existant).

### Test local (sans Hadoop)

```powershell
docker exec hadoop-namenode bash -c "cat /data/transactions.csv | python3 /mapreduce/chiffre_affaires_par_pays_mapper.py | sort | python3 /mapreduce/chiffre_affaires_par_pays_reducer.py"
```

`sort` simule le tri par clé que Hadoop effectue entre le map et le reduce.

### Job 1 : chiffre d'affaires par pays

```powershell
docker exec hadoop-namenode hdfs dfs -rm -r -f /assignment/output/chiffre_affaires_par_pays
docker exec hadoop-namenode hadoop jar /opt/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.4.1.jar -files /mapreduce/chiffre_affaires_par_pays_mapper.py,/mapreduce/chiffre_affaires_par_pays_reducer.py -mapper "python3 chiffre_affaires_par_pays_mapper.py" -reducer "python3 chiffre_affaires_par_pays_reducer.py" -input /assignment/transactions/transactions.csv -output /assignment/output/chiffre_affaires_par_pays
docker exec hadoop-namenode hdfs dfs -cat /assignment/output/chiffre_affaires_par_pays/part-00000
```

### Jobs 2, 3 et 4

Même commande en remplaçant `pays` par `categorie`, `paiement` ou `mois` dans les noms de fichiers et le dossier de sortie :

| Job | Fichiers | Sortie HDFS |
|---|---|---|
| 1 | `chiffre_affaires_par_pays_*.py` | `/assignment/output/chiffre_affaires_par_pays` |
| 2 | `chiffre_affaires_par_categorie_*.py` | `/assignment/output/chiffre_affaires_par_categorie` |
| 3 | `chiffre_affaires_par_paiement_*.py` | `/assignment/output/chiffre_affaires_par_paiement` |
| 4 | `chiffre_affaires_par_mois_*.py` | `/assignment/output/chiffre_affaires_par_mois` |

### Choix de conception

- **En-tête** : le mapper ignore la ligne dont le premier champ vaut `transaction_id`, ainsi que toute ligne qui n'a pas exactement 9 champs.
- **Montants** : `quantity × unit_price` calculé en centimes entiers (`round(float(unit_price) * 100)`), sans somme de flottants.
- **Tri des clés** : Hadoop trie les paires par clé entre le map et le reduce, donc le reducer cumule tant que la clé ne change pas.
- **Mois** : extrait des 7 premiers caractères de `date` (format `AAAA-MM-JJ`).

## 5. Validation indépendante

`validate.py` relit le CSV avec le module `csv` et recalcule les totaux avec un dictionnaire, sans MapReduce :

```powershell
docker exec hadoop-namenode python3 /mapreduce/validate.py pays
docker exec hadoop-namenode python3 /mapreduce/validate.py categorie
docker exec hadoop-namenode python3 /mapreduce/validate.py paiement
docker exec hadoop-namenode python3 /mapreduce/validate.py mois
```

Comparer chaque sortie avec le `-cat` HDFS correspondant. 

## 6. Test de panne (Partie D)

Le délai de détection d'un DataNode est réglé à 40 s (2 × 5 s + 10 × 3 s) dans `hdfs-site.xml`.

### Panne d'un DataNode

```powershell
docker stop hadoop-datanode1
# attendre environ 60 s
docker exec hadoop-namenode hdfs dfsadmin -report | Select-String "Live datanodes|Dead datanodes|Name:|Hostname:"
docker exec hadoop-namenode hdfs fsck /assignment/transactions/transactions.csv -files -blocks -locations
docker exec hadoop-namenode hdfs dfs -cat /assignment/transactions/transactions.csv | Select-Object -First 3
docker exec hadoop-resourcemanager yarn node -list
docker start hadoop-datanode1
```

### Panne d'un NodeManager

```powershell
docker stop hadoop-nodemanager1
docker exec hadoop-resourcemanager yarn node -list -all
# relancer un job (voir section 4) : il doit aboutir avec 2 NodeManagers
docker start hadoop-nodemanager1
```

## 7. Arrêt et remise à zéro

```powershell
docker compose down        # arrête le cluster, conserve les volumes (données HDFS)
docker compose down -v     # arrête et supprime les volumes (HDFS remis à zéro)
```

Après un `down -v`, refaire les sections 1 et 3.



## Choix techniques

- **Image** : `apache/hadoop:3.4.1` (version imposée), avec dépôts CentOS 7 redirigés vers `vault.centos.org` (CentOS 7 est en fin de vie) pour installer Python 3.
- **Utilisateur** : `root`, pour éviter les problèmes de permissions sur les volumes nommés (compromis pédagogique).
- **Configuration** : les 4 XML sont copiés dans l'image, donc identiques sur tous les nœuds.
- **Stockage** : un volume nommé par nœud HDFS (`namenode_data`, `datanode1_data` à `datanode3_data`) monté sur `/tmp/hadoop-root/dfs/...`.
- **Limite** : les 8 conteneurs partagent le même PC (CPU, RAM, disque) : la tolérance aux pannes est simulée.



## Assistance extérieure

Un outil d'IA (Claude) a été utilisé pour la structuration du rapport et la relecture du code. 
