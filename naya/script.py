def make_shell(init_func=None, banner=None, use_bpython=True):
    """
    Returns an action callback that spawns a new interactive
    python shell.
    """
    if banner is None:
        banner = 'Interactive Werkzeug Shell'
    if init_func is None:
        init_func = dict

    def action(bpython=use_bpython):
        """Start a new interactive python session."""
        namespace = init_func()

        if use_bpython:
            try:
                import bpython
            except ImportError:
                pass
            else:
                bpython.embed(locals_=namespace, banner=banner)
                return

        from code import interact
        interact(banner, local=namespace)
    return action
