from django.views.generic import *
from multiprocessing import context
from typing import Any
from django.db.models import Model, Q, QuerySet, Field
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
    RedirectView,
    View
)
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.conf import settings
from formset.views import (
    FormViewMixin as FormsetViewMixin,
    FormCollectionView,
    EditCollectionView,
    IncompleteSelectResponseMixin,
)
from xauth.models import  User
from formset.views import FileUploadMixin



LIST_MAX_ROWS = 10


class IndexTemplateView(TemplateView):
    template_name = "index.html"  # Spécifiez directement le nom du template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # # Vérifiez les rôles ou permissions spécifiques de l'utilisateur
        # access_vice_president = user.has_perm("xauth.vice_president")
        # access_responsable_programme = user.has_perm("xauth.responsable_programme")
        # access_responsable_filiere = user.has_perm("xauth.responsable_filiere")

        # # Filtrer les enseignements en fonction des rôles
        # enseignements_queryset = Enseignements.objects.none()
        # if access_vice_president:
        #     # Le vice-président voit tout
        #     enseignements_queryset = Enseignements.objects.all()
        # else:
        #     nomination = Nomination.objects.filter(user=user, is_desactivate=False).first()
        #     if nomination:
        #         if access_responsable_programme:
        #             # Responsable programme : enseignements liés au département
        #             enseignements_queryset = Enseignements.objects.filter(
        #                 filiere__departement=nomination.departement
        #             )
        #         elif access_responsable_filiere:
        #             # Responsable filière : enseignements liés à la filière
        #             enseignements_queryset = Enseignements.objects.filter(
        #                 filiere=nomination.filiere
        #             )
        #     else:
        #             # Enseignant : enseignements liés à ses propres fiches
        #         enseignements_queryset = Enseignements.objects.filter(sheet__enseignant=user)

        # # Calcul des statistiques
        # context['nombre_enseignements'] = enseignements_queryset.count()
        # context['enseignements_validees'] = enseignements_queryset.filter(is_validated=True).count()
        # context['enseignements_rejetees'] = enseignements_queryset.filter(is_validated=False).count()
        # context['enseignements_en_cours'] = enseignements_queryset.filter(is_validated=None).count()

        return context

class RedirectionView(RedirectView):
    url = "/home/"

# Page d'atterrissage
class LandingPageView(TemplateView):
    template_name = 'landing_page.html'

        
    
class CustomViewMixin:
    name = ""

    def get_name(self) -> tuple[str, str]:
        name = self.model.__name__.lower()
        if self.name != "":
            name = self.name
        return name, self.model._meta.app_label.lower()

    def get_title(self, o):
        if hasattr(o, "label"):
            return o.label
        elif hasattr(o, "name"):
            return o.name
        elif hasattr(o, "username"):
            return o.username
        else:
            return o.id


