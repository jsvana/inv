"""
inv is a simple keyboard inventory manager CLI.
"""


import argparse
import logging
import sys


from tabulate import tabulate


from .object import (
    Keyboard,
    KeycapSet,
)


LOG = logging.getLogger()
LOG.setLevel("INFO")
HANDLER = logging.StreamHandler()
HANDLER.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
LOG.addHandler(HANDLER)


def parse_args():
    """
    Sets up and parses CLI arguments.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Increase verbosity of output",
    )

    subparsers = parser.add_subparsers()

    show_parser = subparsers.add_parser(
        "show",
        help="Show a specific keyboard",
    )
    show_parser.set_defaults(function=cmd_show)
    show_parser.add_argument(
        "serial",
        help="Serial number of keyboard to show",
    )

    list_parser = subparsers.add_parser(
        "list",
        help="Show existing inventory",
    )
    list_parser.set_defaults(function=cmd_list)
    for field in sorted(Keyboard.fields()):
        list_parser.add_argument(
            "--" + field.replace("_", "-"),
            help="Filter on " + field,
        )

    add_parser = subparsers.add_parser(
        "add",
        help="Add new keyboard to inventory",
    )
    for field in sorted(Keyboard.required_fields()):
        add_parser.add_argument(
            field,
            help=field + " of keyboard",
        )
    for field in sorted(Keyboard.optional_fields()):
        add_parser.add_argument(
            "--" + field.replace("_", "-"),
            help=field + " of keyboard",
        )
    add_parser.set_defaults(function=cmd_add)

    add_keycaps_parser = subparsers.add_parser(
        "add-caps",
        help="Add new keycap set to inventory",
    )
    for field in sorted(KeycapSet.required_fields()):
        add_keycaps_parser.add_argument(
            field,
            help=field + " of keycap set",
        )
    for field in sorted(KeycapSet.optional_fields()):
        add_keycaps_parser.add_argument(
            "--" + field.replace("_", "-"),
            help=field + " of keycap set",
        )
    add_keycaps_parser.set_defaults(function=cmd_add_keycaps)

    return parser.parse_args()


def init_db():
    """
    Ensures database tables are created properly.
    """
    Keyboard.create_table()
    KeycapSet.create_table()


def cmd_show(args):
    """
    Shows a specific keyboard.
    """
    keyboard = Keyboard.get_one(serial=args.serial)
    if not keyboard:
        LOG.warning('No keyboard with serial "%s" found', args.serial)
        return False

    LOG.info(keyboard)

    return True


def cmd_list(args):
    """
    Shows all keyboards and keycaps.
    """
    headers = sorted(Keyboard.fields().keys())

    filters = {}
    for field in headers:
        val = getattr(args, field, None)
        if val:
            filters[field] = val

    rows = []
    for keyboard in Keyboard.get(**filters):
        row = [getattr(keyboard, h) for h in headers]

        caps = keyboard.keycaps
        row.append(caps.name if caps else "-")

        rows.append(row)

    if not rows:
        print("No keyboards, yet")
    else:
        print("Keyboards")
        print(tabulate(rows, headers=headers + ["keycaps"]))

    rows = []
    for caps in KeycapSet.get(keyboard_serial=None):
        rows.append([
            caps.name,
            caps.profile,
        ])

    if not rows:
        print("No keycap sets, yet")
        return True

    print("Keycap Sets")
    print(tabulate(rows, headers=["name", "profile"]))

    return True


def cmd_add(args):
    """
    Adds a new keyboard to the database.
    """
    values = {f: getattr(args, f) for f in sorted(Keyboard.fields())}

    Keyboard(**values).save()

    return True


def cmd_add_keycaps(args):
    """
    Adds a new keycap set to the database.
    """
    values = {f: getattr(args, f) for f in sorted(KeycapSet.fields())}

    KeycapSet(**values).save()

    return True


def main():
    """
    Entry point.
    """
    args = parse_args()

    if args.verbose:
        LOG.setLevel("DEBUG")

    init_db()

    print(Keyboard.required_fields())
    print(Keyboard.optional_fields())

    func = getattr(args, "function", None)
    if not func:
        LOG.error("No command provided")
        return False

    return func(args)


sys.exit(0 if main() else 1)
