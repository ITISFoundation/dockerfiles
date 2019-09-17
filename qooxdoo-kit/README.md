# [qooxdoo] toolkit

[![itis.dockerhub]](https://hub.docker.com/u/itisfoundation)
[![](https://images.microbadger.com/badges/image/itisfoundation/qooxdoo-kit.svg)](https://microbadger.com/images/itisfoundation/qooxdoo-kit "More info on latest image")
[![](https://images.microbadger.com/badges/version/itisfoundation/qooxdoo-kit.svg)](https://microbadger.com/images/itisfoundation/qooxdoo-kit "Get your own version badge on microbadger.com")
[![](https://images.microbadger.com/badges/commit/itisfoundation/qooxdoo-kit.svg)](https://microbadger.com/images/itisfoundation/qooxdoo-kit "Get your own commit badge on microbadger.com")

<!-- ADD HERE ALL BADGE URLS -->
[itis.dockerhub]:https://img.shields.io/website/https/hub.docker.com/u/itisfoundation.svg?down_color=red&label=dockerhub%20repos&up_color=green
<!---------------------------->


TODO: https://github.com/ITISFoundation/osparc-simcore/issues/572

## Content

- [qooxdoo] compiler
- [puppeteer] - **TEMPORARY DISABLED**. Check [troubeshooting](https://github.com/GoogleChrome/puppeteer/blob/master/docs/troubleshooting.md#running-on-alpine). See also [this ref](https://paul.kinlan.me/hosting-puppeteer-in-a-docker-container/)


See [package.json](package.json) for version specs

## Usage

Some self-explanatory examples

    $ make help

    $ make build
    $ make info
    $ make shell
    $ make shell cmd="jq '.dependencies' package.json"
    $ make clean

    $ make build-nc tag

    $ make build-nc test release


<!--REFERENCES. Please keep alphabetical order -->
[qooxdoo]:qooxdoo.org
[puppeteer]:pptr.dev