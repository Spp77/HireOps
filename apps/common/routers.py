"""
apps/common/routers.py
─────────────────────────────────────────────────────────────────
Database router that sends all read (SELECT) queries to the
'replica' database alias when available.

Horizontal DB scaling: set DB_READ_HOST in .env to activate.
Only migrations and writes go to 'default' (primary).
"""
import random


class PrimaryReplicaRouter:
    """
    Routes:
    - All writes  → 'default' (primary)
    - All reads   → 'replica'  (can be a pool of replicas — extend as needed)
    - Migrations  → 'default' only
    """

    READ_DB    = 'replica'
    WRITE_DB   = 'default'

    def db_for_read(self, model, **hints):
        return self.READ_DB

    def db_for_write(self, model, **hints):
        return self.WRITE_DB

    def allow_relation(self, obj1, obj2, **hints):
        # Allow relations between both DBs (read-replica shares same schema)
        db_set = {self.READ_DB, self.WRITE_DB}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Only run migrations on the primary
        return db == self.WRITE_DB
