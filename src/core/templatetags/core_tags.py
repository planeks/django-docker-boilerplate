from django import template
from django.utils.safestring import mark_safe
from django.conf import settings

register = template.Library()

# Debugging

@register.simple_tag
def debug_print(*values):
    if settings.DEBUG:
        print(*values)
        return values
    else:
        return ''


@register.simple_tag(takes_context=True)
def debug_context(context):
    if settings.DEBUG:
        print(context)
        return context
    else:
        return ''


# Settings

@register.simple_tag
def tabbli_version():
    return settings.TABBLI_VERSION


@register.simple_tag
def load_option(option, default=None):
    return getattr(settings, option, default)


@register.filter
def str_repr(value):
    return mark_safe(repr(value))


# Helpful tags and filters

@register.filter
def is_error_dict(value):
    return type(value) is dict and 'error' in value


@register.filter
def in_list(value, the_list):
    value = str(value)
    return value in the_list.split(',')


@register.filter
def filename(value):
    import os.path
    head, tail = os.path.split(value)
    return tail


@register.filter
def fileext(value):
    import os.path
    fn, file_extension = os.path.splitext(value)
    return file_extension


@register.filter
def make_range(value):
    return range(*[int(x) for x in value.split(',')])


@register.filter
def get_element(iterable, index):
    return iterable.get(index)


@register.filter
def remove_value(iterable, value):
    return [x for x in iterable if x != value]


@register.filter
def cast_elements(iterable, type_name):
    types = {
        'int': int,
        'float': float,
        'str': str,
    }
    return [types[type_name](x) for x in iterable]


@register.simple_tag
def set_element(iterable, index, value):
    iterable[index] = value
    return iterable


@register.filter
def index_element(iterable, index):
    return iterable[index]


@register.filter
def keys(iterable):
    return iterable.keys()


@register.filter
def get_attr(obj, attr):
    return getattr(obj, attr)


@register.filter
def to_int(obj):
    return int(obj)


@register.filter
def to_list(obj):
    return list(obj)


@register.filter
def to_set(obj):
    return set(obj)


@register.filter
def to_dict(obj):
    return dict(obj)


@register.filter
def ignore_none(value):
    return value or ''


@register.filter
def sort(iterable):
    return iterable.sort()


@register.filter
def sort_by_attr(iterable, attr):
    result = sorted(iterable, key=lambda x: getattr(x, attr))
    return result


@register.filter
def sort_by_key(iterable, key):
    result = sorted(iterable, key=lambda x: x[key])
    return result


@register.filter
def class_name(obj):
    return obj.__class__.__name__


@register.filter
def pretty_json(obj, indent=4):
    import json
    return json.dumps(obj, indent=indent)


@register.filter
def uikit_widget_css_class(field, extra_class=None):
    css_class = 'uk-input'
    widget_name = field.field.widget.__class__.__name__
    if widget_name == 'Select':
        css_class = 'uk-select'

    if extra_class is not None:
        css_class += ' %s' % extra_class
    return field.as_widget(attrs={"class": css_class})


@register.filter
def widget_css_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})


@register.filter
def widget_placeholder(field, value):
    return field.as_widget(attrs={"placeholder": value})


@register.simple_tag
def widget_attrs(field, **kwargs):
    return field.as_widget(attrs={k.replace('_', '-'): v for k, v in kwargs.items()})


@register.simple_tag
def widget_attrs_from_dict(field, kwargs):
    return field.as_widget(attrs={k.replace('_', '-'): v for k, v in kwargs.items()})


@register.filter
def markdown(text):
    import markdown
    return mark_safe(
        markdown.markdown(
            text,
            extensions=['smarty', 'nl2br'],
        ))


@register.filter
def subtract(value, arg):
    return value - arg


@register.filter
def add(value, arg):
    return value + arg


@register.filter
def divide(value, arg):
    return value / arg


@register.filter
def multiply(value, arg):
    return value * arg


@register.filter
def divide_and_trunc(value, arg):
    return int(value / arg)


@register.filter
def append_to_list(value, arg):
    return value.append(arg)


@register.simple_tag
def optional_url(url_name, *args, **kwargs):
    from django.urls import reverse, NoReverseMatch
    try:
        return reverse(url_name, args=args, kwargs=kwargs)
    except NoReverseMatch:
        return '#unknown-url'


@register.simple_tag
def url_with_optional_args(url_name, *args, **kwargs):
    from django.urls import reverse
    return reverse(
        url_name,
        args=[x for x in args if x],
        kwargs={k: v for k, v in kwargs.items() if v})


@register.filter
def beautify_comma_separation(value):
    if value is not None:
        return ', '.join([x.strip() for x in value.split(',') if x])
    return ''


