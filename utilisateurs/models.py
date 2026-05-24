from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class Utilisateur(AbstractUser):
    ROLE_CHOICES = (
        ('etudiant', 'Étudiant'),
        ('professeur', 'Professeur'),
        ('administrateur', 'Administrateur'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='etudiant')
    score_global = models.IntegerField(default=0)
    def __str__(self):
        return self.username
    badges = models.ManyToManyField('Badge', through='ObtentionBadge', related_name='etudiants', blank=True)

class Quiz(models.Model):
    titre = models.CharField(max_length=255)
    temps_imparti = models.IntegerField(help_text="Durée en minutes")
    tentatives_max = models.IntegerField()
    class Meta:
        db_table = 'quiz'
    def __str__(self):
        return self.titre
    
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    texte = models.CharField(max_length=500)
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    NIVEAUX = (('Facile', 'Facile'), ('Moyenne', 'Moyenne'), ('Difficile', 'Difficile'))
    difficulte = models.CharField(max_length=15, choices=NIVEAUX, default='Facile')
    REPONSES = (('A', 'Option A'), ('B', 'Option B'), ('C', 'Option C'))
    reponse_correcte = models.CharField(max_length=1, choices=REPONSES)
    class Meta:
        db_table = 'question'
    def __str__(self):
        return f"{self.quiz.titre} - {self.texte}"    

class Tentative(models.Model):
    etudiant = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='tentatives')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='tentatives')
    score_obtenu = models.IntegerField(default=0)
    temps_ecoule = models.IntegerField(default=0) 
    date_passage = models.DateTimeField(auto_now_add=True) 
    class Meta:
        db_table = 'tentative'
    def __str__(self):
        return f"{self.etudiant.email} - {self.quiz.titre} ({self.score_obtenu} pts)"
    
class Badge(models.Model):
    nom = models.CharField(max_length=255)
    icone = models.CharField(max_length=255, default="bi-star-fill text-primary") 
    critere_obtention = models.TextField()
    def __str__(self):
        return self.nom

class ObtentionBadge(models.Model):
    etudiant = models.ForeignKey('Utilisateur', on_delete=models.CASCADE) 
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    date_obtention = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('etudiant', 'badge')