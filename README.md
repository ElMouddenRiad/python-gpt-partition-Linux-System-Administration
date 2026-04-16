# Linux System Administration Portfolio

Ce dépôt regroupe des scripts Python réalisés dans le cadre d'un module d'Administration Système Linux et de répartition.

L'objectif de cette version est de présenter un projet propre, lisible et partageable sur GitHub, avec un niveau de documentation utile pour une candidature ou un portfolio technique.

## Objectifs du dépôt

- montrer des compétences concrètes en administration Linux
- conserver une structure simple et compréhensible
- supprimer les doublons et les brouillons
- documenter clairement le rôle de chaque script
- faciliter une future réutilisation dans un CV ou un entretien

## Contenu conservé

### 1. Analyse de partitions disque
- [parted.py](parted.py) : lecture d'un MBR et, si besoin, de partitions GPT
- [uuid_types.py](uuid_types.py) : mapping des GUID GPT vers des noms lisibles

Compétences montrées :
- lecture binaire de structures disque
- `struct.unpack`
- manipulation d'`Enum` et de `dataclass`
- décodage de GUID GPT

### 2. Gestion d'utilisateurs Linux
- [useradd.py](useradd.py) : aide à la création d'un compte utilisateur Linux

Compétences montrées :
- vérification d'arguments
- interaction avec `pwd`, `grp` et `subprocess`
- automatisation d'actions d'administration système

### 3. Création de disques virtuels
- [vd_create.py](vd_create.py) : création d'images disque et rattachement à des périphériques loop

Compétences montrées :
- validation d'entrées
- calcul d'espace disque
- automatisation de `losetup`
- gestion de fichiers image

### 4. Journalisation distante
- [rsyslog.py](rsyslog.py) : envoi de logs vers un serveur syslog

Compétences montrées :
- configuration de `logging`
- `SysLogHandler`
- externalisation de la cible réseau via des arguments

## Comment lancer les scripts

Les scripts sont pensés pour Linux.

Par défaut, les scripts sensibles fonctionnent en mode aperçu. L'exécution réelle demande l'option `--apply` et, selon le cas, des privilèges administrateur.

### Analyse de disque
```bash
python parted.py /chemin/vers/disque.img
```

### Création d'utilisateur
```bash
python useradd.py login motdepasse --apply
```
Sans `--apply`, le script affiche seulement les actions prévues.

### Création de disques virtuels
```bash
python vd_create.py 2 10G --apply
```
Sans `--apply`, le script fonctionne en mode aperçu.

### Syslog
```bash
python rsyslog.py --host 127.0.0.1 --port 514 --message "Test" --level error
```

## Axes d'amélioration identifiés

- ajouter une suite de tests
- séparer le code métier et l'interface CLI
- mieux gérer les erreurs système et les droits root
- rendre les scripts plus portables et plus modulaires
- ajouter un `requirements.txt` si des dépendances externes apparaissent plus tard

## Lecture rapide du projet

Ce dépôt met surtout en valeur :

- la lecture de structures bas niveau
- l'automatisation de tâches Linux
- l'usage de `subprocess`, `pwd`, `grp`, `logging` et `struct`
- la capacité à nettoyer un code source pour le rendre présentable publiquement

## Fichiers supprimés volontairement

Les anciennes variantes `PROF`, `MOI`, `partiel_*` et le répertoire de cache Python sont considérés comme des brouillons ou des doublons et ont été retirés pour garder un dépôt propre.

## Remarque

Certains scripts d'administration système nécessitent des privilèges élevés. Ils doivent être utilisés avec prudence, idéalement sur une machine de test ou une VM.
