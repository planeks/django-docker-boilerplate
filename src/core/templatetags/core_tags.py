from django import template
from django.utils.safestring import mark_safe
from django.conf import settings

register = template.Library()

# Debugging

@register.simple_tag
def debug_print(*values):
    """
    Prints the values if DEBUG is set to True in settings.
    """
    if settings.DEBUG:
        print(*values)
        return values
    else:
        return ''


@register.simple_tag(takes_context=True)
def debug_context(context):
    """
    Prints the context if DEBUG is set to True in settings.
    """
    if settings.DEBUG:
        print(context)
        return context
    else:
        return ''


# Settings

@register.simple_tag
def load_option(option, default=None):
    """ Returns the value of a setting variable.

    Example: {% load_option 'DEBUG' as IS_DEBUG %}
    Sets the value IS_DEBUG as True if DEBUG is set to True in settings.
    """
    return getattr(settings, option, default)


@register.filter
def str_repr(value):
    """ Returns the string representation of a value without escaping."""
    return mark_safe(repr(value))


# Helpful tags and filters

@register.filter
def is_error_dict(value):
    """ Returns True if the value is a dictionary and contains an 'error' key."""
    return type(value) is dict and 'error' in value


@register.filter
def in_list(value, the_list):
    """ Returns True if the value is in the list.
    The list is a string of comma-separated values."""
    value = str(value)
    return value in the_list.split(',')


@register.filter
def filename(value):
    """ Returns the filename from a path.

    Example: {{ '/home/user/file.txt' | filename }} returns 'file.txt'
    """
    import os.path
    head, tail = os.path.split(value)
    return tail


@register.filter
def fileext(value):
    """ Returns the extension of a file.

    Example: {{ '/home/user/file.txt' | fileext }} returns '.txt'
    """
    import os.path
    fn, file_extension = os.path.splitext(value)
    return file_extension


@register.filter
def make_range(value):
    """ Returns a range object with attributes from the comma-separated string.

    Example: {{ '1,10,2' | make_range }} returns range(1, 10, 2)
    """
    return range(*[int(x) for x in value.split(',')])


@register.filter
def get_element(iterable, index):
    """ Returns the element at the given index in the iterable."""
    return iterable.get(index)


@register.filter
def remove_value(iterable, value):
    """ Returns the list excluding the given value."""
    return [x for x in iterable if x != value]


@register.filter
def cast_elements(iterable, type_name):
    """ Returns a list with elements casted to the given type.

    The next types are supported: int, float, str.
    """
    types = {
        'int': int,
        'float': float,
        'str': str,
    }
    return [types[type_name](x) for x in iterable]


@register.simple_tag
def set_element(iterable, index, value):
    """ Sets the element at the given index in the iterable."""
    iterable[index] = value
    return iterable


@register.filter
def index_element(iterable, index):
    """ Returns the element at the given index in the iterable."""
    return iterable[index]


@register.filter
def keys(iterable):
    """ Returns the keys of a dictionary."""
    return iterable.keys()


@register.filter
def get_attr(obj, attr):
    """ Returns the attribute of an object."""
    return getattr(obj, attr)


@register.filter
def to_int(obj):
    """ Returns the integer representation of an object."""
    return int(obj)


@register.filter
def to_list(obj):
    """ Returns the list representation of an object."""
    return list(obj)


@register.filter
def to_set(obj):
    """ Returns the set representation of an object."""
    return set(obj)


@register.filter
def to_dict(obj):
    return dict(obj)


@register.filter
def ignore_none(value):
    """ Returns the value if it's not None. Otherwise returns an empty string."""
    return value or ''


@register.filter
def sort(iterable):
    """ Returns the sorted iterable."""
    return sorted(iterable)


@register.filter
def sort_by_attr(iterable, attr):
    """ Returns the sorted iterable by the given attribute."""
    result = sorted(iterable, key=lambda x: getattr(x, attr))
    return result


@register.filter
def sort_by_key(iterable, key):
    """ Returns the sorted iterable by the given key."""
    result = sorted(iterable, key=lambda x: x[key])
    return result


@register.filter
def class_name(obj):
    """ Returns the class name of an object."""
    return obj.__class__.__name__


@register.filter
def pretty_json(obj, indent=4):
    """ Returns the pretty JSON representation of an object.
    You can specify the indent. Ny default it is 4.
    """
    import json
    return json.dumps(obj, indent=indent)


@register.filter
def widget_css_class(field, css_class):
    """ Adds a CSS class to a widget."""
    return field.as_widget(attrs={"class": css_class})


@register.filter
def widget_placeholder(field, value):
    """ Adds a placeholder to a widget."""
    return field.as_widget(attrs={"placeholder": value})


@register.simple_tag
def widget_attrs(field, **kwargs):
    """ Adds custom attributes to a widget."""
    return field.as_widget(attrs={k.replace('_', '-'): v for k, v in kwargs.items()})


@register.simple_tag
def widget_attrs_from_dict(field, kwargs):
    """ Adds custom attributes to a widget using the dictionary."""
    return field.as_widget(attrs={k.replace('_', '-'): v for k, v in kwargs.items()})


