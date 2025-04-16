from datetime import date
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Group
from django.contrib.auth import views as auth_views
from django.forms import BaseModelForm
from django.http.response import HttpResponse as HttpResponse
from django.http import Http404, HttpResponseBadRequest
from django.utils import timezone
from django.contrib.auth import login as auth_login
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.db.models import Q, Sum, Max
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.conf import settings
from datetime import datetime
from SIGC import views as cviews
from xauth.models import User, Assign, AccountActivationSecret
from .forms import *
from formset.views import FileUploadMixin
from django.views.generic import TemplateView

# from web.mails import mail_password
from SIGC import views as cviews
from xauth import forms
from xauth import models
from django.views.generic import CreateView, UpdateView, ListView, DeleteView, DetailView, FormView
from SIGC import (
    mails as web_mail
)
from formset.views import FormViewMixin

# Create your views here.

GENERATED_PASSWORD_LENGTH = getattr(settings, "GENERATED_PASSWORD_LENGTH", 10)
DEFAULT_FROM_EMAIL = getattr(settings, "DEFAULT_FROM_EMAIL")

# Users management



@method_decorator(transaction.atomic, name="form_valid")
@method_decorator(
    permission_required("xauth.can_assign", raise_exception=True),
    name="dispatch",
)
class AssignCreateView(cviews.CustomCreateView):
    model = models.Assign
    name = "nomination"
    form_class = forms.AssignForm
    success_url = reverse_lazy("auth:user-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(models.User, pk=self.kwargs.get(self.pk_url_kwarg))
        card_title = (
            f"Nomination du {user.grade.label} {user.get_full_name()}"
            if user.grade
            else f"Nomination de {user.get_full_name()}"
        )
        context["card_title"] = card_title
        return context

    def form_valid(self, form):
        office = form.cleaned_data["group_assign"]
        user = get_object_or_404(models.User, pk=self.kwargs.get(self.pk_url_kwarg))
        form.instance.user = user
        form.instance.assigner = self.request.user

        for permission in office.permissions.all():
            user.groups.add(permission)

        return super().form_valid(form)


@method_decorator(transaction.atomic, name="form_valid")
@method_decorator(
    permission_required("xauth.can_assign", raise_exception=True),
    name="dispatch",
) 
class RoleCreateView(cviews.CustomCreateView):
    model = models.Assign
    name = "nomination"
    form_class = forms.RoleForm
    success_url = reverse_lazy("auth:user-list")
    
    def get_template_names(self) -> list[str]:
        return ['private/user_form.html']

    def dispatch(self, request, *args, **kwargs):
        self.current_user = get_object_or_404(
            models.User, pk=self.kwargs.get(self.pk_url_kwarg)
        )
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.current_user
        
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['card_title'] = "Assignation de role"
        return context

    def form_valid(self, form):
        office = form.cleaned_data["group_assign"]
        form.instance.user = self.current_user
        form.instance.assigner = self.request.user
        form.instance.user.groups.add(office)

        try:
            clinic = form.cleaned_data.get("clinic")
            department = form.cleaned_data.get("department")
            form.instance.user.clinics.add(clinic)
        except:
            pass
        
        
       
        self.current_user.groups.add(office)
        return super().form_valid(form)


# @method_decorator(transaction.atomic, name="form_valid")
# @method_decorator(
#     permission_required("xauth.can_assign", raise_exception=True),
#     name="dispatch",
# )
# # class AssignUpdateView(cviews.CustomUpdateView):
#     model = models.Assign
#     name = "nomination"
#     form_class = forms.AssignForm
#     success_url = reverse_lazy("auth:user-list")

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         user = get_object_or_404(models.User, pk=self.kwargs.get(self.pk_url_kwarg))
#         context["card_title"] = (
#             f"Nomination du {user.grade.label} {user.get_full_name()}"
#         )
#         return context

#     def form_valid(self, form):
#         office = form.cleaned_data["office"]
#         user = get_object_or_404(models.User, pk=self.kwargs.get(self.pk_url_kwarg))
#         form.instance.user = user
#         form.instance.assigner = self.request.user
#         user.groups.add(office.permissions)
#         return super().form_valid(form)


@method_decorator(transaction.atomic, name="get")
@method_decorator(
    permission_required("xauth.can_assign", raise_exception=True),
    name="dispatch",
)
class AssignRemoveView(View):

    def get_success_url(self):
        return reverse(
            "auth:user-list")
    

    def get(self, request, *args, **kwargs):
        self.user = get_object_or_404(models.User, pk=self.kwargs.get("pk"))

        if not hasattr(self.user, "assign"):
            messages.warning(request, "Aucun rôle pour cette utilisateur")
            return redirect("auth:user-list")
        else:
            assign = get_object_or_404(models.Assign, pk=self.user.assign.pk)
            self.user.groups.remove(assign.group_assign)
            assign.user = None
            assign.save()
            assign.delete()

            messages.success(request, "Rôle retirer avec succès")
            return redirect(self.get_success_url())


# @method_decorator(
#     permission_required("xauth.list_user", raise_exception=True),
#     name="dispatch",
# )
class UserListView(cviews.CustomListView):
    model = models.User
    template_name = "private/list-user.html"
    context_object_name = "users"
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = UserCreateForm()  # Assurez-vous que form est bien un objet Form
        context["can_assign"] = self.request.user.has_perm("change_right_user")
        context["deactivate_user"] = self.request.user.has_perm("deactivate_user")
        context["can_add"]=True
        context["add_url"]=reverse(
            "auth:user-create"
        )
        if self.request.user.is_staff :

            context["can_assign"] = True
            context["deactivate_user"] = True
        return context

   
    

@method_decorator(
    permission_required("xauth.list_user", raise_exception=True),
    name="dispatch",
)
class StaffListView(ListView):
    model = models.User
    name = "user"
    template_name = "private/list-staff.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_assign"] = self.request.user.has_perm("change_right_user")
        context["deactivate_user"] = self.request.user.has_perm("deactivate_user")
        context["card_title"] = "Liste du personnel militaire"
        return context

    def get_queryset(self):
        queryset = super().get_queryset().order_by("first_name", "last_name")

        if hasattr(self.request.user, "assign"):
            queryset = queryset.filter(
                structure__in=self.request.user.assign.structure.get_children(),
                structure__isnull=False,
            )

        return queryset


