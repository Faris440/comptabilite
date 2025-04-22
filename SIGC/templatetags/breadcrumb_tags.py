from django import template
from django.urls import resolve
from django.utils.text import slugify
from django.utils.html import format_html
from django.urls import reverse

register = template.Library()

@register.inclusion_tag('components/breadcrumb.html', takes_context=True)
def auto_breadcrumb(context, custom_title=None):
    request = context['request']
    path = request.path
    current_view = resolve(path)

    segments = [seg for seg in path.strip('/').split('/') if seg]

    breadcrumb_items = []
    url_accum = ''
    for seg in segments:
        url_accum += '/' + seg
        name = seg.replace('-', ' ').replace('_', ' ').capitalize()
        breadcrumb_items.append({'name': name, 'url': url_accum})

    # Marquer le dernier comme actif (sans URL)
    if breadcrumb_items:
        breadcrumb_items[-1]['url'] = ''

    title = custom_title or breadcrumb_items[-1]['name'] if breadcrumb_items else 'Accueil'

    return {
        'title': title,
        'breadcrumb_items': breadcrumb_items
    }
