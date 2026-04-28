"""Sanic main entry point."""
import sys


def main():
    """Main entry point for Sanic CLI."""
    from sanic.cli.app import SanicCLI

    cli = SanicCLI()
    cli.run()


if __name__ == "__main__":
    main()
