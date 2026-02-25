# Justfile

This project uses [Just](https://github.com/casey/just) as a command runner.

The following commands are available:

<!-- [[[cog
import subprocess
import cog

help = subprocess.run(['just', '--summary'], stdout=subprocess.PIPE)

for command in help.stdout.decode('utf-8').split(' '):
    command = command.strip()
    cog.outl(
        f"- [{command}](#{command})"
    )
]]] -->
- [bootstrap](#bootstrap)
- [coverage](#coverage)
- [demo](#demo)
- [lint](#lint)
- [lock](#lock)
- [test](#test)
- [testall](#testall)
- [types](#types)
- [copier::copy](#copier::copy)
- [copier::recopy](#copier::recopy)
- [copier::recopy-all](#copier::recopy-all)
- [copier::update](#copier::update)
- [copier::update-all](#copier::update-all)
- [docs::build](#docs::build)
- [docs::serve](#docs::serve)
<!-- [[[end]]] -->

## Commands

```{code-block} shell
:class: copy

$ just --list
```
<!-- [[[cog
import subprocess
import cog

list = subprocess.run(['just', '--list'], stdout=subprocess.PIPE)
cog.out(
    f"```\n{list.stdout.decode('utf-8')}\n```"
)
]]] -->
```
Available recipes:
    bootstrap
    coverage
    demo
    lint
    lock *ARGS
    test *ARGS
    testall *ARGS
    types *ARGS
    copier ...
    docs ...

```
<!-- [[[end]]] -->

<!-- [[[cog
import subprocess
import cog

summary = subprocess.run(['just', '--summary'], stdout=subprocess.PIPE)

for command in summary.stdout.decode('utf-8').split(' '):
    command = command.strip()
    cog.outl(
        f"### {command}\n"
    )
    cog.outl(
        f"```{{code-block}} shell\n"
        f":class: copy\n"
        f"\n$ just {command}\n"
        f"```\n"
    )
    command_show = subprocess.run(['just', '--show', command], stdout=subprocess.PIPE)
    cog.outl(
        f"```{{code-block}} shell\n{command_show.stdout.decode('utf-8')}```\n"
    )
]]] -->
### bootstrap

```{code-block} shell
:class: copy

$ just bootstrap
```

```{code-block} shell
bootstrap:
    uv python install
    uv sync --frozen
```

### coverage

```{code-block} shell
:class: copy

$ just coverage
```

```{code-block} shell
coverage:
    @just nox coverage
```

### demo

```{code-block} shell
:class: copy

$ just demo
```

```{code-block} shell
demo:
    @just nox demo
```

### lint

```{code-block} shell
:class: copy

$ just lint
```

```{code-block} shell
lint:
    uv run --with pre-commit-uv pre-commit run --all-files
    just fmt
```

### lock

```{code-block} shell
:class: copy

$ just lock
```

```{code-block} shell
lock *ARGS:
    uv lock {{ ARGS }}
```

### test

```{code-block} shell
:class: copy

$ just test
```

```{code-block} shell
test *ARGS:
    @just nox test {{ ARGS }}
```

### testall

```{code-block} shell
:class: copy

$ just testall
```

```{code-block} shell
testall *ARGS:
    @just nox tests {{ ARGS }}
```

### types

```{code-block} shell
:class: copy

$ just types
```

```{code-block} shell
types *ARGS:
    @just nox types {{ ARGS }}
```

### copier::copy

```{code-block} shell
:class: copy

$ just copier::copy
```

```{code-block} shell
# Create a copier answers file
[no-cd]
copy TEMPLATE_PATH DESTINATION_PATH=".":
    uv run copier copy --trust {{ TEMPLATE_PATH }} {{ DESTINATION_PATH }}
```

### copier::recopy

```{code-block} shell
:class: copy

$ just copier::recopy
```

```{code-block} shell
# Recopy the project from the original template
[no-cd]
recopy ANSWERS_FILE *ARGS:
    uv run copier recopy --trust --answers-file {{ ANSWERS_FILE }} {{ ARGS }}
```

### copier::recopy-all

```{code-block} shell
:class: copy

$ just copier::recopy-all
```

```{code-block} shell
# Loop through all answers files and recopy the project using copier
[no-cd]
@recopy-all *ARGS:
    for file in `ls .copier/`; do just copier recopy .copier/$file "{{ ARGS }}"; done
```

### copier::update

```{code-block} shell
:class: copy

$ just copier::update
```

```{code-block} shell
# Update the project using a copier answers file
[no-cd]
update ANSWERS_FILE *ARGS:
    uv run copier update --trust --answers-file {{ ANSWERS_FILE }} {{ ARGS }}
```

### copier::update-all

```{code-block} shell
:class: copy

$ just copier::update-all
```

```{code-block} shell
# Loop through all answers files and update the project using copier
[no-cd]
@update-all *ARGS:
    for file in `ls .copier/`; do just copier update .copier/$file "{{ ARGS }}"; done
```

### docs::build

```{code-block} shell
:class: copy

$ just docs::build
```

```{code-block} shell
# Build documentation using Sphinx
[no-cd]
build LOCATION="docs/_build/html": cog
    uv run --extra docs sphinx-build docs {{ LOCATION }}
```

### docs::serve

```{code-block} shell
:class: copy

$ just docs::serve
```

```{code-block} shell
# Serve documentation locally
[no-cd]
serve PORT="8000": cog
    #!/usr/bin/env sh
    HOST="localhost"
    if [ -f "/.dockerenv" ]; then
        HOST="0.0.0.0"
    fi
    uv run --extra docs sphinx-autobuild docs docs/_build/html --host "$HOST" --port {{ PORT }}
```

<!-- [[[end]]] -->
