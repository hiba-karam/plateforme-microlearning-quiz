# Plateforme de Micro-learning pour Quiz Techniques

## À propos
Ce projet est une solution de micro-learning développée pour optimiser l'auto-évaluation des étudiants en ingénierie. La plateforme propose un parcours pédagogique personnalisé basé sur une logique adaptative et intègre une dimension de gamification (système de badges et classement) pour stimuler l'engagement. L'ensemble est soutenu par une architecture garantissant l'intégrité des évaluations grâce à une sécurisation rigoureuse des sessions côté serveur.

## Fonctionnalités
* **Algorithme Adaptatif :** Ajustement dynamique de la difficulté des questions en temps réel via un moteur basé sur un arbre de décision conditionnel.
* **Sécurité Anti-Triche Backend :** Chronomètre sécurisé côté serveur utilisant des Timestamp UNIX intégrés dans les sessions Django, empêchant toute manipulation via la console du navigateur ou des scripts côté client.
* **Gamification :** Système de récompenses automatiques incluant l'attribution de badges d'expertise et un classement global pour stimuler l'engagement.
* **Gestion des Rôles :** Authentification sécurisée différenciant les accès entre étudiants, professeurs et administrateurs.
* **Design Responsive :** Interface utilisateur épurée et adaptative.

## Technologies & Architecture
* **Backend :** Python, Django.
* **Frontend :** HTML5, CSS3, Bootstrap 5.
* **Base de données :** MariaDB.
* **Architecture :** Architecture robuste de type 3-Tiers, logique métier centralisée sur le serveur (Django ORM).
* **Conception & Modélisation :** Modélisation UML (Diagrammes de cas d'utilisation, de classes, de séquence, d'activité, d'état-transition et de déploiement) et conception de base de données (MCD, MLD, MPD).

## Auteurs
Projet réalisé par Hiba Karam en collaboration avec Abdelouahab Belmoudden et Othmane Kardady - Élèves Ingénieurs @ EMSI.