class CustomDetailView(CustomViewMixin, DetailView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        o = self.get_object()
        name, app_name = self.get_name()
        model_name = self.model.__name__.lower()

        context["can_update"] = self.request.user.has_perm(
            f"{app_name}.change_{model_name}"
        )
        context["can_delete"] = self.request.user.has_perm(
            f"{app_name}.delete_{model_name}"
        )
        context["list_of"] = f"Liste des {o._meta.verbose_name_plural}"
        try:
            context["list_url"] = reverse(f"{app_name}:{name}-list")
        except Exception as exp:
            context["list_url"] = None

        try:
            context["delete_url"] = reverse(
                f"{app_name}:{name}-delete", kwargs={"slug": o.slug}
            )
        except Exception as exp:
            try:
                context["delete_url"] = reverse(
                    f"{app_name}:{name}-delete", kwargs={"pk": o.pk}
                )
            except Exception as exp:
                context["delete_url"] = None

        try:
            context["update_url"] = reverse(
                f"{app_name}:{name}-update", kwargs={"slug": o.slug}
            )
        except Exception as exp:
            try:
                context["update_url"] = reverse(
                    f"{app_name}:{name}-update", kwargs={"pk": o.id}
                )
            except Exception as exp:
                context["update_url"] = None

        context["card_title"] = self.get_title(o)
        context["back_url"] =  self.request.META.get('HTTP_REFERER','/')
        return context





class CustomMouvementDeleteView(CustomViewMixin, DeleteView):
    template_name = "models/delete.html"

    def get_success_url(self):
        name, app_name = self.get_name()
        try:
            url = reverse(f"{app_name}:mouvement-list")
        except Exception as exp:
            url = ""

        return url

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        name, app_name = self.get_name()
        model_name = self.model.__name__.lower()
        context = super().get_context_data(**kwargs)
        context["card_title"] = f"Liste des mouvements"

        try:
            context["list_url"] = reverse(f"{app_name}:mouvement-list")
        except Exception as exp:
            context["list_url"] = None

        context["list_of"] = f"Liste des mouvements"
        context["what_of"] = self.get_title(self.object)
        context["what_to"] = self.object._meta.verbose_name

        return context

    def form_valid(self, form):
        messages.success(
            self.request, f"{self.get_object()} a été supprimé avec succès"
        )
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        self.process_before_delete()
        if hasattr(self.object, "is_removed"):
            self.object.is_removed = True
            self.object.save()
        else:
            self.object.delete()

        self.process_after_delete()

        messages.success(request, f"{self.object} a été supprimé avec succès.")
        return HttpResponseRedirect(self.get_success_url())

    def get_can_delete(self):
        return True

    def process_before_delete(self):
        pass

    def process_after_delete(self):
        pass

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        name, app_name = self.get_name()

        can_delete = self.get_can_delete()

        if can_delete:
            return self.render_to_response(context)
        messages.warning(request, "Impossible de supprimer cet élément.")

        try:
            detail_url = reverse(
                f"{app_name}:mouvement-detail", kwargs={"slug": self.object.slug}
            )
        except Exception as exp:
            try:
                detail_url = reverse(
                    f"{app_name}:mouvement-detail", kwargs={"pk": self.object.pk}
                )
            except Exception as exp:
                detail_url = ""
        return HttpResponseRedirect(detail_url)

class CustomDeleteView(CustomViewMixin, DeleteView):
    template_name = "models/delete.html"

    def get_success_url(self):
        name, app_name = self.get_name()
        try:
            url = reverse(f"{app_name}:{name}-list")
        except Exception as exp:
            url = ""

        return url

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        name, app_name = self.get_name()
        model_name = self.model.__name__.lower()
        context = super().get_context_data(**kwargs)
        context["card_title"] = f"Liste des {self.object._meta.verbose_name_plural}"

        try:
            context["list_url"] = reverse(f"{app_name}:{name}-list")
        except Exception as exp:
            context["list_url"] = None

        context["list_of"] = f"Liste des {self.object._meta.verbose_name_plural}"
        context["what_of"] = self.get_title(self.object)
        context["what_to"] = self.object._meta.verbose_name

        return context

    def form_valid(self, form):
        messages.success(
            self.request, f"{self.get_object()} a été supprimé avec succès"
        )
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        self.process_before_delete()
        if hasattr(self.object, "is_removed"):
            self.object.is_removed = True
            self.object.save()
        else:
            self.object.delete()

        self.process_after_delete()

        messages.success(request, f"{self.object} a été supprimé avec succès.")
        return HttpResponseRedirect(self.get_success_url())

    def get_can_delete(self):
        return True

    def process_before_delete(self):
        pass

    def process_after_delete(self):
        pass

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        name, app_name = self.get_name()

        can_delete = self.get_can_delete()

        if can_delete:
            return self.render_to_response(context)
        messages.warning(request, "Impossible de supprimer cet élément.")

        try:
            detail_url = reverse(
                f"{app_name}:{name}-detail", kwargs={"slug": self.object.slug}
            )
        except Exception as exp:
            try:
                detail_url = reverse(
                    f"{app_name}:{name}-detail", kwargs={"pk": self.object.pk}
                )
            except Exception as exp:
                detail_url = ""
        return HttpResponseRedirect(detail_url)


class CustomDeleteView1(CustomViewMixin, DeleteView):
    template_name = "models/delete.html"

    def get_success_url(self):
        name, app_name = self.get_name()
        try:
            url = reverse(f"{app_name}:sortant-list")
        except Exception as exp:
            url = ""

        return url

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        name, app_name = self.get_name()
        model_name = self.model.__name__.lower()
        context = super().get_context_data(**kwargs)
        context["card_title"] = f"Liste des {self.object._meta.verbose_name_plural}"

        try:
            context["list_url"] = reverse(f"{app_name}:{name}-list")
        except Exception as exp:
            context["list_url"] = None

        context["list_of"] = f"Liste des {self.object._meta.verbose_name_plural}"
        context["what_of"] = self.get_title(self.object)
        context["what_to"] = self.object._meta.verbose_name

        return context

    def form_valid(self, form):
        messages.success(
            self.request, f"{self.get_object()} a été supprimé avec succès"
        )
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        self.process_before_delete()
        if hasattr(self.object, "is_removed"):
            self.object.is_removed = True
            self.object.save()
        else:
            self.object.delete()

        self.process_after_delete()

        messages.success(request, f"{self.object} a été supprimé avec succès.")
        return HttpResponseRedirect(self.get_success_url())

    def get_can_delete(self):
        return True

    def process_before_delete(self):
        pass

    def process_after_delete(self):
        pass

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        name, app_name = self.get_name()

        can_delete = self.get_can_delete()

        if can_delete:
            return self.render_to_response(context)
        messages.warning(request, "Impossible de supprimer cet élément.")

        try:
            detail_url = reverse(
                f"{app_name}:{name}-detail", kwargs={"slug": self.object.slug}
            )
        except Exception as exp:
            try:
                detail_url = reverse(
                    f"{app_name}:{name}-detail", kwargs={"pk": self.object.pk}
                )
            except Exception as exp:
                detail_url = ""
        return HttpResponseRedirect(detail_url)

class CustomCreateView1(
    IncompleteSelectResponseMixin, FormsetViewMixin, CustomViewMixin, CreateView
):
    template_name = "models/form-entrant.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        name, app_name = self.get_name()

        try:
            context["list_url"] = reverse(f"{app_name}:{name}-list")
        except Exception as exp:
            context["list_url"] = ""
        context["can_rerender"] = True
        context["add_of"] = f"Ajout {self.model._meta.verbose_name}"
        context["card_title"] = f"Enregistrement {self.model._meta.verbose_name}"
        context["list_of"] = f"Liste des {self.model._meta.verbose_name_plural}"
        return context
    def form_valid(self, form):
        messages.success(self.request, f"{form.instance} a été ajouté avec succès")
        return super().form_valid(form)



class CustomCreateView2(
    IncompleteSelectResponseMixin, FormsetViewMixin, CustomViewMixin, CreateView
):
    template_name = "models/form-sortant.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        name, app_name = self.get_name()

        try:
            context["list_url"] = reverse(f"{app_name}:{name}-list")
        except Exception as exp:
            context["list_url"] = ""

        context["can_rerender"] = True
        context["add_of"] = f"Ajout {self.model._meta.verbose_name}"
        context["card_title"] = f"Enregistrement {self.model._meta.verbose_name}"
        context["list_of"] = f"Liste des {self.model._meta.verbose_name_plural}"

        return context

    def form_valid(self, form):
        messages.success(self.request, f"{form.instance} a été ajouté avec succès")
        return super().form_valid(form)


class CustomListView1(CustomViewMixin, ListView):
    paginate_by = LIST_MAX_ROWS

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        name, app_name = self.get_name()
        model_name = self.model._name_.lower()
        url_name = app_name

        if name in ["user"]:
            url_name = "auth"

        context["import_url"] = reverse(
            "ie_app:import-view", kwargs={"model_name": f"{app_name}.{model_name}"}
        )
        context["export_url"] = reverse(
            "ie_app:export-view",
            kwargs={"model_name": f"{app_name}.{model_name}", "with_data": 1},
        )
        context["model_url"] = reverse(
            "ie_app:export-view",
            kwargs={"model_name": f"{app_name}.{model_name}", "with_data": 0},
        )

        try:
            context["add_url"] = reverse(f"{url_name}:{name}-create")
            context["can_add"] = self.request.user.has_perm(
                f"{app_name}.add_{model_name}"
            )
        except Exception as exp:
            context["can_add"] = False
            context["add_url"] = ""

        try:
            context["search_url"] = reverse(f"{url_name}:mouvement-list")
        except Exception as exp:
            ...

        context["can_export"] = self.request.user.has_perm(
            f"{app_name}.export_{model_name}"
        )
        context["can_import"] = self.request.user.has_perm(
            f"{app_name}.import_{model_name}"
        )

        try:
            reverse(f"{url_name}:{name}-detail")
            context["can_detail"] = self.request.user.has_perm(
                f"{app_name}.view_{model_name}"
            )
        except Exception as exp:
            if str(exp).find("with no arguments not found") != -1:
                context["info_url"] = f"{url_name}:{name}-detail"
                context["can_detail"] = self.request.user.has_perm(
                    f"{app_name}.view_{model_name}"
                )
            else:
                context["can_detail"] = False
        try:
            reverse(f"{url_name}:{name}-delete")
            context["can_delete"] = self.request.user.has_perm(
                f"{app_name}.delete_{model_name}"
            )
        except Exception as exp:
            if str(exp).find("with no arguments not found") != -1:
                context["can_delete"] = self.request.user.has_perm(
                    f"{app_name}.delete_{model_name}"
                )
                context["delete_url"] = f"{url_name}:{name}-delete"
            else:
                context["can_delete"] = False
        try:
            reverse(f"{url_name}:{name}-update")
            context["can_update"] = self.request.user.has_perm(
                f"{app_name}.change_{model_name}"
            )
        except Exception as exp:
            if str(exp).find("with no arguments not found") != -1:
                context["update_url"] = f"{url_name}:{name}-update"
                context["can_update"] = self.request.user.has_perm(
                    f"{app_name}.change_{model_name}"
                )
            else:
                context["can_update"] = False

        try:
            reverse(f"{url_name}:{name}-print")
            context["can_print"] = self.request.user.has_perm(
                f"{app_name}.view_{model_name}"
            )
        except Exception as exp:
            if str(exp).find("with no arguments not found") != -1:
                context["print_url"] = f"{url_name}:{name}-print"
                context["can_print"] = self.request.user.has_perm(
                    f"{app_name}.view_{model_name}"
                )
            else:
                context["can_print"] = False

        context["card_title"] = f"Liste des {self.model._meta.verbose_name_plural}"

        return context

    def get_queryset(self):
        if hasattr(self.model, "available_objects"):
            queryset = self.model.available_objects.all()
            ordering = self.get_ordering()
            if ordering:
                if isinstance(ordering, str):
                    ordering = (ordering,)
                queryset = queryset.order_by(*ordering)
        else:
            queryset = super().get_queryset()

        query: str = self.request.GET.get("query", None)
        if query is None:
            return queryset
        else:
            queryset = self.search(self.model._meta.fields, queryset, query)
            return queryset

    def search(self, fields: list[Field], queryset: QuerySet, query: str):
        from django.db.models import (
            CharField,
            TextField,
            IntegerField,
            FloatField,
            DecimalField,
            ForeignKey,
            DateField,
        )

        searchable_fields = (
            CharField,
            TextField,
            IntegerField,
            FloatField,
            DecimalField,
            DateField,
            
        )

        field_list = [field for field in fields if isinstance(field, searchable_fields)]
        foreign_keys = [
            (field.name, field)
            for field in self.model._meta.fields
            if isinstance(field, ForeignKey)
        ]
        foreign_keys = [
            (name, field.related_model._meta.fields) for name, field in foreign_keys
        ]
        foreign_keys = [
            (name, field) for name, sublist in foreign_keys for field in sublist
        ]
        foreign_keys = [
            (name, field)
            for name, field in foreign_keys
            if isinstance(field, searchable_fields)
        ]

        queries = [
            Q({field.name + "__icontains": query.strip()}) for field in field_list
        ]
        queries += [
            Q({name + "" + field.name + "__icontains": query.strip()})
            for name, field in foreign_keys
        ]
        q_object = Q()
        for q in queries:
            q_object = q_object | q
        queryset = queryset.filter(q_object)
        return queryset.distinct()


class CustomCreateView(
    IncompleteSelectResponseMixin, FormsetViewMixin, CustomViewMixin, CreateView
):
    template_name = "models/form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        name, app_name = self.get_name()

        try:
            context["list_url"] = reverse(f"{app_name}:{name}-list")
        except Exception as exp:
            context["list_url"] = ""

        context["can_rerender"] = True
        context["add_of"] = f"Ajout {self.model._meta.verbose_name}"
        context["card_title"] = f"Enregistrement {self.model._meta.verbose_name}"
        context["list_of"] = f"Liste des {self.model._meta.verbose_name_plural}"

        return context

    def form_valid(self, form):
        messages.success(self.request, f"{form.instance} a été ajouté avec succès")
        return super().form_valid(form)

class CustomProductCreateView(
    IncompleteSelectResponseMixin, FormsetViewMixin, CustomViewMixin, CreateView
):
    template_name = "models/form_stock.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        name, app_name = self.get_name()

        try:
            context["list_url"] = reverse(f"{app_name}:{name}-list")
        except Exception as exp:
            context["list_url"] = ""

        context["can_rerender"] = True
        context["add_of"] = f"Ajout {self.model._meta.verbose_name}"
        context["card_title"] = f"Enregistrement {self.model._meta.verbose_name}"
        context["list_of"] = f"Liste des {self.model._meta.verbose_name_plural}"

        return context

    def form_valid(self, form):
        messages.success(self.request, f"{form.instance} a été ajouté avec succès")
        return super().form_valid(form)




class CustomCreatePlanningView(
    IncompleteSelectResponseMixin, FormsetViewMixin, CustomViewMixin, CreateView
):
    template_name = "models/form_planning.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        name, app_name = self.get_name()

        try:
            context["list_url"] = reverse(f"{app_name}:{name}-list")
        except Exception as exp:
            context["list_url"] = ""

        context["can_rerender"] = True
        context["add_of"] = f"Ajout {self.model._meta.verbose_name}"
        context["card_title"] = f"Enregistrement {self.model._meta.verbose_name}"
        context["list_of"] = f"Liste des {self.model._meta.verbose_name_plural}"

        return context

    def form_valid(self, form):
        messages.success(self.request, f"{form.instance} a été ajouté avec succès")
        return super().form_valid(form)

class CustomMouvementUpdateView(
    IncompleteSelectResponseMixin, FormsetViewMixin, CustomViewMixin, UpdateView,
):
    template_name = "form_vente.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        name, app_name = self.get_name()

        try:
            context["list_url"] = reverse(f"{app_name}:{name}-list")
        except Exception as exp:
            context["list_url"] = ""

        context["can_rerender"] = False
        context["add_of"] = f"Modification {self.model._meta.verbose_name}"
        context["card_title"] = f"Modification {self.model._meta.verbose_name}"
        context["list_of"] = f"Liste des {self.model._meta.verbose_name_plural}"
        context["detail_of"] = self.get_title(self.object)

        try:
            context["detail_url"] = reverse(
                f"{app_name}:{name}-detail",
                kwargs={"slug": self.kwargs.get(self.slug_url_kwarg)},
            )
        except:
            try:
                context["detail_url"] = reverse(
                    f"{app_name}:{name}-detail",
                    kwargs={"pk": self.kwargs.get(self.pk_url_kwarg)},
                )
            except:
                context["detail_url"] = ""

        return context

    def form_valid(self, form):
        messages.success(self.request, f"{self.get_object()} a été modifié avec succès")
        return super().form_valid(form)



class CustomUpdateView(
    IncompleteSelectResponseMixin, FormsetViewMixin, CustomViewMixin, UpdateView
):
    template_name = "models/form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        name, app_name = self.get_name()

        try:
            context["list_url"] = reverse(f"{app_name}:{name}-list")
        except Exception as exp:
            context["list_url"] = ""

        context["can_rerender"] = False
        context["add_of"] = f"Modification {self.model._meta.verbose_name}"
        context["card_title"] = f"Modification {self.model._meta.verbose_name}"
        context["list_of"] = f"Liste des {self.model._meta.verbose_name_plural}"
        context["detail_of"] = self.get_title(self.object)

        try:
            context["detail_url"] = reverse(
                f"{app_name}:{name}-detail",
                kwargs={"slug": self.kwargs.get(self.slug_url_kwarg)},
            )
        except:
            try:
                context["detail_url"] = reverse(
                    f"{app_name}:{name}-detail",
                    kwargs={"pk": self.kwargs.get(self.pk_url_kwarg)},
                )
            except:
                context["detail_url"] = ""

        return context

    def form_valid(self, form):
        messages.success(self.request, f"{self.get_object()} a été modifié avec succès")
        return super().form_valid(form)
    
  
class CustomProductUpdateView(
    IncompleteSelectResponseMixin, FormsetViewMixin, CustomViewMixin, UpdateView
):
    template_name = "models/form_stock.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        name, app_name = self.get_name()

        try:
            context["list_url"] = reverse(f"{app_name}:{name}-list")
        except Exception as exp:
            context["list_url"] = ""

        context["can_rerender"] = False
        context["add_of"] = f"Modification {self.model._meta.verbose_name}"
        context["card_title"] = f"Modification {self.model._meta.verbose_name}"
        context["list_of"] = f"Liste des {self.model._meta.verbose_name_plural}"
        context["detail_of"] = self.get_title(self.object)

        try:
            context["detail_url"] = reverse(
                f"{app_name}:{name}-detail",
                kwargs={"slug": self.kwargs.get(self.slug_url_kwarg)},
            )
        except:
            try:
                context["detail_url"] = reverse(
                    f"{app_name}:{name}-detail",
                    kwargs={"pk": self.kwargs.get(self.pk_url_kwarg)},
                )
            except:
                context["detail_url"] = ""

        return context

    def form_valid(self, form):
        messages.success(self.request, f"{self.get_object()} a été modifié avec succès")
        return super().form_valid(form)
 
  
  
    
#patient
class CustomListView1(CustomViewMixin, ListView):
    paginate_by = LIST_MAX_ROWS

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        app_name = self.get_name()
        model_name = 'patient'
        name = 'patient'
        url_name = 'health'

        if name in ["user"]:
            url_name = "auth"

        context["import_url"] = reverse(
            "ie_app:import-view", kwargs={"model_name": f"{app_name}.{model_name}"}
        )
        context["export_url"] = reverse(
            "ie_app:export-view",
            kwargs={"model_name": f"{app_name}.{model_name}", "with_data": 1},
        )
        context["model_url"] = reverse(
            "ie_app:export-view",
            kwargs={"model_name": f"{app_name}.{model_name}", "with_data": 0},
        )

        try:
            context["add_url"] = reverse(f"{url_name}:{name}-create")
            context["can_add"] = self.request.user.has_perm(
                f"{app_name}.add_{model_name}"
            )
        except Exception as exp:
            context["can_add"] = False
            context["add_url"] = ""

        try:
            context["search_url"] = reverse(f"{url_name}:{name}-list")
        except Exception as exp:
            ...

        context["can_export"] = self.request.user.has_perm(
            f"{app_name}.export_{model_name}"
        )
        context["can_import"] = self.request.user.has_perm(
            f"{app_name}.import_{model_name}"
        )

        try:
            reverse(f"{url_name}:{name}-detail")
            context["can_detail"] = self.request.user.has_perm(
                f"{app_name}.view_{model_name}"
            )
        except Exception as exp:
            if str(exp).find("with no arguments not found") != -1:
                context["info_url"] = f"{url_name}:{name}-detail"
                context["can_detail"] = self.request.user.has_perm(
                    f"{app_name}.view_{model_name}"
                )
            else:
                context["can_detail"] = False

        try:
            reverse(f"{url_name}:{name}-delete")
            context["can_delete"] = self.request.user.has_perm(
                f"{app_name}.delete_{model_name}"
            )
        except Exception as exp:
            if str(exp).find("with no arguments not found") != -1:
                context["can_delete"] = self.request.user.has_perm(
                    f"{app_name}.delete_{model_name}"
                )
                context["delete_url"] = f"{url_name}:{name}-delete"
            else:
                context["can_delete"] = False
        try:
            reverse(f"{url_name}:{name}-update")
            context["can_update"] = self.request.user.has_perm(
                f"{app_name}.change_{model_name}"
            )
        except Exception as exp:
            if str(exp).find("with no arguments not found") != -1:
                context["update_url"] = f"{url_name}:{name}-update"
                context["can_update"] = self.request.user.has_perm(
                    f"{app_name}.change_{model_name}"
                )
            else:
                context["can_update"] = False

        try:
            reverse(f"{url_name}:{name}-print")
            context["can_print"] = self.request.user.has_perm(
                f"{app_name}.view_{model_name}"
            )
        except Exception as exp:
            if str(exp).find("with no arguments not found") != -1:
                context["print_url"] = f"{url_name}:{name}-print"
                context["can_print"] = self.request.user.has_perm(
                    f"{app_name}.view_{model_name}"
                )
            else:
                context["can_print"] = False

        context["card_title"] = f"Liste des {self.model._meta.verbose_name_plural}"
        return context

    def get_queryset(self):
        if hasattr(self.model, "available_objects"):
            queryset = self.model.available_objects.all()
            ordering = self.get_ordering()
            if ordering:
                if isinstance(ordering, str):
                    ordering = (ordering,)
                queryset = queryset.order_by(*ordering)
        else:
            queryset = super().get_queryset()

        query: str = self.request.GET.get("query", None)
        if query is None:
            return queryset
        else:
            queryset = self.search(self.model._meta.fields, queryset, query)
            return queryset

    def search(self, fields: list[Field], queryset: QuerySet, query: str):
        from django.db.models import (
            CharField,
            TextField,
            IntegerField,
            FloatField,
            DecimalField,
            ForeignKey,
        )

        searchable_fields = (
            CharField,
            TextField,
            IntegerField,
            FloatField,
            DecimalField,
        )

        field_list = [field for field in fields if isinstance(field, searchable_fields)]
        foreign_keys = [
            (field.name, field)
            for field in self.model._meta.fields
            if isinstance(field, ForeignKey)
        ]
        foreign_keys = [
            (name, field.related_model._meta.fields) for name, field in foreign_keys
        ]
        foreign_keys = [
            (name, field) for name, sublist in foreign_keys for field in sublist
        ]
        foreign_keys = [
            (name, field)
            for name, field in foreign_keys
            if isinstance(field, searchable_fields)
        ]

        queries = [
            Q(**{field.name + "__icontains": query.strip()}) for field in field_list
        ]
        queries += [
            Q(**{name + "__" + field.name + "__icontains": query.strip()})
            for name, field in foreign_keys
        ]

        q_object = Q()
        for q in queries:
            q_object = q_object | q
        queryset = queryset.filter(q_object)
        return queryset.distinct()



class  CustomListView(CustomViewMixin, ListView):
    
    def get_paginate_by(self, queryset):
        paginate_by = LIST_MAX_ROWS
        return paginate_by

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        name, app_name = self.get_name()
        model_name = self.model.__name__.lower() 
        url_name = app_name

        if name in ["user", "attributmodule"]:
            url_name = "auth"

        try:
            context["add_url"] = reverse(f"{url_name}:{name}-create")
            context["can_add"] = self.request.user.has_perm(
                f"{app_name}.add_{model_name}"
            )
        except Exception as exp:
            context["can_add"] = False
            context["add_url"] = ""

        try:
            context["search_url"] = reverse(f"{url_name}:{name}-list")
        except Exception as exp:
            ...

        context["can_export"] = self.request.user.has_perm(
            f"{app_name}.export_{model_name}"
        )
        context["can_import"] = self.request.user.has_perm(
            f"{app_name}.import_{model_name}"
        )

        try:
            reverse(f"{url_name}:{name}-detail")
            context["can_detail"] = self.request.user.has_perm(
                f"{app_name}.view_{model_name}"
            )
        except Exception as exp:
            if str(exp).find("with no arguments not found") != -1:
                context["info_url"] = f"{url_name}:{name}-detail"
                context["can_detail"] = self.request.user.has_perm(
                    f"{app_name}.view_{model_name}"
                )
            else:
                context["can_detail"] = False
        try:
            reverse(f"{url_name}:{name}-delete")
            context["can_delete"] = self.request.user.has_perm(
                f"{app_name}.delete_{model_name}"
            )
        except Exception as exp:
            if str(exp).find("with no arguments not found") != -1:
                context["can_delete"] = self.request.user.has_perm(
                    f"{app_name}.delete_{model_name}"
                )
                context["delete_url"] = f"{url_name}:{name}-delete"
            else:
                context["can_delete"] = False
        try:
            reverse(f"{url_name}:{name}-update")
            context["can_update"] = self.request.user.has_perm(
                f"{app_name}.change_{model_name}"
            )
        except Exception as exp:
            if str(exp).find("with no arguments not found") != -1:
                context["update_url"] = f"{url_name}:{name}-update"
                context["can_update"] = self.request.user.has_perm(
                    f"{app_name}.change_{model_name}"
                )
            else:
                context["can_update"] = False
        try:
            reverse(f"{url_name}:{name}-print")
            context["can_print"] = self.request.user.has_perm(
                f"{app_name}.view_{model_name}"
            )
        except Exception as exp:
            if str(exp).find("with no arguments not found") != -1:
                context["print_url"] = f"{url_name}:{name}-print"
                context["can_print"] = self.request.user.has_perm(
                    f"{app_name}.view_{model_name}"
                )
            else:
                context["can_print"] = False
        context["card_title"] = f"Liste des {self.model._meta.verbose_name_plural}"
        return context
class CustomFormCollectionView(CustomViewMixin, FormCollectionView):
    template_name = "models/form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        name, app_name = self.get_name()

        try:
            context["list_url"] = reverse(f"{app_name}:{name}-list")
        except Exception as exp:
            context["list_url"] = None

        context["can_rerender"] = True
        context["add_of"] = f"Ajout {self.model._meta.verbose_name}"
        context["card_title"] = f"Enregistrement {self.model._meta.verbose_name}"
        context["list_of"] = f"Liste des {self.model._meta.verbose_name_plural}"

        return context


class CustomEditCollectionView(CustomViewMixin, EditCollectionView):
    template_name = "models/form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        name, app_name = self.get_name()

        try:
            context["list_url"] = reverse(f"{app_name}:{name}-list")
        except Exception as exp:
            context["list_url"] = None

        context["can_rerender"] = False
        context["add_of"] = f"Modification {self.model._meta.verbose_name}"
        context["card_title"] = f"Modification {self.model._meta.verbose_name}"
        context["list_of"] = f"Liste des {self.model._meta.verbose_name_plural}"
        context["detail_of"] = self.get_title(self.object)

        try:
            context["detail_url"] = reverse(
                f"{app_name}:{name}-detail",
                kwargs={"slug": self.kwargs.get(self.slug_url_kwarg)},
            )
        except:
            try:
                context["detail_url"] = reverse(
                    f"{app_name}:{name}-detail",
                    kwargs={"pk": self.kwargs.get(self.pk_url_kwarg)},
                )
            except:
                context["detail_url"] = ""

        return context
    
def back_button_view(request):
    """
    Vue pour gérer le bouton "Retour".
    Redirige vers l'URL précédente ou vers une URL par défaut.
    """
    previous_url = request.META.get('HTTP_REFERER', '/')
    return redirect(previous_url)



