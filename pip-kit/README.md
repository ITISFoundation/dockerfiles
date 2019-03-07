# pip toolkit
[![image-size]](https://microbadger.com/images/itisfoundation/pip-kit "More on itisfoundation/pip-kit latet image")
[![image-badge]](https://microbadger.com/images/itisfoundation/pip-kit "More on image in registry")
[![image-version]](https://microbadger.com/images/itisfoundation/pip-kit "More on image in registry")
[![image-commit]](https://microbadger.com/images/itisfoundation/pip-kit "More on mage in registry")

Managing python dependencies without loosing control or your mind ... :-)

<!-- Add badges urls here-->
[image-size]:https://img.shields.io/microbadger/image-size/itisfoundation/pip-kit:latest.svg?label=pip-kit
[image-badge]:https://images.microbadger.com/badges/image/itisfoundation/pip-kit.svg
[image-version]:https://images.microbadger.com/badges/version/itisfoundation/pip-kit.svg
[image-commit]:https://images.microbadger.com/badges/commit/itisfoundation/pip-kit.svg
<!------------------------->

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
