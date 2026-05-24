import random
import re
import unicodedata
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg
from .models import Quiz, Question, Tentative, Badge
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import update_session_auth_hash

User = get_user_model()


def nettoyer(texte):
    if not texte:
        return ""
    texte = str(texte).lower()
    texte = "".join(
        c
        for c in unicodedata.normalize("NFD", texte)
        if unicodedata.category(c) != "Mn"
    )
    return re.sub(r"[^a-z0-9]", "", texte)


@login_required
def dashboard_etudiant(request):
    quizzes = Quiz.objects.all()
    for quiz in quizzes:
        badge_nom = f"Expert {quiz.titre}"
        est_expert = request.user.badges.filter(nom=badge_nom).exists()

        tentatives_faites = Tentative.objects.filter(
            etudiant=request.user, quiz=quiz
        ).count()

        if est_expert:
            quiz.essais_restants = 0
            quiz.est_expert = True
        else:
            quiz.essais_restants = max(0, quiz.tentatives_max - tentatives_faites)
            quiz.est_expert = False

    return render(request, "dashboard_etudiant.html", {"quizzes": quizzes})


@login_required
def passer_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    badge_nom = f"Expert {quiz.titre}"
    if request.user.badges.filter(nom=badge_nom).exists():
        messages.info(
            request,
            f"Vous avez déjà obtenu le badge {badge_nom} ! Vous ne pouvez plus refaire ce quiz.",
        )
        return redirect("dashboard_etudiant")

    nombre_tentatives = Tentative.objects.filter(
        etudiant=request.user, quiz=quiz
    ).count()

    if nombre_tentatives >= quiz.tentatives_max:
        messages.error(
            request,
            f"Accès refusé : Vous avez déjà utilisé vos {quiz.tentatives_max} tentatives.",
        )
        return redirect("dashboard_etudiant")

    quiz_id_str = str(quiz_id)
    session_quiz = str(request.session.get("quiz_en_cours", ""))

    if session_quiz != quiz_id_str:
        now_timestamp = timezone.now().timestamp()
        request.session["quiz_en_cours"] = quiz_id_str
        request.session["difficulte_actuelle"] = "Facile"
        request.session["questions_posees"] = []
        request.session["score_temporaire"] = 0
        request.session["heure_debut"] = now_timestamp
        request.session["fin_quiz_timestamp"] = now_timestamp + (
            quiz.temps_imparti * 60
        )
        request.session.modified = True

    fin_quiz = request.session.get("fin_quiz_timestamp")

    if fin_quiz:
        if timezone.now().timestamp() > (fin_quiz + 3):
            messages.warning(
                request, "Temps écoulé ! Votre quiz a été soumis automatiquement."
            )
            return redirect("terminer_quiz", quiz_id=quiz.id)

    difficulte = request.session.get("difficulte_actuelle", "Facile")
    questions_posees = request.session.get("questions_posees", [])
    questions_disponibles = quiz.questions.filter(difficulte=difficulte).exclude(
        id__in=questions_posees
    )

    if len(questions_posees) >= 3 or not questions_disponibles.exists():
        return redirect("terminer_quiz", quiz_id=quiz.id)

    question_ia = random.choice(list(questions_disponibles))

    return render(
        request,
        "passer_quiz.html",
        {
            "quiz": quiz,
            "question": question_ia,
            "difficulte": difficulte,
            "fin_quiz_timestamp": fin_quiz,
        },
    )


@login_required
def soumettre_quiz(request, quiz_id):
    if request.method == "POST":
        quiz = get_object_or_404(Quiz, id=quiz_id)
        
        fin_quiz = request.session.get("fin_quiz_timestamp")
        if fin_quiz:
            if timezone.now().timestamp() > (fin_quiz + 3):
                messages.warning(
                    request, "Délai dépassé ! Cette réponse n'a pas été comptabilisée."
                )
                return redirect("terminer_quiz", quiz_id=quiz.id)

        question_id = request.POST.get("question_id")
        question = get_object_or_404(Question, id=question_id)
        reponse_utilisateur = request.POST.get(f"question_{question.id}", "")

        texte_complet_choisi = ""
        if reponse_utilisateur == "Option A":
            texte_complet_choisi = question.option_a
        elif reponse_utilisateur == "Option B":
            texte_complet_choisi = question.option_b
        elif reponse_utilisateur == "Option C":
            texte_complet_choisi = question.option_c
        else:
            texte_complet_choisi = reponse_utilisateur

        clean_bouton = nettoyer(reponse_utilisateur)
        clean_lettre = clean_bouton[-1] if clean_bouton else ""
        clean_texte = nettoyer(texte_complet_choisi)
        clean_db = nettoyer(question.reponse_correcte)

        difficulte = request.session.get("difficulte_actuelle", "Facile")
        score = request.session.get("score_temporaire", 0)
        liste_posees = list(request.session.get("questions_posees", []))
        if question.id not in liste_posees:
            liste_posees.append(question.id)
            
        if clean_db in (clean_bouton, clean_texte, clean_lettre):
            score += 1
            if difficulte == "Facile":
                difficulte = "Moyenne"
            elif difficulte == "Moyenne":
                difficulte = "Difficile"
        else:
            if difficulte == "Difficile":
                difficulte = "Moyenne"
            else:
                difficulte = "Facile"
                
        request.session["questions_posees"] = liste_posees
        request.session["difficulte_actuelle"] = difficulte
        request.session["score_temporaire"] = score
        request.session.modified = True
        request.session.save()

        return redirect("passer_quiz", quiz_id=quiz_id)

    return redirect("dashboard_etudiant")