@method_decorator(transaction.atomic, name="form_valid")
@method_decorator(
    permission_required("xauth.add_user", raise_exception=True),
    name="dispatch",
)


class UserCreateView(FileUploadMixin,cviews.CustomCreateView):
    model = models.User
    success_url = reverse_lazy("auth:user-list")
    
    def get_template_names(self) -> list[str]:
        return ['private/user_form.html']
    
    def get_form_class(self):
        if self.request.user.is_superuser:
            return forms.UserCreateForm
        return forms.UserCreateForm2
    

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["card_title"] = "Ajout d'un nouvel utilisateur"
        return context
    def form_valid(self, form):
        form.instance.is_active = False
        return super().form_valid(form)
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Passe l'utilisateur connecté au formulaire
        return kwargs




@method_decorator(transaction.atomic, name="form_valid")
@method_decorator(
    permission_required("xauth.change_user", raise_exception=True),
    name="dispatch",
)
class UserUpdateView(FileUploadMixin,cviews.CustomUpdateView):
    model = models.User
    form_class = forms.UserCreateForm

    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs["user"] = self.request.user
    #     return kwargs

    def dispatch(self, request, *args, **kwargs):
        user = self.get_object()
        if request.user.is_staff or request.user.id == user.id:
            return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied
    
    
    
    def get_success_url(self):
        return reverse(
            "auth:user-list"
        )

    """ def get_success_url(self):
        return reverse(
            "auth:user-list", kwargs={"pk": self.kwargs.get(self.pk_url_kwarg)}
        ) """

    """ def get_success_url(self):
        return reverse(
            "auth:user-list", kwargs={"pk": self.kwargs.get(self.pk_url_kwarg)}
        ) """

    """ def get_success_url(self):
        return reverse(
            "auth:user-list", kwargs={"pk": self.kwargs.get(self.pk_url_kwarg)}
        ) """


