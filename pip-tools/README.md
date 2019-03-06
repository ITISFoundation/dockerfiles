# dev tools

Container for python-based command-line utilities to assist development tasks.

## Content

- [cookiecutter]  creates projects from cookiecutters (project templates)
- [pipdeptree]: displaying the installed python packages in form of a dependency tree
- [pip-tools] (pip-compile + pip-sync): help you keep your pip-based packages fresh, even when you’ve pinned (i.e. freeze) them

## Usage

```bash
$ docker -it -v $(pwd):/home/scu/data ITISFoudation/devtools cookiecutter

# OR
$ docker-compose devtools run cookiecutter --help

```



[cookiecutter]:https://cookiecutter.readthedocs.io/en/latest/
[pipdeptree]:https://pypi.org/project/pipdeptree/
[pip-tools]:https://pypi.org/project/pip-tools/