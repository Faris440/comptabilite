from django.conf import settings
from formset.richtext import controls
from model_utils.choices import Choices
from formset.fields import Activator
from formset.renderers import ButtonVariant
from formset.widgets import Button

hostname = getattr(settings, "CUSTOM_HOST_NAME", None)


MIN_LENGTH = 50
MEDIUM_LENGTH = 100
LONG_LENGTH = 250
BIG_LENGTH = 400

OPTIONS_ICONS_SIZE = "16"
SIDEBAR_ICONS_SIZE = "16"
HEADER_ICONS_SIZE = "20"

TEXTAREA = {
    "rows": 4,
    "cols": 50,
    "maxlength": 5000,
    "placeholder": "une description …",
}


ORGANIZATION_TYPES = [
    ('government', 'Gouvernement'),
    ('private', 'Privé'),
    ('ngo', 'ONG'),
    ('other', 'Autre'),
]


control_elements = [
    controls.Heading([1, 2, 3, 4, 5, 6]),
    controls.Bold(),
    controls.Italic(),
    controls.Underline(),
    controls.Separator(),
    controls.Blockquote(),
    controls.TextColor(["rgb(212, 0, 0)", "rgb(0, 212, 0)", "rgb(0, 0, 212)"]),
    controls.Separator(),
    controls.BulletList(),
    controls.OrderedList(),
    controls.Separator(),
    controls.TextIndent(),
    controls.TextIndent("outdent"),
    controls.TextMargin("increase"),
    controls.TextMargin("decrease"),
    controls.TextAlign(["left", "center", "right"]),
    controls.Separator(),
    # controls.Link(),
    controls.HorizontalRule(),
    controls.Subscript(),
    controls.Superscript(),
    controls.Separator(),
    controls.ClearFormat(),
    controls.Redo(),
    controls.Undo(),
]

STATUS = Choices(
    ("0", "to_validate", "à valider"),
    ("1", "ongoing", "en cours"),
    ("2", "suspended", "suspendue"),
    ("3", "completed", "terminée"),
)



STATUS_CLOSE =Choices(
    ('active', 'Active'),
    ('extended', 'Prolongée'),
    ('closed', 'Clôturée'),
    ('disabled', 'Désactivée')
)

STATUS_PUNITION =Choices(
    ('active', 'Active'),
    ('extended', 'Prolongée'),
    ('end', 'Terminée'),
    ('closed', 'Annulée'),
)


DURATION_TYPE_CHOICES = Choices (
    ('day', 'Jour'),
    ('week', 'Semaine'),
    ('month', 'Mois'),
    ('year', 'Année'),
    ('indefinite', 'Indéfini'),
)


RETIREMENT_TYPE_CHOICES = [
    ("standard", "Standard"),
    ("Anticipée", "Anticipée"),
    ("Pour Invalidité", "Pour Invalidité"),
]


submit = Activator(
    label="Submit",
    widget=Button(
        action="spinner -> submit -> okay(2000) -> proceed !~ bummer(10000) -> scrollToError",
        button_variant=ButtonVariant.SUCCESS,
        # icon_path="formset/icons/send.svg",
    ),
)


reset = Activator(
    label="Annuler",
    widget=Button(
        action="spinner -> reset -> proceed('{{request.META.HTTP_REFERER}}')",
        button_variant=ButtonVariant.WARNING,
        # icon_path="formset/icons/send.svg",
    ),
)


reload = Activator(
    label="Enregistrer et continuer",
    widget=Button(
        action="spinner -> submit -> okay(2000) -> proceed -> reload !~ bummer(10000)",
        button_variant=ButtonVariant.PRIMARY,
        # icon_path="formset/icons/send.svg",
    ),
)
