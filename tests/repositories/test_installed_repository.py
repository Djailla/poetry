from importlib_metadata import PathDistribution
from poetry.repositories.installed_repository import InstalledRepository
from poetry.utils._compat import Path
from poetry.utils.env import MockEnv as BaseMockEnv


FIXTURES_DIR = Path(__file__).parent / "fixtures"
ENV_DIR = (FIXTURES_DIR / "installed").resolve()
SITE_PACKAGES = ENV_DIR / "lib" / "python3.7" / "site-packages"
SRC = ENV_DIR / "src"
INSTALLED_RESULTS = [
    PathDistribution(SITE_PACKAGES / "cleo-0.7.6.dist-info"),
    PathDistribution(SRC / "pendulum" / "pendulum.egg-info"),
]


class MockEnv(BaseMockEnv):
    @property
    def site_packages(self):  # type: () -> Path
        return SITE_PACKAGES


def test_load(mocker):
    mocker.patch(
        "importlib_metadata.Distribution.discover", return_value=INSTALLED_RESULTS
    )
    mocker.patch(
        "poetry.vcs.git.Git.rev_parse",
        return_value="bb058f6b78b2d28ef5d9a5e759cfa179a1a713d6",
    )
    mocker.patch(
        "poetry.vcs.git.Git.remote_urls",
        side_effect=[
            {"remote.origin.url": "https://github.com/sdispater/pendulum.git"},
            {"remote.origin.url": "git@github.com:sdispater/pendulum.git"},
        ],
    )
    repository = InstalledRepository.load(MockEnv(path=ENV_DIR))

    assert len(repository.packages) == 2

    cleo = repository.packages[0]
    assert cleo.name == "cleo"
    assert cleo.version.text == "0.7.6"
    assert (
        cleo.description
        == "Cleo allows you to create beautiful and testable command-line interfaces."
    )

    pendulum = repository.packages[1]
    assert pendulum.name == "pendulum"
    assert pendulum.version.text == "2.0.5"
    assert pendulum.description == "Python datetimes made easy"
    assert pendulum.source_type == "git"
    assert pendulum.source_url == "https://github.com/sdispater/pendulum.git"
    assert pendulum.source_reference == "bb058f6b78b2d28ef5d9a5e759cfa179a1a713d6"