@register.filter
def comma_separated_attrs(value, attr):
    return ','.join([getattr(x, attr) for x in value])


@register.filter
def is_today(value):
    from datetime import date
    return (date.today() - value.date()).days == 0


@register.filter
def is_yesterday(value):
    from datetime import date
    return (date.today() - value.date()).days == 1


@register.filter
def is_checkbox(field):
    from django.forms import CheckboxInput
    return isinstance(field.field.widget, CheckboxInput)


@register.filter
def is_radio_select(field):
    from django.forms import RadioSelect
    return isinstance(field.field.widget, RadioSelect)


@register.filter
def is_select(field):
    from django.forms import Select
    return isinstance(field.field.widget, Select)


@register.filter
def is_checkbox_select_multiple(field):
    from django.forms import CheckboxSelectMultiple
    return isinstance(field.field.widget, CheckboxSelectMultiple)


@register.filter
def is_file_input(field):
    from django.forms import FileInput
    return isinstance(field.field.widget, FileInput)


@register.filter
def widget_class_name(field):
    return field.field.widget.__class__.__name__


@register.filter
def weight(value):
    return '%.1f kg' % value


@register.simple_tag
def create_list(*args):
    return args


@register.simple_tag
def create_dict(**kwargs):
    return kwargs


@register.simple_tag
def save(value):
    return value


@register.simple_tag(takes_context=True)
def update_context_attr(context, attr, value):
    context[attr] = value
    return value


@register.simple_tag
def create_list():
    return list()


@register.simple_tag
def create_dict():
    return dict()


@register.filter
def attrs_list(obj):
    return dir(obj)


@register.filter
def inspect(obj):
    attrs = dir(obj)
    result = dict()
    for attr in attrs:
        result[attr] = getattr(obj, attr)
    return result


@register.simple_tag
def split_str(value, delimiter=','):
    return value.split(delimiter)


@register.filter
def strip_items(iterable):
    return [x.strip() for x in iterable]


@register.filter
def join_list(iterable, delimiter=','):
    return delimiter.join([str(x) for x in iterable])


@register.filter
def format_str(value, format_='%s'):
    return format_ % value


@register.filter
def money(value, template_name='price_template'):
    if value is None or value == '':
        value = 0.0
    b_value = '{:,}'.format(int(value)).replace(',', ' ')

    _template = '<span class="money" data-value="%s" data-currency="%s">%s</span>'
    currency_code = getattr(settings, 'DEFAULT_CURRENCY', 'default')

    chunks = template_name.split(',')
    if len(chunks) == 2:
        currency_code, template_name = chunks[0], chunks[1]
    elif len(chunks) == 1:
        if template_name in settings.CURRENCIES:
            currency_code = template_name
            template_name = 'price_template'

    if hasattr(settings, 'CURRENCIES'):
        currency_config = settings.CURRENCIES.get(currency_code)
        return mark_safe(
            _template % (
                value,
                currency_code,
                currency_config.get(template_name, '%s') % b_value)
            )
    else:
        return _template % (value, currency_code, b_value)


@register.filter
def thousands_separator(value, separator=' '):
    return '{:,}'.format(value).replace(',', separator)


@register.simple_tag
def set_query_parameter(url, param_name, param_value):
    from urllib.parse import (
        urlencode,
        parse_qs,
        urlsplit,
        urlunsplit,
    )
    scheme, netloc, path, query_string, fragment = urlsplit(url)
    query_params = parse_qs(query_string)
    if param_value:
        query_params[param_name] = [param_value]
    elif param_name in query_params:
        del query_params[param_name]
    new_query_string = urlencode(query_params, doseq=True)
    return urlunsplit((scheme, netloc, path, new_query_string, fragment))


@register.filter
def get_query_parameter(url, param_name):
    from urllib.parse import (
        urlencode,
        parse_qs,
        urlsplit,
        urlunsplit,
    )
    scheme, netloc, path, query_string, fragment = urlsplit(url)
    query_params = parse_qs(query_string)
    return ','.join(query_params.get(param_name))


@register.filter(takes_context=True)
def build_absolute_uri(context, location):
    return context['request'].build_absolute_uri(location)


@register.filter
def call_function(callable, arg):
    return callable(arg)

# Querysets

@register.filter
def order_by(queryset, values):
    values_attrs = values.split(',')
    return queryset.order_by(*values_attrs)


@register.filter
def select_related(queryset, value):
    return queryset.select_related(value)


@register.filter
def prefetch_related(queryset, value):
    return queryset.prefetch_related(value)


@register.filter
def distinct(queryset):
    return queryset.distinct()


