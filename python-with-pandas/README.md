# python-with-pandas:*-alpine

Pre-buit of python-alpine including numpy and pandas

## Motivation

[blackfynn-python] client library takes VERY long to install in alpine because it contains pandas therefore services like storage would benefit from a pre-built base image with blackfynn requirements pre-installed in a python2 virtualenv

See [discussion](https://stackoverflow.com/questions/49037742/why-does-it-take-ages-to-install-pandas-on-alpine-linux?rq=1)  about installing pandas in alpine linux

- [Installing pandas in alpine is slow]:(https://stackoverflow.com/questions/49037742/why-does-it-take-ages-to-install-pandas-on-alpine-linux?rq=1)

## References

- alpine-pkg-py-pandas - https://github.com/sgerrand/alpine-pkg-py-pandas
- alpine packages - https://github.com/nbgallery/apks


[blackfynn-python]:https://github.com/Blackfynn/blackfynn-python