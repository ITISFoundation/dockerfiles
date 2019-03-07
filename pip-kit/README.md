# pip toolkit

Managing python dependencies without loosing control or your mind ... :-)

## Content

- [pipdeptree] displays a dependency tree of the installed python packages
- [pip-tools] (``pip-compile`` + ``pip-sync``) helps you keep your pip-based packages fresh, even when you’ve pinned (i.e. freeze) them
- [yolk] gets info about installed packages or those in some registry (e.g. PyPI)
- [pipreqs] deduces the requirements from the source code of a package
  
## Usage

```bash
docker -it itisfoundation/pip-kit --help
```

```bash
echo pip-tools > requirements.in

docker -it -v $(pwd):/home/itis/work itisfoundation/pip-kit pip-compile requirements.in
# OR
docker-compose run pip-kit pip-compile requirements.in
```

<!--REFERENCES. Please keep alphabetical order -->
[pipdeptree]:https://pypi.org/project/pipdeptree/
[pipreqs]:https://github.com/bndr/pipreqs
[pip-tools]:https://pypi.org/project/pip-tools/
[yolk]:https://github.com/myint/yolk