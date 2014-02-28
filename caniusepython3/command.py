import setuptools

import caniusepython3 as ciu
import caniusepython3.__main__ as ciu_main


class Command(setuptools.Command):

    description = """Run caniusepython3 over a setup.py file."""

    user_options = []

    _require_fields = ('install_requires', 'extras_require', 'setup_requires',
                       'tests_require')

    def initialize_options(self):
        pass

    def run(self):
        projects = []
        for attr in self._require_fields:
            requirements = getattr(self.distribution, attr, None) or []
            for project in requirements:
                if not project:
                    continue
                projects.append(ciu.just_name(project))
        ciu_main.check(projects)

    def finalize_options(self):
        pass
