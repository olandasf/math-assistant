"""add BP 2022 achievement levels and global topics to problem_bank

Revision ID: a1b2c3d4e5f6
Revises: e4e5b26f65be
Create Date: 2026-03-16 12:00:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'e4e5b26f65be'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Pasiekimų lygis (A/B/C pagal BP 2022)
    op.add_column('problem_bank', sa.Column(
        'achievement_level',
        sa.Enum('A', 'B', 'C', name='achievementlevel'),
        nullable=True,
    ))
    op.create_index(
        op.f('ix_problem_bank_achievement_level'),
        'problem_bank', ['achievement_level'], unique=False
    )

    # Globali sritis (iš global_topics.py)
    op.add_column('problem_bank', sa.Column(
        'global_topic', sa.String(length=50), nullable=True,
    ))
    op.create_index(
        op.f('ix_problem_bank_global_topic'),
        'problem_bank', ['global_topic'], unique=False
    )

    # Globali potemė
    op.add_column('problem_bank', sa.Column(
        'global_subtopic', sa.String(length=100), nullable=True,
    ))
    op.create_index(
        op.f('ix_problem_bank_global_subtopic'),
        'problem_bank', ['global_subtopic'], unique=False
    )

    # Tikslinė klasė (spiralinis modelis)
    op.add_column('problem_bank', sa.Column(
        'target_grade', sa.Integer(), nullable=True,
    ))
    op.create_index(
        op.f('ix_problem_bank_target_grade'),
        'problem_bank', ['target_grade'], unique=False
    )

    # Kompetencijų žymos (JSON)
    op.add_column('problem_bank', sa.Column(
        'competency_tags', sa.Text(), nullable=True,
    ))

    # Ar tekstinis uždavinys
    op.add_column('problem_bank', sa.Column(
        'is_word_problem', sa.Boolean(), server_default='0', nullable=False,
    ))

    # Migruoti senus duomenis: EASY->A, MEDIUM->B, HARD->C
    op.execute("""
        UPDATE problem_bank SET achievement_level = 'A' WHERE difficulty = 'easy';
    """)
    op.execute("""
        UPDATE problem_bank SET achievement_level = 'B' WHERE difficulty = 'medium';
    """)
    op.execute("""
        UPDATE problem_bank SET achievement_level = 'C' WHERE difficulty = 'hard';
    """)


def downgrade() -> None:
    op.drop_column('problem_bank', 'is_word_problem')
    op.drop_column('problem_bank', 'competency_tags')
    op.drop_index(op.f('ix_problem_bank_target_grade'), table_name='problem_bank')
    op.drop_column('problem_bank', 'target_grade')
    op.drop_index(op.f('ix_problem_bank_global_subtopic'), table_name='problem_bank')
    op.drop_column('problem_bank', 'global_subtopic')
    op.drop_index(op.f('ix_problem_bank_global_topic'), table_name='problem_bank')
    op.drop_column('problem_bank', 'global_topic')
    op.drop_index(op.f('ix_problem_bank_achievement_level'), table_name='problem_bank')
    op.drop_column('problem_bank', 'achievement_level')
