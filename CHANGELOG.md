# Changelog

## [1.0.0](https://github.com/derlin/rickroller/compare/v0.1.1...v1.0.0) (2023-08-17)


### ⚠ BREAKING CHANGES

* add optional URL shortening (requires persistence)

### 🚀 Features

* add limit on records in DB based on the client IP ([a113bee](https://github.com/derlin/rickroller/commit/a113beee9cacbfa4b9fc25af41149a456dba47c7))
* add loading indicator ([2fed676](https://github.com/derlin/rickroller/commit/2fed6762621dd0b8334cd4d38b9a6c179263a917))
* add optional URL shortening (requires persistence) ([1c5b6bd](https://github.com/derlin/rickroller/commit/1c5b6bd922a879061153f1a33aaf8dd33483f0c5))
* deploy to divio ([ed4269a](https://github.com/derlin/rickroller/commit/ed4269adf02c0490a993eb70e8479895c96c5aea))
* expose port 8080 ([c70b64d](https://github.com/derlin/rickroller/commit/c70b64d3f1a4fd096a7d1b96fd15265306917963))
* improve rickrolling using &lt;base&gt; tag ([bc5f840](https://github.com/derlin/rickroller/commit/bc5f84038e3b5eef76b1f34c70662f3cb86473bc))
* let user choose how many scrolls before roll ([836ebce](https://github.com/derlin/rickroller/commit/836ebcec200edff019c1f72d5a8630a7835fd9d3))
* make cleanup units configurable ([a34048e](https://github.com/derlin/rickroller/commit/a34048e46ca020693947e8609190255f8501e518))
* make it possible to change gunicorn logging level ([80c3c35](https://github.com/derlin/rickroller/commit/80c3c35459af2e57d97805db6da97aed2ed5f1ff))
* move from bandit to ruff ([39915b8](https://github.com/derlin/rickroller/commit/39915b84925f1fd686b7b155567ee55b46f9211a))
* optionally roll on scroll end ([d97ff78](https://github.com/derlin/rickroller/commit/d97ff78904d70a21a49f0d12cee9eec035579119))
* support MongoDB databases ([eb5b43f](https://github.com/derlin/rickroller/commit/eb5b43f6ba3648dfef91b0d0378433994d898b3f))
* support X-Forwarded-* headers ([c0feb94](https://github.com/derlin/rickroller/commit/c0feb94a4763b1076b3135a286a71cc927f4bdf2))


### 🐛 Bug Fixes

* add CSRF token ([f876402](https://github.com/derlin/rickroller/commit/f876402eb19ac392c4f1d5e7f23a1fbf8bf0c77f))
* allow safe redirects ([b30f806](https://github.com/derlin/rickroller/commit/b30f806f9755c06ebd6ed41d12c2076a05c784b9))
* avoid SSRF ([1138969](https://github.com/derlin/rickroller/commit/1138969b5a73444090eb22cae24142511b8a93a6))
* do not allow redirects (SSRFs) ([92a855e](https://github.com/derlin/rickroller/commit/92a855e21d785d78539ece2dbd3a5dc338005935))
* ensure postgres and postgresql dialects are treated the same ([c10e3d1](https://github.com/derlin/rickroller/commit/c10e3d1498952cfd570be510ba09605672a558e4))
* error handler leaking sensitive information ([155978b](https://github.com/derlin/rickroller/commit/155978b759b871fb914e2111b2342cdd8055370c))
* hide loading bar on back navigation (mobile) ([9fc491b](https://github.com/derlin/rickroller/commit/9fc491bdd069b63bdc537462b1bb324e77ee1258))
* missing commit on SQL and remove rollback ([20b84fa](https://github.com/derlin/rickroller/commit/20b84fab8124564606378b09af614c06c9d48592))
* missing gif and favicon on rickrolled page ([30bdd76](https://github.com/derlin/rickroller/commit/30bdd76a778f8f279b3bbffca20894f959afd5ad))
* show app logs when running on gunicorn and change format ([2df4ebf](https://github.com/derlin/rickroller/commit/2df4ebf1a256d94b8913737f55bff86419721f9e))
* support log level DEBUG ([e22091c](https://github.com/derlin/rickroller/commit/e22091c6baac3d9c8291a1948efbf61573aa9375))
* use a custom page for rickroll instead of YouTube ([ad1cfcb](https://github.com/derlin/rickroller/commit/ad1cfcb677d85834af4355696868ab8412dfddb0))
* use factory pattern for app ([7fd4007](https://github.com/derlin/rickroller/commit/7fd4007e3d44943806f6f2fd1692cee8b2e3077f))


### 🌈 Styling

* add font and use flexbox for footer ([e77561e](https://github.com/derlin/rickroller/commit/e77561e189b8e7467d396c2a861d0786ccab611c))
* update some colors ([ab61663](https://github.com/derlin/rickroller/commit/ab61663209c256d850132e6bf91a859dee4e41f1))


### 💬 Documentation

* add persistance and quickstart documentation ([580fd23](https://github.com/derlin/rickroller/commit/580fd23c5be29242cc8bdf0b704b5d12a7c3bc0a))
* document how rickrolling works ([a7acda1](https://github.com/derlin/rickroller/commit/a7acda1ef5990a3e40fbb2175aa1b096cef10d5e))
* update live url (divio) ([b3a3a6a](https://github.com/derlin/rickroller/commit/b3a3a6a1f837e351d330431287cea2f61ca237b5))


### 🦀 Build And CI

* always run build, publish only on develop+main ([158e703](https://github.com/derlin/rickroller/commit/158e70396da57aee76938c2ea1866488e85da2a4))
* always run lint ([c5caa96](https://github.com/derlin/rickroller/commit/c5caa9639d294d355ac445c8d236174a278e2592))
* better handle publish_dockerhub flag ([2bbb9cf](https://github.com/derlin/rickroller/commit/2bbb9cf39bff730d8ca5fd5c9ed18ef4eab0f5c4))
* upgrade and align Python OS images ([17070f7](https://github.com/derlin/rickroller/commit/17070f79d2b81b35fffb208f97c23cbd275ed3f8))

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
