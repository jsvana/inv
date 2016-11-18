"""
Contains database-backed objects with convenience methods for fetching and
saving.
"""


import logging


import sqlite3


LOG = logging.getLogger(__name__)


class Object(object):
    """
    Generic SQLite-backed object
    """

    # Location of backing database
    DB_FILE = "inv.db"

    # Name of object's table
    TABLE = ""

    def __init__(self, *args, **kwargs):
        # Assume field values are presented in the same order as values
        if args:
            assert len(args) == len(self.fields())
            for name, value in zip(self.fields(), args):
                setattr(self, name, value)

        for name, value in kwargs.items():
            setattr(self, name, value)

    @classmethod
    def fields(cls):
        """
        Returns a dictionary of {field_name: field_type} for the SQLite table
        structure.

        Must be implemented by children.
        """
        raise NotImplementedError()

    @property
    def field_values(self):
        """
        Returns a dictionary of {field_name: field_value or None} for the object
        from the database.
        """
        values = {}
        for name in self.fields():
            values[name] = getattr(self, name, None)
        return values

    @classmethod
    def enum_field(cls, name, field_type, choices):
        """
        Builds the SQLite string for an enum field
        """
        return "{} CHECK({} IN ({}))".format(
            field_type,
            name,
            ",".join(["'{}'".format(c) for c in choices])
        )

    def save(self):
        """
        Saves the object into the database.
        """
        keys, values = list(zip(*self.field_values.items()))

        sql = "INSERT INTO `{}` ({}) VALUES ({})".format(
            self.TABLE,
            ",".join(["`{}`".format(k) for k in keys]),
            ",".join(["?"] * len(values)),
        )
        LOG.debug("[INSERT] " + sql)
        with sqlite3.connect(self.DB_FILE) as conn:
            conn.execute(sql, values)

    @classmethod
    def create_table(cls):
        """
        Creates the proper table structure in the database.
        """
        sql = "CREATE TABLE IF NOT EXISTS `{}` ({})".format(
            cls.TABLE,
            ",".join([
                "`{}` {}".format(k, v) for k, v in cls.fields().items()
            ]),
        )
        LOG.debug("[CREATE] " + sql)
        with sqlite3.connect(cls.DB_FILE) as conn:
            conn.execute(sql)

    @classmethod
    def get(cls, **constraints):
        """
        Gets all rows in the object's table with optional constraints.
        """
        sql = "SELECT {} FROM `{}`".format(
            ",".join(["`{}`".format(k) for k in cls.fields().keys()]),
            cls.TABLE,
        )

        values = []
        if constraints:
            sql += " WHERE"
            for key, value in constraints.items():
                sql += " `{}` ".format(key)
                if value is None:
                    sql += "IS NULL"
                else:
                    sql += "= ?"
                    values.append(value)

        LOG.debug("[SELECT] " + sql)

        with sqlite3.connect(cls.DB_FILE) as conn:
            cur = conn.cursor()
            cur.execute(sql, values)
            for row in cur.fetchall():
                yield cls(*row)

    @classmethod
    def get_one(cls, **constraints):
        """
        Gets a specific row from the database with constraints or None.
        """
        try:
            row = next(cls.get(**constraints))
        except StopIteration:
            return None

        return row

    def __str__(self):
        return " ".join(
            [
                "{}:{}".format(k, v)
                for k, v in sorted(self.field_values.items())
            ]
        )


class Keyboard(Object):
    """
    Represents a keyboard in the database.
    """

    TABLE = "keyboards"

    FORM_FACTORS = [
        "full",
        "tkl",
        "60%",
        "40%",
    ]

    @classmethod
    def fields(cls):
        """
        See Object.fields().
        """
        return {
            "make": "TEXT",
            "model": "TEXT",
            "form_factor": cls.enum_field(
                "form_factor",
                "TEXT",
                cls.FORM_FACTORS,
            ),
            "serial": "TEXT PRIMARY KEY",
        }

    @property
    def keycaps(self):
        return KeycapSet.get_one(keyboard_serial=self.serial)


class KeycapSet(Object):
    """
    Represents a keycap set in the database.
    """

    TABLE = "keycaps"

    PROFILES = [
        "sa",
        "dsa",
        "cherry",
    ]

    @classmethod
    def fields(cls):
        """
        See Object.fields().
        """
        return {
            "name": "TEXT",
            "profile": cls.enum_field(
                "profile",
                "TEXT",
                cls.PROFILES,
            ),
            "keyboard_serial": "TEXT",
        }
