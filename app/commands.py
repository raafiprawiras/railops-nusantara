"""Flask CLI commands."""

import click
from flask import current_app
from flask.cli import with_appcontext


def register_commands(app):
    """Register custom Flask CLI commands."""
    app.cli.add_command(seed_demo_command)


@click.command("seed-demo")
@click.option("--reset", is_flag=True, help="Hapus semua data lalu seed ulang (development only).")
@with_appcontext
def seed_demo_command(reset):
    """Seed demo data untuk RailOps Nusantara."""
    if reset:
        if not current_app.debug and not current_app.testing:
            click.echo("ERROR: --reset hanya tersedia di mode development (FLASK_DEBUG=1).")
            return

    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from scripts.seed_demo import seed_demo

    success = seed_demo(reset=reset, app=current_app._get_current_object())
    if success:
        click.echo("Selesai.")
    else:
        click.echo("Gagal. Periksa output di atas.")
