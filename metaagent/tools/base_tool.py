import inspect
import logging
import re
from abc import ABCMeta
from copy import deepcopy
from functools import wraps
from typing import Callable, Iterable, Optional, Type, get_args, get_origin

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

from griffe import Docstring
from griffe import DocstringSectionKind


def tool_api(
    func: Optional[Callable] = None,
    *,
    explode_return: bool = False,
    returns_named_value: bool = False,
    include_arguments: Optional[Iterable[str]] = None,
    exclude_arguments: Optional[Iterable[str]] = None,
    **kwargs,
):
    """Turn functions into tools. It will parse typehints as well as docstrings
    to build the tool description and attach it to functions via an attribute
    ``api_description``.

    Examples:

        .. code-block:: python

            # typehints has higher priority than docstrings
            from typing import Annotated

            @tool_api
            def add(a: Annotated[int, 'augend'], b: Annotated[int, 'addend'] = 1):
                '''Add operation

                Args:
                    x (int): a
                    y (int): b
                '''
                return a + b

            print(add.api_description)

    Args:
        func (Optional[Callable]): function to decorate. Defaults to ``None``.
        explode_return (bool): whether to flatten the dictionary or tuple return
            as the ``return_data`` field. When enabled, it is recommended to
            annotate the member in docstrings. Defaults to ``False``.

            .. code-block:: python

                @tool_api(explode_return=True)
                def foo(a, b):
                    '''A simple function

                    Args:
                        a (int): a
                        b (int): b

                    Returns:
                        dict: information of inputs
                            * x: value of a
                            * y: value of b
                    '''
                    return {'x': a, 'y': b}

                print(foo.api_description)

        returns_named_value (bool): whether to parse ``thing: Description`` in
            returns sections as a name and description, rather than a type and
            description. When true, type must be wrapped in parentheses:
            ``(int): Description``. When false, parentheses are optional but
            the items cannot be named: ``int: Description``. Defaults to ``False``.

    Returns:
        Callable: wrapped function or partial decorator

    Important:
        ``return_data`` field will be added to ``api_description`` only
        when ``explode_return`` or ``returns_named_value`` is enabled.
    """
    if include_arguments is None:
        exclude_arguments = exclude_arguments or set()
        if isinstance(exclude_arguments, str):
            exclude_arguments = {exclude_arguments}
        elif not isinstance(exclude_arguments, set):
            exclude_arguments = set(exclude_arguments)
        if 'self' not in exclude_arguments:
            exclude_arguments.add('self')
    else:
        include_arguments = {include_arguments} if isinstance(include_arguments, str) else set(include_arguments)

    def _detect_type(string):
        field_type = 'STRING'
        if 'list' in string:
            field_type = 'Array'
        elif 'str' not in string:
            if 'float' in string:
                field_type = 'FLOAT'
            elif 'int' in string:
                field_type = 'NUMBER'
            elif 'bool' in string:
                field_type = 'BOOLEAN'
        return field_type

    def _explode(desc):
        kvs = []
        desc = '\nArgs:\n' + '\n'.join(
            ['    ' + item.lstrip(' -+*#.') for item in desc.split('\n')[1:] if item.strip()]
        )
        docs = Docstring(desc).parse('google')
        if not docs:
            return kvs
        if docs[0].kind is DocstringSectionKind.parameters:
            for d in docs[0].value:
                d = d.as_dict()
                if not d['annotation']:
                    d.pop('annotation')
                else:
                    d['type'] = _detect_type(d.pop('annotation').lower())
                kvs.append(d)
        return kvs

    def _parse_tool(function):
        # remove rst syntax
        docs = Docstring(re.sub(':(.+?):`(.+?)`', '\\2', function.__doc__ or '')).parse(
            'google', returns_named_value=returns_named_value, **kwargs
        )
        desc = dict(
            name=function.__name__,
            description=docs[0].value if docs[0].kind is DocstringSectionKind.text else '',
            parameters=[],
            required=[],
        )
        args_doc, returns_doc = {}, []
        for doc in docs:
            if doc.kind is DocstringSectionKind.parameters:
                for d in doc.value:
                    d = d.as_dict()
                    d['type'] = _detect_type(d.pop('annotation').lower())
                    args_doc[d['name']] = d
            if doc.kind is DocstringSectionKind.returns:
                for d in doc.value:
                    d = d.as_dict()
                    if not d['name']:
                        d.pop('name')
                    if not d['annotation']:
                        d.pop('annotation')
                    else:
                        d['type'] = _detect_type(d.pop('annotation').lower())
                    returns_doc.append(d)

        sig = inspect.signature(function)
        for name, param in sig.parameters.items():
            if name in exclude_arguments if include_arguments is None else name not in include_arguments:
                continue
            parameter = dict(
                name=param.name, type='STRING', description=args_doc.get(param.name, {}).get('description', '')
            )
            annotation = param.annotation
            if annotation is inspect.Signature.empty:
                parameter['type'] = args_doc.get(param.name, {}).get('type', 'STRING')
            else:
                if get_origin(annotation) is Annotated:
                    annotation, info = get_args(annotation)
                    if info:
                        parameter['description'] = info
                while get_origin(annotation):
                    annotation = get_args(annotation)
                parameter['type'] = _detect_type(str(annotation))
            desc['parameters'].append(parameter)
            if param.default is inspect.Signature.empty:
                desc['required'].append(param.name)

        return_data = []
        if explode_return:
            return_data = _explode(returns_doc[0]['description'])
        elif returns_named_value:
            return_data = returns_doc
        if return_data:
            desc['return_data'] = return_data
        return desc

    if callable(func):

        if inspect.iscoroutinefunction(func):

            @wraps(func)
            async def wrapper(self, *args, **kwargs):
                return await func(self, *args, **kwargs)

        else:

            @wraps(func)
            def wrapper(self, *args, **kwargs):
                return func(self, *args, **kwargs)

        wrapper.api_description = _parse_tool(func)
        return wrapper

    def decorate(func):

        if inspect.iscoroutinefunction(func):

            @wraps(func)
            async def wrapper(self, *args, **kwargs):
                return await func(self, *args, **kwargs)

        else:

            @wraps(func)
            def wrapper(self, *args, **kwargs):
                return func(self, *args, **kwargs)

        wrapper.api_description = _parse_tool(func)
        return wrapper

    return decorate


