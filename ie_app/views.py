from datetime import date

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views.generic import View, FormView
from django.apps import apps
from django.urls import reverse, reverse_lazy
from ie_app.forms import *
from import_export.formats import base_formats
import zipfile

from import_export import (
    forms as ie_forms,
    tmp_storages as ie_tmp_storages,
    mixins as ie_mixins,
    results as ie_results,
    admin as ie_admin,
    resources as ie_resources,
)
from tablib import Dataset
from formset.views import FormViewMixin

from ie_app.resources import resource_classes
from ie_app import resources

# Create your views here.

@method_decorator([require_http_methods(["GET"])], name="get")
class ExportView(View):
    def get(self, request, model_name: str, with_data=1, *args, **kwargs):
        try:
            model = apps.get_model(model_name)
        except Exception:
            messages.error(request, "Impossible d'exporter cette table.")
            return redirect(request.META.get("HTTP_REFERER"))

        try:
            resource_class = resource_classes.get(model.__name__, resource_classes["default"])
            resource = ie_resources.modelresource_factory(model=model, resource_class=resource_class)
        except KeyError:
            resource = ie_resources.modelresource_factory(model=model, resource_class=resource_classes["default"])

        if not resource:
            messages.error(request, "Impossible d'exporter les données de cette table.")
            return redirect(request.META.get("HTTP_REFERER"))

        resource = resource(with_data=with_data, request = self.request)
        if with_data == 1:
            queryset = resource.get_queryset()
        else:
            queryset = resource.get_none()

        if not queryset.exists() and with_data == 1:
            messages.warning(request, "Aucune donnée à exporter.")
            return redirect(request.META.get("HTTP_REFERER"))

        dataset = resource.export(queryset=queryset)
        export_format = base_formats.XLSX()
        export_data = export_format.export_data(dataset)
        file_name = f"{model._meta.verbose_name_plural.lower()}{'' if with_data else '-modele'}-{date.today().isoformat()}.xlsx"
        return HttpResponse(
            content=export_data,
            content_type=export_format.get_content_type(),
            headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
        )

"""@method_decorator([require_http_methods(["GET"])], name="get")
class ExportView(View):
    def get(self, request, model_name: str, with_data=1, *args, **kwargs):
        # model_name : <app_label>.<model_name>
        try:
            model = apps.get_model(model_name)
        except Exception:
            messages.error(request, "Impossible d'exporter cette table.")
            return redirect(request.META.get("HTTP_REFERER"))

        try:
            resource = ie_resources.modelresource_factory(
                model=model, resource_class=resource_classes[model.__name__]
            )
        except:
            resource = ie_resources.modelresource_factory(
                model=model, resource_class=resource_classes["default"]
            )

        if not resource:
            messages.error(request, "Impossible d'exporter les données de cette table.")
            return redirect(request.META.get("HTTP_REFERER"))

        resource = resource(with_data=with_data)
        if with_data == 1:
            queryset = resource.get_queryset()
        else:
            queryset = resource.get_none()

        if not queryset.exists() and with_data == 1:
            messages.warning(request, "Aucune donnée à importer.")
            return redirect(request.META.get("HTTP_REFERER"))

        dataset = resource.export(queryset=queryset)
        file_name = f"{model._meta.verbose_name_plural.lower()}{'' if with_data else '-modele' }-{date.today().isoformat()}.xlsx"
        return HttpResponse(
            content=dataset.xlsx,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={f"Content-Disposition": f'attachment; filename="{file_name}"'},
        )"""


