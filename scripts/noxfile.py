import nox

nox.options.reuse_existing_virtualenvs = True


@nox.session
def typing(session):
    session.install("requests")
    session.install("mypy", "types-requests")
    session.run("mypy", "create_singularities")


@nox.session
def test(session):
    session.install("click", "requests", "datalad", "pytest")
    session.run("pytest", "-v", "tests/test_create_singularities.py", *session.posargs)
