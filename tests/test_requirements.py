from importlib import metadata
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

REQUIREMENTS = Path(__file__).resolve().parents[1] / "requirements.txt"
OLDEST_PYTHON = {"python_version": "3.8", "python_full_version": "3.8.10", "extra": ""}
PACKAGING_PYTHON = {"python_version": "3.14", "python_full_version": "3.14.0", "extra": ""}


def top_level_requirements():
    lines = REQUIREMENTS.read_text(encoding="utf-8").splitlines()
    return [Requirement(line) for line in lines if line.strip() and not line.startswith("#")]


def applies(requirement, environment):
    return requirement.marker is None or requirement.marker.evaluate(environment)


def dependency_closure(environment):
    seen = set()
    pending = [r.name for r in top_level_requirements() if applies(r, environment)]
    while pending:
        name = pending.pop()
        key = canonicalize_name(name)
        if key in seen:
            continue
        seen.add(key)
        try:
            requires = metadata.requires(name) or []
        except metadata.PackageNotFoundError:
            continue
        pending.extend(r.name for r in map(Requirement, requires) if applies(r, environment))
    return seen


def test_zip_built_on_new_python_has_everything_python_38_needs():
    # package.sh vendors for Python 3.8, but pip evaluates dependency markers
    # against the Python running it, so 3.8-only dependencies must be listed.
    missing = dependency_closure(OLDEST_PYTHON) - dependency_closure(PACKAGING_PYTHON)
    assert not missing
