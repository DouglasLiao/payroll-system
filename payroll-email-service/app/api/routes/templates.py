from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.email_template import EmailTemplate
from app.schemas.template import (
    EmailTemplateCreate,
    EmailTemplateUpdate,
    EmailTemplateResponse,
)
from typing import List
from uuid import UUID

router = APIRouter()


@router.get("/", response_model=List[EmailTemplateResponse])
async def list_templates(db: Session = Depends(get_db)):
    """List all email templates"""
    templates = db.query(EmailTemplate).all()
    return templates


@router.get("/{template_name}", response_model=EmailTemplateResponse)
async def get_template(template_name: str, db: Session = Depends(get_db)):
    """Get template by name"""
    template = (
        db.query(EmailTemplate).filter(EmailTemplate.name == template_name).first()
    )

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return template


@router.post("/", response_model=EmailTemplateResponse, status_code=201)
async def create_template(template: EmailTemplateCreate, db: Session = Depends(get_db)):
    """Create a new email template"""

    # Check if template already exists
    existing = (
        db.query(EmailTemplate).filter(EmailTemplate.name == template.name).first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="Template already exists")

    # Create new template
    db_template = EmailTemplate(
        name=template.name,
        subject=template.subject,
        html_content=template.html_content,
        text_content=template.text_content,
        variables={"variables": template.variables} if template.variables else None,
    )

    db.add(db_template)
    db.commit()
    db.refresh(db_template)

    return db_template


@router.put("/{template_name}", response_model=EmailTemplateResponse)
async def update_template(
    template_name: str, template: EmailTemplateUpdate, db: Session = Depends(get_db)
):
    """Update an existing template"""

    db_template = (
        db.query(EmailTemplate).filter(EmailTemplate.name == template_name).first()
    )

    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Update fields
    if template.subject is not None:
        db_template.subject = template.subject
    if template.html_content is not None:
        db_template.html_content = template.html_content
    if template.text_content is not None:
        db_template.text_content = template.text_content
    if template.variables is not None:
        db_template.variables = {"variables": template.variables}

    db.commit()
    db.refresh(db_template)

    return db_template


@router.delete("/{template_name}", status_code=204)
async def delete_template(template_name: str, db: Session = Depends(get_db)):
    """Delete a template"""

    db_template = (
        db.query(EmailTemplate).filter(EmailTemplate.name == template_name).first()
    )

    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")

    db.delete(db_template)
    db.commit()

    return None