@login_required
def terminer_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    score_final = request.session.get("score_temporaire", 0)
    questions_posees = request.session.get("questions_posees", [])
    total_questions = len(questions_posees)
    heure_debut = request.session.get("heure_debut")
    temps_ecoule_reel = 0

    if heure_debut:
        temps_ecoule_reel = int(timezone.now().timestamp() - heure_debut)
        limite_max = quiz.temps_imparti * 60
        if temps_ecoule_reel > limite_max:
            temps_ecoule_reel = limite_max

    points_gagnes = 0
    if total_questions > 0:
        Tentative.objects.create(
            etudiant=request.user,
            quiz=quiz,
            score_obtenu=score_final,
            temps_ecoule=temps_ecoule_reel,
        )
        points_gagnes = score_final * 10
        request.user.score_global += points_gagnes
        request.user.save()

        if score_final == total_questions and total_questions > 0:
            badge_nom = f"Expert {quiz.titre}"
            badge, created = Badge.objects.get_or_create(
                nom=badge_nom,
                defaults={
                    "critere_obtention": f"Avoir un score parfait au quiz {quiz.titre}",
                    "icone": "bi-trophy-fill text-warning",
                },
            )
            if not request.user.badges.filter(id=badge.id).exists():
                request.user.badges.add(badge)
                messages.success(
                    request,
                    f"🎉 Félicitations ! Score parfait ! Vous avez débloqué le badge : {badge.nom} !",
                )

    request.session.pop("quiz_en_cours", None)
    request.session.pop("difficulte_actuelle", None)
    request.session.pop("questions_posees", None)
    request.session.pop("score_temporaire", None)
    request.session.pop("heure_debut", None)
    request.session.pop("fin_quiz_timestamp", None)

    return render(
        request,
        "resultat.html",
        {
            "quiz": quiz,
            "score": score_final,
            "total": total_questions,
            "points": points_gagnes,
        },
    )


@login_required
def classement(request):
    etudiants = User.objects.filter(
        is_superuser=False, is_staff=False, score_global__gt=0
    ).order_by("-score_global")
    return render(request, "classement.html", {"etudiants": etudiants})


@login_required
def changer_mdp(request):
    if request.method == "POST":
        form = SetPasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(
                request, "Votre mot de passe a été mis à jour avec succès ! 🎉"
            )
            return redirect("profil_etudiant")
        else:
            messages.error(
                request,
                "Erreur dans le formulaire. Veuillez vérifier vos mots de passe.",
            )
    else:
        form = SetPasswordForm(user=request.user)
    return render(request, "changer_mdp.html", {"form": form})


@login_required
def profil_etudiant(request):
    try:
        tentatives = Tentative.objects.filter(etudiant=request.user)
        total_quiz = tentatives.count()
        score_brut = tentatives.aggregate(Avg("score_obtenu"))["score_obtenu__avg"]
        score_moyen = int(score_brut) if score_brut else 0
    except:
        total_quiz = 0
        score_moyen = 0

    badges = []
    if total_quiz >= 1:
        badges.append(
            {
                "nom": "Premier Pas",
                "icone": "bi-star-fill",
                "couleur": "text-warning",
                "desc": "A terminé son premier quiz.",
            }
        )
    if total_quiz >= 5:
        badges.append(
            {
                "nom": "Explorateur",
                "icone": "bi-compass",
                "couleur": "text-primary",
                "desc": "A terminé 5 quiz ou plus.",
            }
        )
    if score_moyen >= 80:
        badges.append(
            {
                "nom": "Expert Elite",
                "icone": "bi-lightning-fill",
                "couleur": "text-success",
                "desc": "Moyenne exceptionnelle (>80%).",
            }
        )

    context = {
        "total_quiz": total_quiz,
        "score_moyen": score_moyen,
        "badges": badges,
    }
    return render(request, "profil.html", context)