@register.filter
def markdown(text):
    """ Returns the HTML representation of a Markdown text.
    You can use the SmartyPants and nl2br extensions.
    """
    import markdown
    return mark_safe(
        markdown.markdown(
            text,
            extensions=['smarty', 'nl2br'],
        ))


@register.filter
def subtract(value, arg):
    """ Subtracts the arg from the value.

    Example: {{ 10 | subtract: 5 }} returns 5
    """
    return value - arg


@register.filter
def add(value, arg):
    """ Adds the arg to the value.

    Example: {{ 10 | add: 5 }} returns 15
    """
    return value + arg


@register.filter
def divide(value, arg):
    """ Divides the value by the arg.

    Example: {{ 10 | divide: 5 }} returns 2
    """
    return value / arg


@register.filter
def multiply(value, arg):
    """ Multiplies the value by the arg.

    Example: {{ 10 | multiply: 5 }} returns 50
    """
    return value * arg


@register.filter
def divide_and_trunc(value, arg):
    """ Divides the value by the arg and truncates the result.

    Example: {{ 10 | divide_and_trunc: 3 }} returns 3
    """
    return int(value / arg)


@register.filter
def append_to_list(value, arg):
    """ Appends the arg to the list."""
    return value.append(arg)


@register.simple_tag
def optional_url(url_name, *args, **kwargs):
    """ Returns the URL if it exists. Otherwise returns '#unknown-url'."""
    from django.urls import reverse, NoReverseMatch
    try:
        return reverse(url_name, args=args, kwargs=kwargs)
    except NoReverseMatch:
        return '#unknown-url'


@register.simple_tag
def url_with_optional_args(url_name, *args, **kwargs):
    """ Returns the URL with arguments if they are not empty."""
    from django.urls import reverse
    return reverse(
        url_name,
        args=[x for x in args if x],
        kwargs={k: v for k, v in kwargs.items() if v})


@register.filter
def beautify_comma_separation(value):
    """ Returns the comma-separated values in a human-readable format.

    Example: {{ 'a,b,c' | beautify_comma_separation }} returns 'a, b, c'
    """
    if value is not None:
        return ', '.join([x.strip() for x in value.split(',') if x])
    return ''


@register.filter
def comma_separated_attrs(value, attr):
    """ Returns the comma-separated values of the given attribute.

    Example: {{ users | comma_separated_attrs:'email' }} returns 'email1,email2,email3'
    """
    return ','.join([getattr(x, attr) for x in value])


@register.filter
def is_today(value):
    """ Returns True if the value is today's date."""
    from datetime import date
    return (date.today() - value.date()).days == 0


@register.filter
def is_yesterday(value):
    """ Returns True if the value is yesterday's date."""
    from datetime import date
    return (date.today() - value.date()).days == 1


@register.filter
def is_checkbox(field):
    """ Returns True if the field is a checkbox."""
    from django.forms import CheckboxInput
    return isinstance(field.field.widget, CheckboxInput)


@register.filter
def is_radio_select(field):
    """ Returns True if the field is a radio select."""
    from django.forms import RadioSelect
    return isinstance(field.field.widget, RadioSelect)


@register.filter
def is_select(field):
    """ Returns True if the field is a select."""
    from django.forms import Select
    return isinstance(field.field.widget, Select)


@register.filter
def is_checkbox_select_multiple(field):
    """ Returns True if the field is a multiple checkbox representation for the select."""
    from django.forms import CheckboxSelectMultiple
    return isinstance(field.field.widget, CheckboxSelectMultiple)


@register.filter
def is_file_input(field):
    """ Returns True if the field is a file input."""
    from django.forms import FileInput
    return isinstance(field.field.widget, FileInput)


@register.filter
def widget_class_name(field):
    """ Returns the class name of the field's widget."""
    return field.field.widget.__class__.__name__



@register.simple_tag
def create_list(*args):
    """ Creates the list with the given elements.

    Example: {% create_list 'a' 'b' 'c' as list %} creates the list ['a', 'b', 'c']
    """
    return args


@register.simple_tag
def create_dict(**kwargs):
    """ Creates the dictionary with the given key-value pairs.

    Example: {% create_dict a='1' b='2' c='3' as dict %} creates the dictionary {'a': '1', 'b': '2', 'c': '3'}
    """
    return kwargs


@register.simple_tag
def save(value):
    """ Returns the value. Uses if you need to save the value in a variable.

    Example: {% save 'a' as var %} creates the variable var with the value 'a'
    """
    return value


@register.simple_tag(takes_context=True)
def update_context_attr(context, attr, value):
    """ Updates the context with the given attribute and value."""
    context[attr] = value
    return value


@register.filter
def attrs_list(obj):
    """ Returns the list of attributes of an object. Calls the dir() function."""
    return dir(obj)


@register.filter
def inspect(obj):
    """ Returns the dictionary of attributes of an object and their values."""
    attrs = dir(obj)
    result = dict()
    for attr in attrs:
        result[attr] = getattr(obj, attr)
    return result


