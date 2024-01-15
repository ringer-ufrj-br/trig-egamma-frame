import setuptools
import os

here = os.path.dirname(os.path.realpath(__file__))
requirements_path = os.path.join(here, "requirements.txt")
readme_path = os.path.join(here, "README.md")

requirements = []
with open(requirements_path) as _fp:
    for line in _fp.readlines():
        requirements.append(line)

with open(readme_path, "r") as _fp:
    long_description = _fp.read()


setuptools.setup(
  name = 'trig-egamma-frame',
  version = '1.0',
  license='GPL-3.0',
  description = '',
  long_description = long_description,
  long_description_content_type="text/markdown",
  packages=setuptools.find_packages(),
  author = 'João Victor da Fonseca Pinto and Micael Verissimo de Araujo',
  author_email = 'jodafons@lps.ufrj.br and micael.verissimo@lps.ufrj.br',
  url = 'https://gitlab.cern.ch/atlas-trig-egamma/ringer/trig-egamma-frame',
  classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
  ],
)