class ImportView(ie_mixins.BaseImportMixin, FormView):
    form_class = ie_forms.ImportForm
    confirm_form_class = ie_forms.ConfirmImportForm
    template_name = "import.html"

    def dispatch(self, request, *args, **kwargs):
        model_name = self.kwargs.get("model_name")
        print(model_name)

        try:
            model = apps.get_model(model_name)
        except Exception:
            messages.error(self.request, "Impossible d'importer cette table.")
            return redirect(self.request.META.get("HTTP_REFERER"))

        try:
            resource = ie_resources.modelresource_factory(
                model=model, resource_class=resource_classes[model.__name__]
            )
        except:
            resource = ie_resources.modelresource_factory(
                model=model, resource_class=resource_classes["default"]
            )

        if not resource:
            messages.error(
                self.request, "Impossible d'exporter les données de cette table."
            )
            return redirect(self.request.META.get("HTTP_REFERER"))

        self.model = model
        self.resource = resource()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["model_name"] = self.model._meta.label_lower
        context["fields_list"] = [
            (
                resource.get_display_name(),
                [f.column_name for f in resource.get_user_visible_fields()],
            )
            for resource in [self.resource]
        ]
        return context

    def write_to_tmp_storage(self, import_file, input_format):
        encoding = None

        tmp_storage = ie_tmp_storages.TempFolderStorage(
            encoding=encoding, read_mode=input_format.get_read_mode()
        )
        data = bytes()
        for chunk in import_file.chunks():
            data += chunk

        # if tmp_storage_cls == MediaStorage and not input_format.is_binary():
        #     data = data.decode(self.from_encoding)

        tmp_storage.save(data)
        return tmp_storage
    def get_import_resources(self):
        return [self.resource]
    
    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(self.get_import_formats(), self.get_import_resources(), **self.get_form_kwargs())

    """def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(self.get_import_formats(), **self.get_form_kwargs())"""

    def get_success_url(self):
        model_name = self.kwargs.get("model_name")
        return reverse(f"app:import-view", kwargs={"model_name": model_name})

    def form_valid(self, form):
        import_formats = self.get_import_formats()

        import_file = form.cleaned_data["import_file"]
        input_format = import_formats[int(form.cleaned_data["format"])]()

        dataset = Dataset()
        imported_data = dataset.load(import_file)

        result: ie_results.Result = self.resource.import_data(
            imported_data,
            collect_failed_rows=True,
            dry_run=True,
            rollback_on_validation_errors=True,
            use_transactions=True,
        )

        tmp_storage = self.write_to_tmp_storage(import_file, input_format)
        import_file.tmp_storage_name = tmp_storage.name
        context = self.get_context_data()

        if not result.has_errors() and not result.has_validation_errors():
            kwargs = {
                "data": self.request.POST or None,
                "files": self.request.FILES or None,
                "initial": {
                    "import_file_name": import_file.tmp_storage_name,
                    "original_file_name": import_file.name,
                    "input_format": form.cleaned_data["format"],
                    "resource": form.cleaned_data.get("resource", ""),
                },
            }
            context["confirm_form"] = ie_forms.ConfirmImportForm(**kwargs)

        context["result"] = result
        context["title"] = "Import"
        context["form"] = form
        context["opts"] = self.model._meta

        return render(self.request, self.get_template_names(), context=context)


"""class ConfirmImportView(mixins.BaseImportMixin, FormView):
    form_class = ie_forms.ConfirmImportForm

    def get_import_data_kwargs(self, request, *args, **kwargs):
        
        #Prepare kwargs for import_data.
        
        form = kwargs.get("form")
        if form:
            kwargs.pop("form")
            return kwargs
        return {}

    def form_valid(self, form):
        model_name = self.kwargs.get("model_name")

        try:
            model = apps.get_model(model_name)
        except Exception:
            messages.error(self.request, "Impossible d'exporter cette table.")
            return redirect(self.request.META.get("HTTP_REFERER"))

        try:
            resource = ie_resources.modelresource_factory(
                model=model, resource_class=resource_classes[model.__name__]
            )
        except:
            resource = ie_resources.modelresource_factory(
                model=model, resource_class=resource_classes["default"]
            )

        if not resource:
            messages.error(
                self.request, "Impossible d'exporter les données de cette table."
            )
            return redirect(self.request.META.get("HTTP_REFERER"))

        resource = resource()
        import_formats = self.get_import_formats()
        input_format = import_formats[int(form.cleaned_data["input_format"])](
            encoding=None
        )
        encoding = None
        tmp_storage = tmp_storages.TempFolderStorage(
            name=form.cleaned_data["import_file_name"],
            encoding=encoding,
            read_mode=input_format.get_read_mode(),
        )

        data = tmp_storage.read()
        dataset = input_format.create_dataset(data)

        result: results.Result = resource.import_data(
            dataset,
            collect_failed_rows=True,
            dry_run=False,
            rollback_on_validation_errors=True,
            use_transactions=True,
            file_name=form.cleaned_data.get("original_file_name"),
            user=self.request.user,
            **self.kwargs,
        )

        # for k, errors in result.row_errors():
        #     print(k, [error.error for error in errors])

        tmp_storage.remove()

        if not result.has_errors() and not result.has_validation_errors():
            messages.success(
                self.request,
                f"{model._meta.verbose_name_plural} importé(e)s avec succès.",
            )
        else:
            if result.has_errors():
                messages.error(
                    self.request,
                    "|".join(
                        [
                            "\t".join([str(error.error) for error in errors])
                            for k, errors in result.row_errors()
                        ]
                    ),
                )
            if result.has_validation_errors():
                messages.error(
                    self.request,
                    "|".join(
                        [
                            "\t".join([str(value) for value in error.values])
                            for error in result.invalid_rows
                        ]
                    ),
                )
                messages.error(
                    self.request,
                    "|".join([str(error.error_dict) for error in result.invalid_rows]),
                )

        return redirect("/")"""



