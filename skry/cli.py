"""Skry CLI."""
from __future__ import annotations

import os
from pathlib import Path

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

app = typer.Typer(no_args_is_help=True, add_completion=False)
console = Console()


def _env(k: str, d: str | None = None) -> str:
    v = os.environ.get(k, d)
    if v is None:
        console.print(f"[red]missing env var {k}[/]"); raise typer.Exit(1)
    return v


def _render(result: dict):
    console.print(f"[bold]{result['query']}[/]  [dim]vocab={result['vocab_mode']}[/]")
    t = Table()
    for col in ("name", "count", "mean_sim", "score", "docs", "evidence"):
        t.add_column(col)
    for e in result["entities"]:
        t.add_row(e["name"], str(e["count"]), f"{e['mean_sim']:.3f}", f"{e['score']:.3f}",
                  str(e["n_docs"]), ", ".join(str(c) for c in e["chunks"][:3]))
    console.print(t)


@app.command()
def look(
    name: str = typer.Argument(...),
    top: int = typer.Option(20, "--top"),
    chunks: int = typer.Option(60, "--chunks"),
):
    """Look at what one entity is woven into."""
    from skry import skry
    r = skry(
        _env("SKRY_DB_URL"),
        ollama_url=_env("SKRY_OLLAMA_URL"),
        embed_model=_env("SKRY_EMBED_MODEL"),
        query=name, top_chunks=chunks, top_entities=top,
    )
    _render(r)


@app.command()
def search(
    phrase: str = typer.Argument(...),
    top: int = typer.Option(20, "--top"),
    chunks: int = typer.Option(60, "--chunks"),
):
    """Like `look`, but the query is a phrase rather than an entity name."""
    from skry import skry
    r = skry(
        _env("SKRY_DB_URL"),
        ollama_url=_env("SKRY_OLLAMA_URL"),
        embed_model=_env("SKRY_EMBED_MODEL"),
        query=phrase, top_chunks=chunks, top_entities=top,
    )
    _render(r)


if __name__ == "__main__":
    app()
