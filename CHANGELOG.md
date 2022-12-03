# Changelog

## [0.1.1](https://github.com/derlin/rickroller/compare/v0.1.0...v0.1.1) (2022-12-03)


* fix missing secrets during release ([fa9ddb7](https://github.com/derlin/rickroller/commit/fa9ddb7c35daaf0e6be32d9b02378df503d6c32f))
* publish only latest and release to Docker Hub ([c2c7240](https://github.com/derlin/rickroller/commit/c2c7240c6f1fa26255861232a2c0995cc0b5cb49))


### 🐛 Bug Fixes

* repair broken Docker image ([ff1b4d6](https://github.com/derlin/rickroller/commit/ff1b4d62803eb0490e2f792bfff3cdfde8bd0f26))


### 💬 Documentation

* add Docker Hub section in README and proofread ([cc9f64a](https://github.com/derlin/rickroller/commit/cc9f64a5d43807bbe4010f6fb8c8b2307ee8d0f6))
* add how to run image from Docker Hub ([fe89b5d](https://github.com/derlin/rickroller/commit/fe89b5d39fe2c5d3318b0220b28e1e9b111df27f))

## 0.1.0 (2022-12-01)


### 🚀 Features

* simple rick-rolling implementation ([e15f2a1](https://github.com/derlin/rickroller/commit/e15f2a1437a0fdff245b48a48e0414aa1acc577a))


### 🦀 Build And CI

* switch to poetry and Docker alpine ([db9ab1c](https://github.com/derlin/rickroller/commit/db9ab1c3136698e33aa4593c8664354d06f233f0))
* use python package (setup.py) ([c673e28](https://github.com/derlin/rickroller/commit/c673e28ad776ced773345af625de5c3e1bc29404))


### 🐛 Bug Fixes

* add Dockerfile healthcheck and user (checkov warning) ([83592e8](https://github.com/derlin/rickroller/commit/83592e8567ee6bfb01caccae5e791ab38b5ee7e0))
* catch exception and bind to 127.0.0.1 by default (bandit) ([d75a434](https://github.com/derlin/rickroller/commit/d75a434e7b1cfbd45cc8dd7676d135350ccc6493))
* redirect on click ([aefe986](https://github.com/derlin/rickroller/commit/aefe986d2203023a52a02be59fde8e2a4fa2501d))


### 💬 Documentation

* add README ([30656ec](https://github.com/derlin/rickroller/commit/30656ecf3812fd10b61e22496b8bfec042da93f2))


* add bandit (sast) ([c889b52](https://github.com/derlin/rickroller/commit/c889b5267579c7bd344638b5c2cbaed3cd388ff0))
* add build workflow ([213e73c](https://github.com/derlin/rickroller/commit/213e73c04e01aca8345b26ddf65736bc9a1e616a))
* add Cloud Run release workflow ([56f0f2b](https://github.com/derlin/rickroller/commit/56f0f2b93a19a1749a6993d956ed5201c9a7902f))
* add docker layer caching ([2e9aa00](https://github.com/derlin/rickroller/commit/2e9aa004217afae9b455b1acd88b6e247aaec1ec))
* add release-please ([11aa5d0](https://github.com/derlin/rickroller/commit/11aa5d0df9b32e1a74792e071df62fc294ef4156))
* always run lint (pr, main, develop), but publish Docker image only on main ([496cba4](https://github.com/derlin/rickroller/commit/496cba44387f2e81b47d6f8ec284b46b630005a2))
* build Docker container for ARM architecture ([168b5a1](https://github.com/derlin/rickroller/commit/168b5a1a93b60ea22d68c2832330a4a54e769761))
* publish Docker Image on release ([7bca618](https://github.com/derlin/rickroller/commit/7bca61881977087a65306c40c8164cb101a18001))
* publish images to Docker Hub ([295c8c0](https://github.com/derlin/rickroller/commit/295c8c096362ab60d90b0c7d36f07cd65d40bc19))
* run build workflow on tags ([50c1270](https://github.com/derlin/rickroller/commit/50c12706c25ba32d47aad17ee60e398e7bf9df58))
* scan docker vulnerabilities using checkov ([81a2ef1](https://github.com/derlin/rickroller/commit/81a2ef1edf15dca8c9ca7ab9dea86f63f1c99d47))
* update actions and fix poetry install warning ([8b03ab6](https://github.com/derlin/rickroller/commit/8b03ab644c8888d4bd04648977d1c1161f1cc66a))
* use release-please python release-type ([81a127f](https://github.com/derlin/rickroller/commit/81a127fb362b01c828ccba46b4ab4f161fc975dc))
