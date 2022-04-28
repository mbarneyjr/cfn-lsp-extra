import nox
from nox_poetry import session


package = "cfn_lsp_extra"
python_versions = ["3.10", "3.9", "3.8", "3.7"]
nox.needs_version = ">= 2021.6.6"
nox.options.sessions = ("tests", "lint", "mypy", "coverage")


@session(python=python_versions)
def tests(session):
    session.install("pytest", ".")
    session.install("pytest-asyncio", ".")
    session.install("pytest-mock", ".")
    session.run("pytest", "-s", *session.posargs)


@session(python=python_versions)
def lint(session):
    session.install("flakeheaven")
    session.install("flake8-bugbear")
    session.run("flakeheaven", "lint", package)


@session(python=python_versions)
def mypy(session):
    session.install(".")
    session.install("mypy")
    session.run("mypy", package)


@session(python=python_versions)
def coverage(session):
    session.install("pytest", ".")
    session.install("pytest-asyncio", ".")
    session.install("pytest-mock", ".")
    session.install("coverage", ".")
    session.run("coverage", "run", "-m", "pytest")
    session.run("coverage", "xml")