@register.simple_tag
def prepare_query_object(logic='AND', **kwargs):
    from django.db.models import Q
    query = None
    for k,v in kwargs.items():
        if query is None:
            query = Q(**{k: v})
        else:
            if logic == 'AND':
                query &= Q(**{k: v})
            elif logic == 'OR':
                query |= Q(**{k: v})
    return query


@register.filter
def filter_queryset(queryset, query):
    return queryset.filter(query)


@register.simple_tag
def exclude_from_str(value, *args):
    words = value.split()
    return ' '.join([x for x in words if x not in args])


@register.filter
def exclude_from_queryset(queryset, query):
    return queryset.exclude(query)


@register.filter
def endswith(origin, value):
    return origin.endswith(value)


@register.filter
def startswith(origin, value):
    if type(origin) is str:
        return origin.startswith(value)
    return False


@register.filter
def str_prefix(origin, value):
    return f'{value}{origin}'


# Liquid compatibility


@register.filter
def append(value, arg):
    """Appends characters to a string.
    Input:
        {{ 'sales' | append: '.jpg' }}
    Output:
        sales.jpg
    """
    return value + arg


@register.filter
def camelcase(value):
    """Converts a string into CamelCase.
    Input:
        {{ 'coming-soon' | camelcase }}
    Output:
        ComingSoon
    """
    chunks = value.split('-')
    return ''.join([x.title() for x in chunks])


@register.filter
def capitalize(value):
    """Capitalizes the first word in a string.
    Input:
        {{ 'capitalize me' | capitalize }}
    Output:
        Capitalize me
    """
    return value.title()


@register.filter
def downcase(value):
    """Converts a string into lowercase.
    Input
        {{ 'UPPERCASE' | downcase }}
    Output
        uppercase
    """
    return value.lower()


@register.filter
def escape(value):
    """Escapes a string.
    Input
        {{ "<p>test</p>" | escape }}
    Output
         <!-- The <p> tags are not rendered -->
        <p>test</p>"""
    import html
    return html.escape(value)


@register.filter
def upcase(value):
    return value.upper()


@register.filter
def encodeobj(obj):
    import pickle
    import base64
    return mark_safe(base64.b64encode(pickle.dumps(obj)).decode('ascii'))


@register.filter
def is_hidden_input(field):
    from django.forms import HiddenInput
    return isinstance(field.field.widget, HiddenInput)


# capture tag

@register.tag(name='capture')
def do_capture(parser, token):
    """
    Capture the contents of a tag output.
    Usage:
    .. code-block:: html+django
        {% capture %}..{% endcapture %}                    # output in {{ capture }}
        {% capture silent %}..{% endcapture %}             # output in {{ capture }} only
        {% capture as varname %}..{% endcapture %}         # output in {{ varname }}
        {% capture as varname silent %}..{% endcapture %}  # output in {{ varname }} only
    For example:
    .. code-block:: html+django
        {# Allow templates to override the page title/description #}
        <meta name="description" content="{% capture as meta_description %}{% block meta-description %}{% endblock %}{% endcapture %}" />
        <title>{% capture as meta_title %}{% block meta-title %}Untitled{% endblock %}{% endcapture %}</title>
        {# copy the values to the Social Media meta tags #}
        <meta property="og:description" content="{% block og-description %}{{ meta_description }}{% endblock %}" />
        <meta name="twitter:title" content="{% block twitter-title %}{{ meta_title }}{% endblock %}" />
    """
    bits = token.split_contents()

    # tokens
    t_as = 'as'
    t_silent = 'silent'
    var = 'capture'
    silent = False

    num_bits = len(bits)
    if len(bits) > 4:
        raise template.TemplateSyntaxError("'capture' node supports '[as variable] [silent]' parameters.")
    elif num_bits == 4:
        t_name, t_as, var, t_silent = bits
        silent = True
    elif num_bits == 3:
        t_name, t_as, var = bits
    elif num_bits == 2:
        t_name, t_silent = bits
        silent = True
    else:
        var = 'capture'
        silent = False

    if t_silent != 'silent' or t_as != 'as':
        raise template.TemplateSyntaxError("'capture' node expects 'as variable' or 'silent' syntax.")

    nodelist = parser.parse(('endcapture',))
    parser.delete_first_token()
    return CaptureNode(nodelist, var, silent)


class CaptureNode(template.Node):
    def __init__(self, nodelist, varname, silent):
        self.nodelist = nodelist
        self.varname = varname
        self.silent = silent

    def render(self, context):
        output = self.nodelist.render(context)
        context[self.varname] = output
        if self.silent:
            return ''
        else:
            return output
