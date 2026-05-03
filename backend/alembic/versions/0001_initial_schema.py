"""Initial schema.

Revision ID: 0001
Revises:
Create Date: 2026-05-03
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── uuid_generate_v7() function ────────────────────────────────────────
    op.execute("""
        CREATE OR REPLACE FUNCTION uuid_generate_v7()
        RETURNS uuid
        LANGUAGE plpgsql
        VOLATILE
        AS $$
        DECLARE
            unix_ts_ms BYTEA;
            uuid_bytes BYTEA;
        BEGIN
            unix_ts_ms = substring(
                int8send(floor(extract(epoch from clock_timestamp()) * 1000)::bigint)
                from 3
            );
            uuid_bytes = uuid_send(gen_random_uuid());
            uuid_bytes = overlay(uuid_bytes placing unix_ts_ms from 1 for 6);
            uuid_bytes = set_byte(
                uuid_bytes, 6,
                (b'0111' || substring(get_byte(uuid_bytes, 6)::bit(8) from 5 for 4))::bit(8)::int
            );
            RETURN encode(uuid_bytes, 'hex')::uuid;
        END;
        $$;
    """)

    # ── updated_at trigger function ────────────────────────────────────────
    op.execute("""
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$;
    """)

    # ── projects ───────────────────────────────────────────────────────────
    op.create_table(
        "projects",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("uuid_generate_v7()")),
        sa.Column("slug", sa.Text(), nullable=False, unique=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False, server_default="active"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_projects_status", "projects", ["status"])
    op.create_index("ix_projects_created_at", "projects", ["created_at"])
    op.create_index("ix_projects_deleted_at", "projects", ["deleted_at"])
    op.execute(
        "CREATE TRIGGER trg_projects_updated_at BEFORE UPDATE ON projects FOR EACH ROW EXECUTE FUNCTION set_updated_at();"
    )

    # ── persons ────────────────────────────────────────────────────────────
    op.create_table(
        "persons",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("uuid_generate_v7()")),
        sa.Column("slug", sa.Text(), nullable=False, unique=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("email", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_persons_created_at", "persons", ["created_at"])
    op.create_index("ix_persons_deleted_at", "persons", ["deleted_at"])
    op.execute(
        "CREATE TRIGGER trg_persons_updated_at BEFORE UPDATE ON persons FOR EACH ROW EXECUTE FUNCTION set_updated_at();"
    )

    # ── meetings ───────────────────────────────────────────────────────────
    op.create_table(
        "meetings",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("uuid_generate_v7()")),
        sa.Column("slug", sa.Text(), nullable=False, unique=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "project_id",
            sa.Uuid(),
            sa.ForeignKey("projects.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_meetings_date", "meetings", ["date"])
    op.create_index("ix_meetings_project_id", "meetings", ["project_id"])
    op.create_index("ix_meetings_created_at", "meetings", ["created_at"])
    op.create_index("ix_meetings_deleted_at", "meetings", ["deleted_at"])
    op.execute(
        "CREATE TRIGGER trg_meetings_updated_at BEFORE UPDATE ON meetings FOR EACH ROW EXECUTE FUNCTION set_updated_at();"
    )

    # ── meeting_participants ───────────────────────────────────────────────
    op.create_table(
        "meeting_participants",
        sa.Column(
            "meeting_id",
            sa.Uuid(),
            sa.ForeignKey("meetings.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "person_id",
            sa.Uuid(),
            sa.ForeignKey("persons.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )

    # ── atoms ──────────────────────────────────────────────────────────────
    op.create_table(
        "atoms",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("uuid_generate_v7()")),
        sa.Column("slug", sa.Text(), nullable=False, unique=True),
        sa.Column("content", sa.Text(), nullable=False, server_default=""),
        sa.Column("content_json", JSONB(), nullable=True),
        sa.Column("type", sa.Text(), nullable=False, server_default="note"),
        sa.Column("status", sa.Text(), nullable=False, server_default="open"),
        sa.Column("priority", sa.Text(), nullable=False, server_default="medium"),
        sa.Column("inbox", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("reminder", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deadline_hard", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "project_id",
            sa.Uuid(),
            sa.ForeignKey("projects.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "meeting_id",
            sa.Uuid(),
            sa.ForeignKey("meetings.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "assigned_to",
            sa.Uuid(),
            sa.ForeignKey("persons.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_atoms_type", "atoms", ["type"])
    op.create_index("ix_atoms_status", "atoms", ["status"])
    op.create_index("ix_atoms_inbox", "atoms", ["inbox"])
    op.create_index("ix_atoms_project_id", "atoms", ["project_id"])
    op.create_index("ix_atoms_meeting_id", "atoms", ["meeting_id"])
    op.create_index("ix_atoms_assigned_to", "atoms", ["assigned_to"])
    op.create_index("ix_atoms_deadline", "atoms", ["deadline"])
    op.create_index("ix_atoms_reminder", "atoms", ["reminder"])
    op.create_index("ix_atoms_created_at", "atoms", ["created_at"])
    op.create_index("ix_atoms_deleted_at", "atoms", ["deleted_at"])
    # GIN index for German fulltext search
    op.execute(
        "CREATE INDEX ix_atoms_content_fts ON atoms USING GIN (to_tsvector('german', content));"
    )
    op.execute(
        "CREATE TRIGGER trg_atoms_updated_at BEFORE UPDATE ON atoms FOR EACH ROW EXECUTE FUNCTION set_updated_at();"
    )

    # ── atom_persons ───────────────────────────────────────────────────────
    op.create_table(
        "atom_persons",
        sa.Column(
            "atom_id", sa.Uuid(), sa.ForeignKey("atoms.id", ondelete="CASCADE"), primary_key=True
        ),
        sa.Column(
            "person_id",
            sa.Uuid(),
            sa.ForeignKey("persons.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )

    # ── saved_filters ──────────────────────────────────────────────────────
    op.create_table(
        "saved_filters",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("uuid_generate_v7()")),
        sa.Column("slug", sa.Text(), nullable=False, unique=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("filter_json", JSONB(), nullable=False, server_default="{}"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_saved_filters_created_at", "saved_filters", ["created_at"])
    op.create_index("ix_saved_filters_deleted_at", "saved_filters", ["deleted_at"])
    op.execute(
        "CREATE TRIGGER trg_saved_filters_updated_at BEFORE UPDATE ON saved_filters FOR EACH ROW EXECUTE FUNCTION set_updated_at();"
    )

    # ── views ──────────────────────────────────────────────────────────────
    op.execute("""
        CREATE VIEW v_inbox AS
        SELECT * FROM atoms
        WHERE inbox = true AND deleted_at IS NULL
        ORDER BY created_at DESC;
    """)
    op.execute("""
        CREATE VIEW v_overdue_tasks AS
        SELECT * FROM atoms
        WHERE type = 'task'
          AND status NOT IN ('done', 'cancelled')
          AND deadline < now()
          AND deleted_at IS NULL
        ORDER BY deadline ASC;
    """)
    op.execute("""
        CREATE VIEW v_upcoming_reminders AS
        SELECT * FROM atoms
        WHERE reminder IS NOT NULL
          AND reminder > now()
          AND deleted_at IS NULL
        ORDER BY reminder ASC;
    """)
    op.execute("""
        CREATE VIEW v_open_tasks AS
        SELECT * FROM atoms
        WHERE type = 'task'
          AND status NOT IN ('done', 'cancelled')
          AND deleted_at IS NULL
        ORDER BY priority DESC, created_at DESC;
    """)


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS v_open_tasks;")
    op.execute("DROP VIEW IF EXISTS v_upcoming_reminders;")
    op.execute("DROP VIEW IF EXISTS v_overdue_tasks;")
    op.execute("DROP VIEW IF EXISTS v_inbox;")
    op.drop_table("atom_persons")
    op.drop_table("atoms")
    op.drop_table("meeting_participants")
    op.drop_table("meetings")
    op.drop_table("persons")
    op.drop_table("projects")
    op.drop_table("saved_filters")
    op.execute("DROP FUNCTION IF EXISTS set_updated_at();")
    op.execute("DROP FUNCTION IF EXISTS uuid_generate_v7();")
