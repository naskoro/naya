import jinja2


def markdown(value):
    try:
        from markdown import Markdown
        md = Markdown(extensions=['footnotes'])
    except ImportError:
        try:
            from markdown2 import Markdown
            md = Markdown(extras=['footnotes', 'code-friendly'])
        except ImportError:
            raise jinja2.TemplateError('Markdown is not installed!')

    return md.convert(value)


def rst(value):
    try:
        import docutils.core
    except ImportError:
        raise jinja2.TemplateError('docutils are not installed!')

    settings = {'footnote_references': 'superscript'}
    parts = docutils.core.publish_parts(source=value, writer_name='html',
                                        settings_overrides=settings)
    return parts['fragment']


def textile(value):
    try:
        import textile
    except ImportError:
        raise jinja2.TemplateError('textile is not installed!')

    return textile.textile(value)


all = dict((f.__name__, f) for f in [markdown, rst, textile])
