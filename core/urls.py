from django.contrib import admin
from django.urls import path
from utilisateurs import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("dashboard/", views.dashboard_etudiant, name="dashboard_etudiant"),
    path("quiz/<int:quiz_id>/", views.passer_quiz, name="passer_quiz"),
    path("quiz/<int:quiz_id>/soumettre/", views.soumettre_quiz, name="soumettre_quiz"),
    path("quiz/<int:quiz_id>/terminer/", views.terminer_quiz, name="terminer_quiz"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="login.html", redirect_authenticated_user=True
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("classement/", views.classement, name="classement"),
    path("changer-mdp/", views.changer_mdp, name="changer_mdp"),
    path("profil/", views.profil_etudiant, name="profil"),
]
