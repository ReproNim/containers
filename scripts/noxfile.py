import nox

nox.options.reuse_existing_virtualenvs = True


@nox.session
def typing(session):
    session.install("requests")
    session.install("mypy", "types-requests")
    session.run("mypy", "create_singularities")


@nox.session
def tests(session):
    session.install("requests", "datalad", "pytest", "click")
    session.run("pytest", "tests/test_create_singularities.py", "-v")