class ToolMeta(ABCMeta):
    """Metaclass of tools."""

    def __new__(mcs, name, base, attrs):
        is_toolkit, tool_desc = True, dict(
            name=name, description=Docstring(attrs.get('__doc__', '')).parse('google')[0].value
        )
        for key, value in attrs.items():
            if callable(value) and hasattr(value, 'api_description'):
                api_desc = getattr(value, 'api_description')
                if key == 'run':
                    tool_desc['parameters'] = api_desc['parameters']
                    tool_desc['required'] = api_desc['required']
                    if api_desc['description']:
                        tool_desc['description'] = api_desc['description']
                    if api_desc.get('return_data'):
                        tool_desc['return_data'] = api_desc['return_data']
                    is_toolkit = False
                else:
                    tool_desc.setdefault('api_list', []).append(api_desc)
        if not is_toolkit and 'api_list' in tool_desc:
            raise KeyError('`run` and other tool APIs can not be implemented ' 'at the same time')
        if is_toolkit and 'api_list' not in tool_desc:
            is_toolkit = False
            if callable(attrs.get('run')):
                run_api = tool_api(attrs['run'])
                api_desc = run_api.api_description
                tool_desc['parameters'] = api_desc['parameters']
                tool_desc['required'] = api_desc['required']
                if api_desc['description']:
                    tool_desc['description'] = api_desc['description']
                if api_desc.get('return_data'):
                    tool_desc['return_data'] = api_desc['return_data']
                attrs['run'] = run_api
            else:
                tool_desc['parameters'], tool_desc['required'] = [], []
        attrs['_is_toolkit'] = is_toolkit
        attrs['__tool_description__'] = tool_desc
        return super().__new__(mcs, name, base, attrs)