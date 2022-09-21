import nox

nox.options.reuse_existing_virtualenvs = True


@nox.session
def typing(session):
    session.install("requests")
    session.install("mypy", "types-requests")
    session.run("mypy", "create_singularities")
