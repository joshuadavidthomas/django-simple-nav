set dotenv-load := true
set unstable := true

mod docs ".just/documentation.just"

[private]
default:
    @just --list

[private]
fmt:
    @just --fmt
    @just docs fmt

[private]
nox SESSION *ARGS:
    uv run nox --session "{{ SESSION }}" -- "{{ ARGS }}"

bootstrap:
    uv python install
    uv sync --frozen

coverage:
    @just nox coverage

demo:
    @just nox demo

lint:
    uv run --with pre-commit-uv pre-commit run --all-files
    just fmt

lock *ARGS:
    uv lock {{ ARGS }}

test *ARGS:
    @just nox test {{ ARGS }}

testall *ARGS:
    @just nox tests {{ ARGS }}

types *ARGS:
    @just nox types {{ ARGS }}