@register.simple_tag
def split_str(value, delimiter=','):
    """ Returns the list of values from the given string. Uses the split() function.

    Examples:
        {% split_str 'a,b,c' as list %} creates the list ['a', 'b', 'c']
        {% split_str 'a;b;c' ';' as list %} creates the list ['a', 'b', 'c']
    """
    return value.split(delimiter)


@register.filter
def strip_items(iterable):
    """ Returns the list of stripped values from the given iterable."""
    return [x.strip() for x in iterable]


@register.filter
def join_list(iterable, delimiter=','):
    """ Returns the string from the given list. Uses the join() function."""
    return delimiter.join([str(x) for x in iterable])


@register.filter
def format_str(value, format_='%s'):
    """ Returns the formatted string with the given format.

    Example: {{ 10 | format_str:'%d' }} returns '10'
    """
    return format_ % value


@register.filter
def thousands_separator(value, separator=' '):
    """ Returns the string with the thousands separator.

    Examples:
        {{ 1000000 | thousands_separator }} returns '1 000 000'
        {{ 1000000 | thousands_separator:',' }} returns '1,000,000'
    """
    return '{:,}'.format(value).replace(',', separator)


@register.simple_tag
def set_query_parameter(url, param_name, param_value):
    """ Sets the query parameter in the given URL.

    Examples:
        {% set_query_parameter request.get_full_path 'page' 1 %}
        {% set_query_parameter request.get_full_path 'page' 1 as new_url %}
    """
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
    """ Returns the query parameter from the given URL.

    Example: {{ request.get_full_path | get_query_parameter:'page' }}
    """
    from urllib.parse import (
        parse_qs,
        urlsplit,
    )
    scheme, netloc, path, query_string, fragment = urlsplit(url)
    query_params = parse_qs(query_string)
    return ','.join(query_params.get(param_name))


@register.filter(takes_context=True)
def build_absolute_uri(context, location):
    """ Returns the absolute URI for the given location including the schema.

    Example: {{ request.get_full_path | build_absolute_uri }}
    """
    return context['request'].build_absolute_uri(location)


@register.filter
def call_function(callable, arg):
    """ Calls the given function with the given argument.

    Example: {{ callable | call_function:arg }}
    """
    return callable(arg)

# Querysets

@register.filter
def order_by(queryset, values):
    """ Returns the ordered queryset by the given values.

    Example: {{ queryset | order_by:'-date_joined' }}
    """
    values_attrs = values.split(',')
    return queryset.order_by(*values_attrs)


@register.filter
def select_related(queryset, value):
    """ Returns the queryset with the given select_related value.

    Example: {{ queryset | select_related:'user' }}
    """
    return queryset.select_related(value)


@register.filter
def prefetch_related(queryset, value):
    """ Returns the queryset with the given prefetch_related value.

    Example: {{ queryset | prefetch_related:'user' }}
    """
    return queryset.prefetch_related(value)


@register.filter
def distinct(queryset):
    """ Returns the distinct queryset.

    Example: {{ queryset | distinct }}
    """
    return queryset.distinct()


@register.simple_tag
def prepare_query_object(logic='AND', **kwargs):
    """ Returns the Q object for the given kwargs.

    Example: {% prepare_query_object name='John' age=20 as query_obj %}
    """
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
    """ Returns the filtered queryset.

    Example: {{ queryset | filter_queryset:query_obj }}
    """
    return queryset.filter(query)


@register.simple_tag
def exclude_from_str(value, *args):
    """ Returns the string without the given words.

    Example: {% exclude_from_str 'a b c' 'b' 'c' as result %}
    """
    words = value.split()
    return ' '.join([x for x in words if x not in args])


@register.filter
def exclude_from_queryset(queryset, query):
    """ Returns the filtered queryset with inversed logic.

    Example: {{ queryset | exclude_from_queryset:query_obj }}
    """
    return queryset.exclude(query)


@register.filter
def endswith(origin, value):
    """ Returns True if the origin string ends with the given value.

    Example: {{ 'abc' | endswith:'c' }} returns True
    """
    return origin.endswith(value)


@register.filter
def startswith(origin, value):
    """ Returns True if the origin string starts with the given value.

    Example: {{ 'abc' | startswith:'a' }} returns True
    """
    if type(origin) is str:
        return origin.startswith(value)
    return False


@register.filter
def str_prefix(origin, value):
    """ Returns the origin string with the given value as a prefix.

    Example: {{ 'abc' | str_prefix:'a' }} returns 'aabc'
    """
    return f'{value}{origin}'


# Liquid compatibility (for reusing pieces of Shopify templates)


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
    """ Converts a string into uppercase."""
    return value.upper()


@register.filter
def encodeobj(obj):
    """ Returns the base64 encoded pickled object."""
    import pickle
    import base64
    return mark_safe(base64.b64encode(pickle.dumps(obj)).decode('ascii'))


@register.filter
def is_hidden_input(field):
    """ Returns True if the field is a hidden input."""
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