class ConfirmImportView(ie_mixins.BaseImportMixin, FormView):
    form_class = ie_forms.ConfirmImportForm
    template_name = "ie_app/confirm_import.html"
    def get_import_data_kwargs(self, request, *args, **kwargs):
        """
        Prepare kwargs for import_data.
        """
        form = kwargs.get("form")
        if form:
            kwargs.pop("form")
            return kwargs
        return {}

    def form_valid(self, form):
        model_name = self.kwargs.get("model_name")

        try:
            model = apps.get_model(model_name)
        except Exception:
            messages.error(self.request, "Impossible d'exporter cette table.")
            return redirect(self.request.META.get("HTTP_REFERER"))

        try:
            resource = ie_resources.modelresource_factory(
                model=model, resource_class=resource_classes[model.__name__]
            )
        except:
            resource = ie_resources.modelresource_factory(
                model=model, resource_class=resource_classes["default"]
            )

        if not resource:
            messages.error(
                self.request, "Impossible d'exporter les données de cette table."
            )
            return redirect(self.request.META.get("HTTP_REFERER"))

        resource = resource()
        import_formats = self.get_import_formats()
        input_format = import_formats[int(form.cleaned_data["format"])](encoding=None)
        encoding = None
        tmp_storage = ie_tmp_storages.TempFolderStorage(
            name=form.cleaned_data["import_file_name"],
            encoding=encoding,
            read_mode=input_format.get_read_mode(),
        )

        data = tmp_storage.read()
        dataset = input_format.create_dataset(data)

        result: ie_results.Result = resource.import_data(
            dataset,
            collect_failed_rows=True,
            dry_run=False,
            rollback_on_validation_errors=True,
            use_transactions=True,
            file_name=form.cleaned_data.get("original_file_name"),
            user=self.request.user,
            **self.kwargs,
        )

        # for k, errors in result.row_errors():
        #     print(k, [error.error for error in errors])

        tmp_storage.remove()

        if not result.has_errors() and not result.has_validation_errors():
            messages.success(
                self.request,
                f"{model._meta.verbose_name_plural} importé(e)s avec succès.",
            )
        else:
            if result.has_errors():
                messages.error(
                    self.request,
                    "|".join(
                        [
                            "\t".join([str(error.error) for error in errors])
                            for k, errors in result.row_errors()
                        ]
                    ),
                )
            if result.has_validation_errors():
                messages.error(
                    self.request,
                    "|".join(
                        [
                            "\t".join([str(value) for value in error.values])
                            for error in result.invalid_rows
                        ]
                    ),
                )
                messages.error(
                    self.request,
                    "|".join([str(error.error_dict) for error in result.invalid_rows]),
                )

        return redirect("/")
    



class SomeImportView(ie_mixins.BaseImportMixin, FormView):
    form_class = SomeImportForm()
    confirm_form_class = ie_forms.ConfirmImportForm

    def form_valid(self, form):
        import_file = form.cleaned_data['import_file']
        input_format = form.cleaned_data['format']
        
        kwargs = {
            'initial': {
                'import_file_name': import_file.name,
                'original_file_name': import_file.name,
                'format': input_format,
                # Ajoutez d'autres champs nécessaires
            }
        }
        confirm_form = self.confirm_form_class(**kwargs)
        return render(self.request, 'import.html', {'confirm_form': confirm_form})

    def get_import_formats(self):
        return [base_formats.XLSX, base_formats.CSV, base_formats.JSON]  # Exemples de formats
