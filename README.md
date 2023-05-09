# RickRoller

> RickRoller is a dumb (yet funny) project mostly used as a pretext to play with Google Cloud Run,
GitHub Actions and to try Open Source best practices. Keep reading to know more about what I learned.

Transform any web page into a RickRoller! Test it live
:point_right: [**https://tinyurl.eu.aldryn.io**](https://tinyurl.eu.aldryn.io).

(*For the curious, the live demo is hosted by **[Divio](https://divio.com)**, which is awesome :blue_heart:.
Check it out! Another live demo is deployed from Google Cloud Run and available at [https://rroll.derlin.ch](https://rroll.derlin.ch). It is, however, way slower than the Divio host...*)

![big](https://user-images.githubusercontent.com/5463445/163544627-6fcf82e5-caf9-467c-b234-b0a496b93b5c.png)

Simply take a webpage, paste its URL into the box, and BAM! The same webpage will be displayed,
but every click will redirect you to the famous Rick Astley video,
[never gonna give you up](https://www.youtube.com/watch?v=dQw4w9WgXcQ).

:new: To make it even more efficient at trolling your friends, RickRoller can now disguise itself
as an URL shortener (requires a database)!
Learn more at [docs/persistence](docs/persistence.md).

To run RickRoller locally or deploy it using Docker, see [docs/quickstart](docs/quickstart.md).
To better understand how the RickRolling works, see [docs/rickrolling](docs/rickrolling.md).

-------------

<p align="center"><b> ⇓ ᗯᕼᗩT I ᒪEᗩᖇᑎEᗪ ⇓ </b></p>

------------

# Best practices

<!-- TOC start -->
- [Conventional Commits](#conventional-commits)
- [GitHub Repository settings](#github-repository-settings)
- [Codebase](#codebase)
  * [Linters and SAST](#linters-and-sast)
- [Docker images](#docker-images)
  * [Labels](#labels)
  * [Multi-stage build](#multi-stage-build)
  * [HEALTHCHECK and USER](#healthcheck-and-user)
  * [Multi-platform support](#multi-platform-support)
- [GitHub CI](#github-ci)
  * [Building docker images](#building-docker-images)
  * [Keeping the GitHub Registry clean](#keeping-the-github-registry-clean)
  * [Pushing docker images to both Docker Hub and GitHub Registry](#pushing-docker-images-to-both-docker-hub-and-github-registry)
  * [Release automation: release-please](#release-automation-release-please)
  * [Deploying to Cloud Run With GitHub Action](#deploying-to-cloud-run-with-github-action)
    + [Google Project setup](#google-project-setup)
    + [GitHub Action](#github-action)
- [Other Tips and tricks](#other-tips-and-tricks)
  * [Keep python dependencies up-to-date](#keep-python-dependencies-up-to-date)
  * [Avoid SSRFs](#avoid-ssrfs)
<!-- TOC end -->

<!-- TOC --><a name="conventional-commits"></a>
## Conventional Commits

This repository is using [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/).

This is a simple convention that is both for humans and machines.
I am currently using the basic tags (`feat:` and `fix:`), plus the ones based on [the Angular conventions](
https://github.com/angular/angular/blob/22b96b9/CONTRIBUTING.md#-commit-message-guidelines)
(`build:`, `chore:`, `ci:`, `docs:`, `style:`, `refactor:`, `perf:`, `test:`).

The advantage? By adding a semantic layer to git commits, one can automate lots of tasks such as CHANGELOG
updates, releases, version bumps, statistics, etc. There are lots of tools out there that support this convention,
and it keeps growing!

<!-- TOC --><a name="github-repository-settings"></a>
## GitHub Repository settings

Lots of mistakes and chores can be avoided by properly configuring a GitHub repository.
I am personally in favor of pull requests and clean linear history (squash and merge).
Below are the most important settings for this goal.

**Protect your main branch**: under *Settings* > *Branches*, create a new *Branch protection rule*
for your main branch. What you choose here depends on the project, but I would try to always check:

- *require a pull request before merging*: this ensures no one is pushing directly to `main`.
- *require status checks to pass before merging*: if you have some CI workflows, they should always
  be green before anything is merged!
- *include administrators*: this one is tricky. If you do not check it, admins will be able to bypass
  all rules, meaning you could e.g. force push to `main` by mistake.  

**Enforce a clean history**: this is a highly controversial subject, but I am personally in favor of one
commit, one feature (→ squash before merging). To enforce this in GitHub: 

* in *Settings* > *General* > *Pull Requests*, only check *Allow squash merging*;
* in main branch protection, check *require linear history*.


**Cleanup**: to limit the number of stale branches, check the following in *Settings* > *General* > *Pull Requests*:
* *Automatically delete head branches*: branches are automatically deleted after a PR is merged.

<!-- TOC --><a name="codebase"></a>
## Codebase

<!-- TOC --><a name="linters-and-sast"></a>
### Linters and SAST

Projects should ALWAYS use linting, code formatting rules, and SAST tools.
This eases collaboration and prevents big mistakes.

Each language has its own tools. This specific project (Python + Docker) uses:

* [black](https://github.com/psf/black) for (automatically) formatting python files,
* [~~bandit~~](https://bandit.readthedocs.io/) ~~for checking vulnerabilities in python files~~
* [ruff](https://beta.ruff.rs/docs/) for linting and checking style + vulnerabilities in python files,
* [checkov](https://checkov.io) for checking vulnerabilities in docker images.

black and ruff are listed under dev dependencies. To run the checks locally:
```bash
poetry run black --line-length 100 --check rickroll
poetry run ruff rickroll
```

To fix the problems automatically (when possible), run:
```bash
# formatting
# automatically fix the formatting issue, if possible
poetry run black --line-length 100 --experimental-string-processing rickroll
# automatically fix the issues, if possible
poetry run ruff --fix rickroll
```

As checkov is quite heavy, it is run using a dedicated GitHub action in the CI.
To run it locally:
```bash
poetry run pip install checkov # install, without adding it to pyproject.toml
poetry run checkov --framework dockerfile -f Dockerfile
```

<!-- TOC --><a name="docker-images"></a>
## Docker images

<!-- TOC --><a name="labels"></a>
### Labels

The Docker image uses common labels from [opencontainers](
https://github.com/opencontainers/image-spec/blob/main/annotations.md).
Those are extracted automatically in the CI using [docker/metadata-action](
https://github.com/docker/metadata-action).
They can also be set manually using the `--label` parameter:
```bash
# the --label parameter can be repeated as much as needed
docker build \
  --label org.opencontainers.image.title=rickroller \
  --label org.opencontainers.image.url=https://github.com/derlin/rickroller \
  -t rroll .
```

Note that opencontainers labels are supported by GitHub: the description,
etc. you provide will be used and displayed in the *packages* interface of GitHub. 

<!-- TOC --><a name="multi-stage-build"></a>
### Multi-stage build

The Dockerfile uses [multi-stage build](https://docs.docker.com/develop/develop-images/multistage-build/).
The idea is to use multiple `FROM` in a Dockerfile. The first one(s) are there to build the different
artifacts, which can then be copied into the final `FROM` section (the final image), that only contain
what is needed to run them.
This way, the final image is kept at its minimum, which improves performance, storage, and security.

Since the Flask app runs with `gunicorn`, the module doesn't need to be built/installed:
gunicorn will find it automatically if it is located in the `pwd`.
Hence, I only need to create the virtual env (installing deps using poetry) in my build stage.
In the final image, I copy the virtual env from the previous step, and the `rickroll` folder from the
host.

If the module had to be properly installed in the final Docker image, one way to do it is
to call `poetry build` in the builder. This will create a `*.whl` that can be copied in the
final image and installed with pip.
Another way is simply to install it in the venv of the builder, then ensure that the venv is
activated in the final image (e.g. in an `entrypoint.sh`).

<!-- TOC --><a name="healthcheck-and-user"></a>
### HEALTHCHECK and USER

As checkov told me, Docker containers should provide a [health check
instruction](https://docs.docker.com/engine/reference/builder/#healthcheck).
Note that this healthcheck is not used by Kubernetes, which defines its own, more powerful checks
through `livenessProbe`, `readinessProbe`, and `startupProbe`.

The most common way to implement a health check is to use cURL (cf the official doc):
```dockerfile
HEALTHCHECK --interval=5m --timeout=3s \
  CMD curl -f http://localhost/ || exit 1
```

This, however, requires `curl` to be installed in the container. As it would be a shame to install
it (and thus increase the image size) only for the check, I used a python script instead.
Note that the `requests` package is needed by the app, so I know it is available:
```dockerfile
HEALTHCHECK --start-period=5s --interval=1m --timeout=10s CMD python -c 'import requests' \
    'try:' \
    '  exit(0 if requests.get("http://localhost:8080").status_code == 200 else 1)' \
    'except:' \
    '  exit(1)'
```

In general, I suggest you try to find a way to reuse what you already have available in your image.

Docker containers should also never run as root. Avoiding root is as easy as using `USER xxx`.
Be careful though: if you copy some files that were generated (e.g. in your builder) using
the root user, you may run into permission errors.

This is why I use the `--chown` option in the Dockerfile:
```dockerfile
USER app
# ...
COPY --chown=app --from=venv /app/.venv .venv
```

<!-- TOC --><a name="multi-platform-support"></a>
### Multi-platform support

Now that Apple switched to ARM, it is important to provide images for both AMD and ARM (at the very
least). Using buildx (readily available on Docker Desktop for Mac):
```bash
export DOCKER_BUILDKIT=1
docker build -t rroll --rm --progress=plain --platform linux/amd64  .
docker build -t rroll --rm --progress=plain --platform linux/arm64  .
```

<!-- TOC --><a name="github-ci"></a>
## GitHub CI

<!-- TOC --><a name="building-docker-images"></a>
### Building docker images

On GitHub, the action [docker/build-push-action](https://github.com/docker/build-push-action)
should be used to build docker images. It is very convenient, as it is able to:

* add the proper labels generated by the docker/metadata-action (`with.labels`),
* optionally publish to GitHub packages (`with.push`), given that you logged in to
  Docker in a previous step,
* build Docker images for both arm and amd platform `with.platforms`.

The last point is important, now that Apple switched to ARM. If you forget this simple
parameter, Mac users won't be able to pull/use your image!

Here is the relevant part (the full workflow is in `.GitHub/workflows`):
```yaml
    # build arm64 requires buildx, but also the QEMU emulator,
    # since GitHub Actions runners are amd !
    - name: Set up QEMU
      uses: docker/setup-qemu-action@v2

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2

    - name: Build and push Docker image
      uses: docker/build-push-action@v3
      with:
        context: .
        platforms: linux/amd64,linux/arm64  # also support the new mac architecture
        push: true  # push to the Docker registry (assuming you used docker/login in a previous step)
        # the next two are coming from the docker/metadata-action step (I gave it the id `meta`)
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
```

**Layer caching**

Docker layer caching (DLC) is a great feature when building Docker images is a regular part of the CI process.

The idea is to cache the individual layers of Docker images built in CI jobs, and then reuse unchanged image layers
on subsequent runs, rather than rebuilding the entire images from scratch every time.

This caching mechanism is a given when building Docker images locally (see Docker's documentation - [leverage build cache](
https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#leverage-build-cache)). However, in CI,
a new runner is started each time, so the cache is always empty by default.

The build-push-action from Docker [supports multiple types of caches](https://github.com/docker/build-push-action/blob/master/docs/advanced/cache.md).
In this repo, I use the GitHub cache (`gha`). It is rather straightforward to turn on: simply set the `cache-from` and
`cache-to` parameters. One important detail is the `mode=max`, which instructs the action to cache **all** layers, and not only the
ones from the final image. It is very important if your Dockerfile is using multi-stage builds.

```yaml
- name: Build and push Docker image
  uses: docker/build-push-action@v3
  with:
    # ...
    cache-from: type=gha
    cache-to: type=gha,mode=max # <-- mode=max will also cache all layers, vs only the ones from the final image
```

With DLC, the less the Dockerfiles change from commit to commit, the faster the image-building steps will run.
It is thus important to keep this in mind when writing the Dockerfile.


**Tags**

The metadata-action is configured to add tags to Docker images based on the workflow trigger.

Unique tags:

* an image built from a pull request gets tagged `pr-{{N}}`, with `N` the pull request number,
* an image built from branch *main* creates a tag `main-{{SHA}}`, with `SHA` the short SHA of the commit,
* an image built from a release is tagged with the full version (`major.minor.patch`, e.g. `1.2.0`)

Moving tags:

* the tag *latest* is added to the latest build on branch *main*,
* the version tags `{{major}}` and `{{major}}.{{minor}}` are updated on each release, based on the version released.
  For example, if version `1.2.0` is released, the image will get the tag `1` and `1.2` (as well as the unique tag `1.2.0`).

Moving tags are useful for users, while unique tags are useful for developers when they want to test a specific version of the
code. 

<!-- TOC --><a name="keeping-the-github-registry-clean"></a>
### Keeping the GitHub Registry clean

A lot of images will be pushed to the registry from the CI.

To clean up old tags, a workflow triggered manually is available.
It uses the [vlaurin/action-ghcr-prune](https://github.com/vlaurin/action-ghcr-prune/issues/64)
action to do the dead, which proposes lots of useful options. See their documentation
for details.

Note that to be used, this action requires a PAT - **P**ersonal **A**ccess **T**oken
(it cannot work with the default `GITHUB_TOKEN`), with at least the scopes `repo`
and `packages:delete`.

<!-- TOC --><a name="pushing-docker-images-to-both-docker-hub-and-github-registry"></a>
### Pushing docker images to both Docker Hub and GitHub Registry

In the first iteration of the reusable docker build/push workflow, I only pushed to `ghcr.io`.
Then came the wish to also push to Docker Hub, but only "meaningful" tags: `latest`, and release-related.
In other words, tags for ghcr.io and docker.io are **different**.
I tried multiple approaches and finally came up with a good-enough solution. The idea:

* run the [docker/metadata-action](https://github.com/docker/metadata-action) twice, one for each
  registry, using different inputs;
* add a step that concatenates both results into a single environment variable;
* pass the content of this new environment variable to [docker/build-push-action](docker/build-push-action).

Note that tags must be a multi-line string, with one image per line.
Multi-line strings are tricky in GitHub Actions, and need to use a *heredoc*:
```yaml
- name: Set a multi-line environment variable
  run: |
    echo 'ident<<EOF' >> $GitHub_OUTPUT
    echo -e 'First line\nSecond line\n...' >> $GitHub_OUTPUT
    echo "EOF" >> $GitHub_OUTPUT
```

(See https://github.com/orgs/community/discussions/26288.)

<!-- TOC --><a name="release-automation-release-please"></a>
### Release automation: release-please

Google's release please action simplifies the creation of releases, given your repository uses [conventional commits](
https://www.conventionalcommits.org/en/v1.0.0/).

Basically, [release-please-action](https://github.com/google-GitHub-actions/release-please-action/) is called on each push
to main, and will create (or update) a PR for the next release. The PR will automatically:
* bump the version to the next correct semantic one, depending on your commits (breaking changes, fixes, etc);
* update the CHANGELOG.

Once ready for release, just merge the PR to main. Release-please will be called again and will create a tag
(`vX.X.X`) and a GitHub Release. Additional tasks such as building the Docker image for the tag or attaching assets to
the GitHub releases are up to us.

There are some pitfalls though.

First, by default release-please uses the default GitHub token to create the tag, and thus won't trigger other workflows
supposed to react to tag creation:

> When you use the repository's GitHub_TOKEN to perform tasks, events triggered by the GitHub_TOKEN will not create a new workflow run.
> This prevents you from accidentally creating recursive workflow runs.
> [source](https://docs.GitHub.com/en/actions/security-guides/automatic-token-authentication#using-the-GitHub_token-in-a-workflow)


So how can we build the Docker image on release? Two ways:
1. configure release-please to use a PAT (*P*ersonal *A*ccess *T*oken), and create a workflow triggered by tags `v*`;
2. use release-please output `release_created` to conditionally run another job after release-please. 

I went for 2, and this is why I use a reusable workflow to push Docker images, and call it in both build and release-please.

Second, Java/Kotlin `-SNAPSHOT` conventions are not supported for now: at any one time, the version in the git repo is the
last one released. With Gradle, one way to dirty fix this is to use a `version.txt` at the root managed by release-please,
and to add some logic in `build.gradle`/`build.gradle.kts`. See [https://github.com/derlin/docker-compose-viz-mermaid](
https://github.com/derlin/docker-compose-viz-mermaid/blob/main/build.gradle.kts#L12) for an example.

<!-- TOC --><a name="deploying-to-cloud-run-with-github-action"></a>
### Deploying to Cloud Run With GitHub Action

<!-- TOC --><a name="google-project-setup"></a>
#### Google Project setup

(See https://github.com/google-GitHub-actions/deploy-cloudrun#setup)

1. create project (I used an educational account)
2. enable *Cloud Run*, *IAM* and *Container Registry* APIs
3. create a service account with the following roles:
    * *Cloud Run Admin*: the role which will allow us to create a new Cloud Run deployment;
    * *Storage Admin*: the role which allows us to upload our Docker images to the GCP’s Container Registry;
    * *Service Account User*: the role that allows the service account to act as a user.
4. once created, click on *manage keys* and add a key in JSON format. This will generate a file that you must keep in a safe and secret place.

Now on GitHub Actions, create a new secret with the content of the JSON file: *Settings* > *Secrets* > *Actions*.
The name can be `GOOGLE_CREDENTIALS` (will be referenced later in a workflow using `${{ secrets.GOOGLE_CREDENTIALS }}`),
and the value must be the JSON content.

<!-- TOC --><a name="github-action"></a>
#### GitHub Action

The action is triggered manually and supports optional parameters.

Main actions used:

* [setup-gcloud](https://github.com/google-GitHub-actions/setup-gcloud)
* [deploy-cloud-run](https://github.com/google-GitHub-actions/deploy-cloudrun)

Resources:

* [build and push workflow example](https://github.com/google-GitHub-actions/deploy-cloudrun/blob/main/.GitHub/workflows/example-workflow.yaml)
* [setup gcloud + auth](https://github.com/google-GitHub-actions/setup-gcloud)


**NOTES**

On the first push, a service will be created in Cloud Run that DO NOT allow unauthenticated requests.
This may be modified in the Cloud Run Console:

> A Cloud Run product recommendation is that CI/CD systems not set or change settings for allowing unauthenticated invocations.
> New deployments are automatically private services while deploying a revision of a public (unauthenticated) service will preserve the IAM setting of public (unauthenticated).

To make it public:

1. Go to Cloud Run Service *Permissions*
2. Add a new user:
    * Principal: `allUsers` 
    * Roles: *Cloud Run Invoker*

To add a custom domain: https://cloud.google.com/run/docs/mapping-custom-domains#map

<!-- TOC --><a name="other-tips-and-tricks"></a>
## Other Tips and tricks

<!-- TOC --><a name="keep-python-dependencies-up-to-date"></a>
### Keep python dependencies up-to-date

To update to the latest versions but still respect the constraints in `pyproject.toml`, use:
```bash
poetry update
```

To bump the versions in `pyproject.toml` easily, use [poetryup](https://pypi.org/project/poetryup/):
```bash
poetryup --latest
```

<!-- TOC --><a name="avoid-ssrfs"></a>
### Avoid SSRFs

*S*erver-*S*ide *R*equest *F*orgery (SSRF) is a web security vulnerability that allows an
attacker to induce the server-side application to make requests to an unintended location.

For example, the user may supply to RickRoller the address of a service only reachable from
the internal network where the RickRoller server is located.
Imagine it being hosted on Amazon, and an internal service being the metadata amazon server
hosting tokens and login information. An external user cannot access it as its IP is non-routable,
but RickRoller can as it is hosted on the same network. If we are not careful, RickRoller
could return sensitive information to the user.

More information can be found online, for example, https://portswigger.net/web-security/ssrf.

The mitigation implemented in this repo is two-fold:
1. Before fetching the content from the URL provided, RickRoller resolves the hostname into
   an IP address. If the latter is private (aka non-routable), it stops and raises an exception.
2. During the fetch, RickRoller does follow redirects but keeps a list of redirections.
   Before returning any content, the same checks as in (1) are applied to the full redirection
   history.