@method_decorator(transaction.atomic, name="form_valid")
@method_decorator(
    permission_required("xauth.change_user", raise_exception=True),
    name="dispatch",
)
class UserProfilePhotoUpdateView(FileUploadMixin , cviews.CustomUpdateView):
    model = models.User
    form_class = forms.UserChangeProfilePhotoForm

    def dispatch(self, request, *args, **kwargs):
        user = self.get_object()
        if request.user.is_superuser or request.user.id == user.id:
            return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied

    def get_success_url(self):
        return reverse(
            "auth:user-detail", kwargs={"pk": self.kwargs.get(self.pk_url_kwarg)}
        )


@method_decorator(
    permission_required("xauth.view_user", raise_exception=True),
    name="dispatch",
)
class UserDetailView(cviews.CustomDetailView):
    model = models.User

    def get_template_names(self):
        template_name = "private/user-profile-admin-view.html"

        return [template_name]
    



@method_decorator(transaction.atomic, name="render_to_response")
@method_decorator(
    permission_required("xauth.delete_user", raise_exception=True),
    name="dispatch",
)
class UserDeleteView(cviews.CustomDeleteView):
    model = models.User

    def get_success_url(self):
        return reverse("auth:user-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = forms.UserConfirmDeleteForm(user=self.get_object())
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        can_delete = True

        if self.object.is_staff:
            can_delete = False
            messages.warning(
                request,
                "Impossible de supprimer cette utilisateur il s'agit de l'utilisateur principal de la plateforme.",
            )
            messages.info(
                request,
                "À défaut de pouvoir le supprimer, vous pouvez le désactiver. Notez qu'en le désactivant vous ne pourrez plus l'utiliser pour une connexion à cette plateforme. Vous pouvez le réactiver a tout instant.",
            )
            return HttpResponseRedirect(
                reverse("auth:user-detail", kwargs={"pk": self.object.pk})
            )

        if can_delete:
            return self.render_to_response(context)
        messages.warning(
            request,
            "Impossible de supprimer cette utilisateur car pourrait être l'autre d'une tâche/activité/commentaire et/ou le destinataire d'une tâche.",
        )
        messages.info(
            request,
            "À défaut de pouvoir le supprimer, vous pouvez le désactiver. Notez qu'en le désactivant cet utilisateur ne pourra plus ce connecter à cette plateforme. Vous pouvez le réactiver a tout instant.",
        )
        return HttpResponseRedirect(
            reverse("auth:user-detail", kwargs={"pk": self.object.pk})
        )


class UserUpdatePasswordView(auth_views.PasswordChangeView):
    template_name = "models/form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.object = get_object_or_404(models.User, pk=self.kwargs.get("pk"))
        context["add_of"] = "Modification mot de passe"
        context["card_title"] = "Modification mot de passe"
        context["list_of"] = "Liste des utilisateurs"
        context["list_url"] = reverse("auth:user-list")
        context["detail_of"] = f"{self.object.get_full_name()}"
        context["detail_url"] = reverse(
            "auth:user-detail", kwargs={"pk": self.object.pk}
        )

        return context

    def get_success_url(self):
        return reverse_lazy("auth:user-detail", kwargs={"pk": self.kwargs.get("pk")})

    def form_valid(self, form):
        messages.success(self.request, "Votre mot de passe a été modifié avec succès")
        return super().form_valid(form)

class UserSendSecreteKey(View):
    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")

    def get_object(self, pk):
        return get_object_or_404(models.User, pk=pk)

    def get(self, request, *args, **kwargs):

        pk = self.kwargs.get("pk")
        if pk is None:
            raise ImproperlyConfigured("pk non passé en paramètre de url")
        self.object = self.get_object(pk)

        if not self.object.is_active:
            current_site = get_current_site(request)
            uid = urlsafe_base64_encode(force_bytes(self.object.pk))
            token = PasswordResetTokenGenerator().make_token(self.object)
            activation_link = reverse(
                "user-set-password", kwargs={"uidb64": uid, "token": token}
            )
            activation_url = (
                f"{request.scheme}://{current_site.domain}{activation_link}"
            )
            print(activation_url)
            web_mail.send_account_activation_mail(request, self.object, activation_url)
            messages.success(
                self.request,
                f"Un mail sera envoyé à {self.object.get_full_name()} pour l'activation de son compte.",
            )

        else:
            self.object.is_active = False
            self.object.save()
            messages.warning(
                self.request,
                f"Le compte de {self.object.get_full_name()} est  desactivé.",
            )

        return HttpResponseRedirect(self.get_success_url())



@method_decorator(
    permission_required("xauth.can_change_right", raise_exception=True),
    name="dispatch",
)
class UserAdminRightView(View):
    def get_success_url(self):
        return reverse("auth:user-detail", kwargs={"pk": self.kwargs.get("pk")})

    def get_object(self, pk):
        return get_object_or_404(models.User, pk=pk)

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")
        if pk is None:
            raise ImproperlyConfigured("pk non passé en paramètre de url")
        self.object = self.get_object(pk)

        if self.object.is_superuser:
            self.object.is_superuser = False
            self.object.save()
            messages.success(
                self.request,
                f"{self.object.get_full_name()} a été retiré des administrateurs de la plateforme.",
            )
        else:
            self.object.is_superuser = True
            self.object.save()
            messages.success(
                self.request,
                f"{self.object.get_full_name()} a été nommé administrateur de la plateforme..",
            )

        return HttpResponseRedirect(self.get_success_url())


@method_decorator(
    permission_required("auth.view_group", raise_exception=True),
    name="dispatch",
)
class GroupListView(cviews.CustomListView):
    model = Group
    template_name = "private/list-group.html"

    def get_queryset(self):
        queryset = super().get_queryset().order_by("name")
        user = self.request.user
        if hasattr(user, 'assign') and user.assign:
            group_id = user.assign.group_assign_id
            queryset = queryset.exclude(id=group_id)
        return queryset

        queryset = super().get_queryset().order_by("name")
        user = self.request.user
        if hasattr(user, 'assign') and user.assign:
            group_id = user.assign.group_assign_id
            queryset = queryset.exclude(id=group_id)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_add"]=True
        context["add_url"]=reverse(
            "auth:group-create"
        )
    
        return context



@method_decorator(
    permission_required("auth.add_group", raise_exception=True),
    name="dispatch",
)
class GroupCreateView(cviews.CustomCreateView):
    model = Group
    form_class = forms.GroupForm
    success_url = reverse_lazy("auth:group-list")
    
    def get_template_names(self) -> list[str]:
        return ['private/user_form.html']
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


@method_decorator(
    permission_required("auth.change_group", raise_exception=True),
    name="dispatch",
)
class GroupUpdateView(cviews.CustomUpdateView):
    model = Group
    form_class = forms.GroupForm
    success_url = reverse_lazy("auth:group-list")


@method_decorator(
    permission_required(["auth.view_group", "auth.change_group"], raise_exception=True),
    name="dispatch",
)
class GroupDetailView(cviews.CustomDetailView):
    model = Group
    template_name = "private/detail-group.html"


@method_decorator(
    permission_required("auth.delete_group", raise_exception=True),
    name="dispatch",
)
class GroupDeleteView(cviews.CustomDeleteView):
    model = Group

    def get_success_url(self):
        return reverse("auth:group-list")

    def get_can_delete(self):
        return not self.model.objects.filter(
            user__isnull=False, pk=self.object.id
        ).exists()


# Public authentication


class CustomLoginView(auth_views.LoginView):
    template_name = "public/login.html"
    success_url = reverse_lazy("index-view")
    def get_context_data(self, **kwargs):
        print('azertyuio')
        return super().get_context_data(**kwargs)


class CustomLogoutView(auth_views.LogoutView):
    next_page = reverse_lazy("user-login")
    http_method_names = ["post", "options", "get"]

    def get(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = "public/password-reset-request.html"
    success_url = reverse_lazy("password-reset-request-done")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["card_title"] = "Réinitialisation de votre mot de passe"
        return context

    def form_valid(self, form):
        self.request.session["password-reset-email"] = form.cleaned_data.get("email")
        return super().form_valid(form)


class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = "public/password-reset-request-done.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        email = self.request.session["password-reset-email"]
        context["title"] += f" par mail au {email}"
        return context


class CustomPasswordResetConfirmView(
     auth_views.PasswordResetConfirmView
):
    template_name = "public/password-reset-confirm.html"
    success_url = reverse_lazy("password-reset-complete")
    form_class = forms.CustomSetPasswordForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["card_title"] = "Réinitialisation de votre mot de passe"
        return context
class SetPasswordView(FormViewMixin,FormView):
    template_name = "public/set-password.html"
    success_url = reverse_lazy("user-login")
    form_class = CustomSetPasswordForm

    def dispatch(self, request, *args, **kwargs):
        token = kwargs.get("token")
        uid = force_str(urlsafe_base64_decode(kwargs.get("uidb64")))
        self.user = get_object_or_404(User, pk=uid)
        r = PasswordResetTokenGenerator().check_token(self.user, token)

        if not r:
            raise Http404()

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["card_title"] = "Initialisation de votre mot de passe"
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Votre compte a été activé avec succès.")
        return super().form_valid(form)
    
class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "public/password-reset-complete.html"
    # success_url = reverse_lazy("password-reset-complete")


@method_decorator(transaction.atomic, name="form_valid")
class User2CreateView(FormView):
    form_class = forms.UserPublicActivationForm
    template_name = "public/signup.html"
    
    def get_success_url(self):
        return reverse("user-set-password", kwargs={"pk": self.user.pk})

    def form_valid(self, form):
        # Set the user instance from form data
        self.user = form.cleaned_data["user"]
        secret = form.cleaned_data["secret"]

        # Filter and activate the account
        activation = models.AccountActivationSecret.all_objects.filter(
            user=self.user, secret=secret
        )
        print("Activation exists:", activation.exists())
        activation.update(is_active=True)

        # Return JSON response with the success URL
        return JsonResponse({"success_url": self.get_success_url()})

    def form_invalid(self, form):
        # Collect and format form errors to send as JSON
        errors = form.errors.as_json()
        print("Form validation errors:", errors)
        
        return JsonResponse({"errors": errors}, status=400)



# # Liste des nominations (Vue basée sur la classe)
# class NominationListView(cviews.CustomListView):
#     model = Nomination
#     name = 'nominations'
#     app_name = 'auth'
#     template_name = 'nomination_list.html'

#     def get_name(self) -> tuple[str, str]:
#         if self.name != "":
#             name = self.name
#         return name, self.app_name
    
#     def get_queryset(self):
#         queryset = Nomination.objects.all()
#         print(queryset)
#         return queryset

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         return context

# # Détail d'une nomination (Vue basée sur la classe)
# class NominationDetailView(cviews.CustomDetailView):
#     model = Nomination
#     template_name = 'nomination/nomination_detail.html'
#     name = 'nominations'
#     app_name = 'auth'

#     def get_name(self) -> tuple[str, str]:
#         if self.name != "":
#             name = self.name
#         return name, self.app_name

# # Création d'une nomination (Vue basée sur la classe)
# class NominationCreateView(cviews.CustomCreateView):
#     model = Nomination
#     form_class = NominationForm
#     name = 'nominations'
#     app_name = 'auth'
#     success_url = reverse_lazy('auth:nominations-list')

#     def get_name(self) -> tuple[str, str]:
#         if self.name != "":
#             name = self.name
#         return name, self.app_name 

# # Mise à jour d'une nomination (Vue basée sur la classe)
# class NominationUpdateView(cviews.CustomUpdateView):
#     model = Nomination
#     form_class = NominationForm
#     name = 'nominations'
#     app_name = 'auth'

#     def get_name(self) -> tuple[str, str]:
#         if self.name != "":
#             name = self.name
#         return name, self.app_name

#     def get_success_url(self):
#         return reverse_lazy('auth:nominations-list')  # Redirection vers les détails de la nomination mise à jour

# # Suppression d'une nomination (Vue basée sur la classe)
# class NominationDeleteView(cviews.CustomDeleteView):
#     model = Nomination
#     name = 'nominations'
#     app_name = 'auth'

#     def get_name(self) -> tuple[str, str]:
#         if self.name != "":
#             name = self.name
#         return name, self.app_name

#     success_url = reverse_lazy('auth:nominations-list')  # Redirige vers la liste après suppression


# def deactivate_nomination(request, pk):
#     nomination = get_object_or_404(Nomination, id=pk)

#     if nomination.is_desactivate:
#         messages.warning(request, "La nomination est déjà activée.")
#     else:
#         nomination.is_desactivate = True
#         nomination.date_fin = timezone.now()  # Enregistre l'heure et la date actuelles        
#         nomination.save()
#         messages.success(request, "La nomination a été desactivé avec succès !")

#     return redirect('auth:nominations-list')


class AssignRemoveView(View):

    def get_success_url(self):
        return reverse("auth:user-list")
        

    def get(self, request, *args, **kwargs):
        self.user = get_object_or_404(models.User, pk=self.kwargs.get("pk"))

        if not hasattr(self.user, "assign"):
            messages.warning(request, "Aucun rôle pour cette utilisateur")
            return redirect("auth:user-list")
        else:
            assign = get_object_or_404(models.Assign, pk=self.user.assign.pk)
            self.user.groups.remove(assign.group_assign)
            assign.user = None
            assign.save()
            assign.delete()

            messages.success(request, "Rôle retirer avec succès")
            return redirect(self.get_success_url())


class UserCreateReviewView(FileUploadMixin):
    template_name = 'user_create_review.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Récupérer les données du formulaire à partir de la session
        form_data = self.request.session.get('form_data', {})
        context['form_data'] = form_data
        return context




class UserCreateSubmitView(View):
    def post(self, request, *args, **kwargs):
        # Récupérer les données enregistrées dans la session
        form_data = request.session.get('form_data', {})
        
        # Créer un utilisateur avec les données
        form = UserCreateForm(data=form_data)
        
        if form.is_valid():
            form.save()  # Sauvegarde de l'utilisateur dans la base de données
            # Vous pouvez ensuite rediriger vers une page de succès
            return redirect('success')
        else:
            # Si le formulaire n'est pas valide, renvoyer à la page de récapitulatif
            return redirect('user_create_review')
        
# class AssignModuleView(View):
#     template_name = 'modules/assign_module.html'
#     form_class = ModuleAssignForm

#     def dispatch(self, request, *args, **kwargs):
#         self.teacher = get_object_or_404(models.User, pk=self.kwargs.get("pk"))
#         return super().dispatch(request, *args, **kwargs)

#     def form_valid(self, form):
#         module = form.cleaned_data['module']
#         assignment, created = TeacherModuleAssignment.objects.get_or_create(teacher=self.teacher, module=module)
#         if created:
#             messages.success(self.request, f"Le module {module.label} a été attribué à {self.teacher.first_name} {self.teacher.last_name}.")
#         else:
#             messages.warning(self.request, f"Le module {module.label} est déjà attribué à cet enseignant.")
#         return redirect('auth:user-list')  # Changez par la vue appropriée

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['teacher'] = self.teacher
#         return context


# class RemoveModuleView(View):
#     template_name = 'modules/remove_module.html'

#     def dispatch(self, request, *args, **kwargs):
#         self.teacher = get_object_or_404(User, pk=kwargs['teacher_pk'], user_type='teacher')
#         self.module = get_object_or_404(Module, pk=kwargs['module_pk'])
#         self.assignment = get_object_or_404(TeacherModuleAssignment, teacher=self.teacher, module=self.module)
#         return super().dispatch(request, *args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         self.assignment.delete()
#         messages.success(request, f"Le module {self.module.name} a été retiré à {self.teacher.first_name} {self.teacher.last_name}.")
#         return redirect('auth:user-list')  # Changez par la vue correspondante

#     def get(self, request, *args, **kwargs):
#         return render(request, self.template_name, {'module': self.module, 'teacher': self.teacher})


# # Création d'une nomination (Vue basée sur la classe)
# class NominationCreateView(cviews.CustomCreateView):
#     model = Nomination
#     form_class = NominationForm
#     name = 'nominations'
#     app_name = 'auth'
#     success_url = reverse_lazy('auth:nominations-list')

#     def get_name(self) -> tuple[str, str]:
#         if self.name != "":
#             name = self.name
#         return name, self.app_name 



# class AssignModuleView(cviews.CustomCreateView):
#     model = AttributModule
#     form_class = AttributModuleForm
#     name = 'assignation'
#     app_name = 'auth'
#     success_url = reverse_lazy('auth:user-list')

#     def dispatch(self, request, *args, **kwargs):
#         """Récupère l'enseignant depuis l'URL"""
#         self.teacher = get_object_or_404(User, pk=self.kwargs.get('pk'), user_type='teacher')
#         return super().dispatch(request, *args, **kwargs)

#     def get_form_kwargs(self):
#         """Passe l'enseignant sélectionné au formulaire"""
#         kwargs = super().get_form_kwargs()
#         kwargs['teacher'] = self.teacher  # Ajoute l’enseignant pour qu'il apparaisse grisé
#         return kwargs

#     def form_valid(self, form):
#         attribut_module = form.save(commit=False)
#         attribut_module.enseignant = self.teacher  # Affecte l’enseignant sélectionné
#         attribut_module.save()
#         form.save_m2m()  # Sauvegarde les relations ManyToMany si nécessaire

#         messages.success(self.request, f"Les modules ont été attribués à {self.teacher.first_name} {self.teacher.last_name}.")
#         return redirect(self.success_url)


# class AssignModuleListView(cviews.CustomListView):
#     model = AttributModule
#     name = "attributmodule"
#     app_name = 'auth'
#     template_name = "list-attribut_module.html"

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         return context

# class AssignModuleCreateView(cviews.CustomCreateView):
#     model = AttributModule
#     form_class = AttributModuleForm
#     name = "attributmodule"
#     success_url = reverse_lazy("auth:attributmodule-list")
    


# class AssignModuleUpdateView(cviews.CustomUpdateView):
#     model = AttributModule
#     name = "attributmodule"
#     form_class = AttributModuleForm
#     success_url = reverse_lazy("auth:attributmodule-list")


# class AssignModuleDetailView(cviews.CustomDetailView):
#     model = AttributModule
#     name = "attributmodule"
#     template_name = "attribut_module/detail-attribut_module.html"


# class AssignModuleDeleteView(cviews.CustomDeleteView):
#     model = AttributModule
#     name = "attributmodule"
#     template_name = "attribut_module/delete-attribut_module.html"
#     success_url = reverse_lazy("auth:attributmodule-list")



# class UserModulesUpdateView(cviews.CustomUpdateView):
#     model = User
#     form_class = forms.UserModulesForm
#     success_url = reverse_lazy("auth:user-list")

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['user'] = self.request.user
#         return kwargs

#     def form_valid(self, form):
#         user = self.get_object()
#         modules = form.cleaned_data.get('module')
#         modules_user = user.module.all()
#         for module in modules_user:
#             module.is_attribut = False
#             module.save()
#         for module in modules:
#             module.is_attribut = True
#             module.save()

#         return super().form_valid(form)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         user = self.get_object()
#         context['card_title'] = f"Attribution de module : {user}"
#         return context