"""
Easix CLI Command
"""
import sys


def main():
    """Easix command-line interface."""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                    Easix Admin Framework                   ║
║                      Version 1.0.0                         ║
╚═══════════════════════════════════════════════════════════╝

Usage:
    easix <command> [options]

Commands:
    install     Set up Easix in your Django project
    create      Create a new Easix component
    docs        Open documentation
    
Examples:
    easix install
    easix create widget MyWidget
    easix docs
    """)


if __name__ == "__main__":
    main()
