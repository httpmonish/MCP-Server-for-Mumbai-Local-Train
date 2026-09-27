import csv
import io
import re
import secrets
import uuid
from typing import Dict, List, Set, Tuple

from email_validator import EmailNotValidError, validate_email
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.logger import get_logger
from ..core.security import hash_password
from ..models.auth import User, UserRole
from ..schemas.organizations import BulkImportErrorItem, BulkImportResponse, MemberResponse

logger = get_logger(__name__)

# Constants for Bulk CSV Ingestion
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
MAX_CSV_ROWS = 2000
FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def sanitize_csv_field(value: str) -> str:
    """Neutralize potential CSV/Spreadsheet formula injection payloads."""
    cleaned = value.strip()
    if cleaned and cleaned.startswith(FORMULA_PREFIXES):
        return f"'{cleaned}"
    return cleaned


class CsvImportService:
    @staticmethod
    async def process_csv_upload(
        db: AsyncSession,
        org_id: uuid.UUID,
        file: UploadFile,
    ) -> BulkImportResponse:
        """
        Validate, parse, sanitize, and bulk-import members from CSV file.
        Provides robust error handling and granular per-row audit reporting.
        """
        # 1. Check file extension & filename
        filename = file.filename or "unknown.csv"
        if not filename.lower().endswith(".csv"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file format. Uploaded file must have a .csv extension.",
            )

        # 2. Read content & validate file size
        content_bytes = await file.read()
        if len(content_bytes) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"CSV file exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB.",
            )

        if len(content_bytes) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded CSV file is empty.",
            )

        # 3. Decode UTF-8 (handling BOM)
        try:
            text_content = content_bytes.decode("utf-8-sig")
        except UnicodeDecodeError:
            try:
                text_content = content_bytes.decode("latin-1")
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to decode CSV content. Ensure the file is encoded in UTF-8.",
                )

        csv_file = io.StringIO(text_content)
        reader = csv.reader(csv_file)

        # 4. Parse header
        try:
            header = next(reader, None)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Malformed CSV header: {str(e)}",
            )

        if not header:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CSV file is empty or missing header row.",
            )

        # Normalize header column mapping
        header_map: Dict[str, int] = {}
        for idx, col in enumerate(header):
            col_normalized = col.strip().lower()
            header_map[col_normalized] = idx

        if "email" not in header_map:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CSV must contain an 'email' column.",
            )

        if "role" not in header_map:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CSV must contain a 'role' column.",
            )

        email_idx = header_map["email"]
        role_idx = header_map["role"]
        name_idx = header_map.get("name", header_map.get("full_name"))

        errors: List[BulkImportErrorItem] = []
        valid_rows_data: List[Dict] = []
        seen_emails_in_batch: Set[str] = set()

        row_num = 1  # Header is row 1, data starts at row 2

        # 5. Row validation loop
        for row in reader:
            row_num += 1
            if not row or all(not cell.strip() for cell in row):
                continue  # Skip completely blank lines

            if row_num - 1 > MAX_CSV_ROWS:
                errors.append(
                    BulkImportErrorItem(
                        row=row_num,
                        email=None,
                        error=f"Exceeded maximum limit of {MAX_CSV_ROWS} rows per import.",
                    )
                )
                break

            # Validate column bounds
            if len(row) <= max(email_idx, role_idx):
                errors.append(
                    BulkImportErrorItem(
                        row=row_num,
                        email=None,
                        error="Row has insufficient columns.",
                    )
                )
                continue

            raw_email = row[email_idx].strip()
            raw_role = row[role_idx].strip().upper()
            raw_name = row[name_idx].strip() if name_idx is not None and len(row) > name_idx else None

            # Validate Email
            if not raw_email:
                errors.append(
                    BulkImportErrorItem(
                        row=row_num,
                        email=None,
                        error="Missing email address.",
                    )
                )
                continue

            try:
                valid_info = validate_email(raw_email, check_deliverability=False)
                normalized_email = valid_info.normalized.lower()
            except EmailNotValidError:
                errors.append(
                    BulkImportErrorItem(
                        row=row_num,
                        email=raw_email,
                        error="Invalid email format.",
                    )
                )
                continue

            # Check Intra-batch duplicate
            if normalized_email in seen_emails_in_batch:
                errors.append(
                    BulkImportErrorItem(
                        row=row_num,
                        email=normalized_email,
                        error="Duplicate email found within the same CSV upload.",
                    )
                )
                continue
            seen_emails_in_batch.add(normalized_email)

            # Validate Role
            try:
                role_enum = UserRole(raw_role)
            except ValueError:
                errors.append(
                    BulkImportErrorItem(
                        row=row_num,
                        email=normalized_email,
                        error=f"Invalid role '{raw_role}'. Allowed roles: STUDENT, TEACHER, EMPLOYEE, HR_ADMIN, ORG_ADMIN.",
                    )
                )
                continue

            if role_enum == UserRole.PLATFORM_ADMIN:
                errors.append(
                    BulkImportErrorItem(
                        row=row_num,
                        email=normalized_email,
                        error="Assigning PLATFORM_ADMIN role is strictly prohibited.",
                    )
                )
                continue

            # Sanitize full name against CSV formula injection
            sanitized_name = sanitize_csv_field(raw_name) if raw_name else None

            valid_rows_data.append(
                {
                    "row": row_num,
                    "email": normalized_email,
                    "full_name": sanitized_name,
                    "role": role_enum,
                }
            )

        # 6. Database duplicate verification
        if valid_rows_data:
            candidate_emails = [item["email"] for item in valid_rows_data]
            stmt_existing = select(User.email).where(User.email.in_(candidate_emails))
            res_existing = await db.execute(stmt_existing)
            existing_db_emails = set(res_existing.scalars().all())
        else:
            existing_db_emails = set()

        rows_to_insert = []
        for item in valid_rows_data:
            if item["email"] in existing_db_emails:
                errors.append(
                    BulkImportErrorItem(
                        row=item["row"],
                        email=item["email"],
                        error="User with this email is already registered in the system.",
                    )
                )
            else:
                rows_to_insert.append(item)

        # 7. Insert valid users transactionally
        created_users: List[User] = []
        for item in rows_to_insert:
            temp_password = secrets.token_urlsafe(16)
            password_hash = hash_password(temp_password)

            user = User(
                id=uuid.uuid4(),
                org_id=org_id,
                email=item["email"],
                full_name=item["full_name"],
                password_hash=password_hash,
                role=item["role"],
                is_active=True,
                is_verified=False,
            )
            db.add(user)
            created_users.append(user)

        if created_users:
            await db.commit()
            for u in created_users:
                await db.refresh(u)

        total_processed = row_num - 1
        created_members = [MemberResponse.model_validate(u) for u in created_users]

        logger.info(
            "Bulk CSV import completed.",
            extra={
                "org_id": str(org_id),
                "total_rows": total_processed,
                "created_count": len(created_members),
                "error_count": len(errors),
            },
        )

        return BulkImportResponse(
            total_rows=total_processed,
            valid_rows=len(created_members),
            invalid_rows=len(errors),
            created_count=len(created_members),
            errors=errors,
            created_members=created_members,
        )
