"""Internal CLI commands. Run with `uv run python -m app.entrypoints.cli <command>`."""
from __future__ import annotations

import argparse
import asyncio
import getpass
import sys

import sqlalchemy as sa

from app.companies.domain.models import Company
from app.shared.database.enums import UserRole
from app.shared.database.session import get_session_bg
from app.shared.security import hash_password
from app.users.domain.models import User


async def _seed_superadmin(email: str, password: str, company_name: str) -> None:
    async with get_session_bg() as db:
        # Refuse if any superadmin already exists — manual override required to add another.
        existing = await db.execute(
            sa.select(User).where(User.role == UserRole.SUPERADMIN).limit(1)
        )
        if existing.scalar_one_or_none() is not None:
            print("Refusing: a superadmin already exists.", file=sys.stderr)
            sys.exit(1)

        # Refuse if email already taken.
        existing_email = await db.execute(sa.select(User).where(User.email == email))
        if existing_email.scalar_one_or_none() is not None:
            print(f"Refusing: email {email!r} already in use.", file=sys.stderr)
            sys.exit(1)

        company = Company(name=company_name)
        db.add(company)
        await db.flush()  # populate company.id

        user = User(
            email=email,
            password_hash=await hash_password(password),
            role=UserRole.SUPERADMIN,
            full_name="Platform Superadmin",
            company_id=company.id,
        )
        db.add(user)
        await db.commit()

        print(f"✅  Superadmin created: {email}")
        print(f"    company: {company.name} ({company.id})")
        print(f"    user_id: {user.id}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="app.entrypoints.cli")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sa_cmd = sub.add_parser(
        "seed-superadmin",
        help="Create the first superadmin + platform admin company. "
             "Refuses if any superadmin already exists.",
    )
    sa_cmd.add_argument("--email", required=True)
    sa_cmd.add_argument(
        "--password",
        help="If omitted, prompts interactively (recommended — avoids shell history).",
    )
    sa_cmd.add_argument(
        "--company",
        default="Platform",
        help="Company name to create for this superadmin (default: 'Platform').",
    )

    args = parser.parse_args()

    if args.cmd == "seed-superadmin":
        password = args.password or getpass.getpass("Password: ")
        if not password:
            print("Password is required.", file=sys.stderr)
            sys.exit(1)
        asyncio.run(_seed_superadmin(args.email, password, args.company))


if __name__ == "__main__":
    main()
