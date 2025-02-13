from typing import Dict, Any, List
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime, ForeignKey, Table
from sqlalchemy.orm import Session, DeclarativeBase, relationship
from sqlalchemy.ext.declarative import declarative_base
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

# User-Role association table
user_roles = Table('user_roles', Base.metadata,
    Column('user_id', String, ForeignKey('users.id')),
    Column('role_id', String, ForeignKey('roles.id'))
)

class User(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True)
    email = Column(String, unique=True)
    name = Column(String)
    department = Column(String)
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    created_at = Column(DateTime, default=datetime.now)

class Role(Base):
    __tablename__ = 'roles'
    id = Column(String, primary_key=True)
    name = Column(String, unique=True)
    users = relationship("User", secondary=user_roles, back_populates="roles")

class Workflow(Base):
    __tablename__ = 'workflows'
    id = Column(String, primary_key=True)
    lease_id = Column(String)
    workflow_type = Column(String)  # e.g., "lease_exit", "lease_renewal"
    data = Column(JSON)
    state = Column(String)
    current_step = Column(String)
    created_by = Column(String, ForeignKey('users.id'))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    forms = relationship("Form", back_populates="workflow")
    approvals = relationship("Approval", back_populates="workflow")

class Form(Base):
    __tablename__ = 'forms'
    id = Column(String, primary_key=True)
    workflow_id = Column(String, ForeignKey('workflows.id'))
    form_type = Column(String)  # e.g., "lease_requirements", "exit_requirements"
    submitted_by = Column(String, ForeignKey('users.id'))
    data = Column(JSON)
    documents = Column(JSON)  # Store document references
    created_at = Column(DateTime)
    workflow = relationship("Workflow", back_populates="forms")

class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(String, primary_key=True)
    workflow_id = Column(String, ForeignKey('workflows.id'))
    recipient_id = Column(String, ForeignKey('users.id'))
    data = Column(JSON)
    status = Column(String)
    created_at = Column(DateTime)

class Approval(Base):
    __tablename__ = 'approvals'
    id = Column(String, primary_key=True)
    workflow_id = Column(String, ForeignKey('workflows.id'))
    approver_id = Column(String, ForeignKey('users.id'))
    data = Column(JSON)
    status = Column(String)
    decision = Column(String)
    comments = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    workflow = relationship("Workflow", back_populates="approvals")

class Storage:
    """SQLite-based storage for the application"""

    def __init__(self):
        try:
            db_path = os.path.join(os.getcwd(), 'lease_exit.db')
            self.engine = create_engine(f'sqlite:///{db_path}')
            Base.metadata.create_all(self.engine)
            logger.info(f"SQLite database initialized at {db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise

    def create_workflow(self, data: Dict[str, Any]) -> str:
        workflow_id = f"wf_{datetime.now().timestamp()}"
        with Session(self.engine) as session:
            workflow = Workflow(
                id=workflow_id,
                data=data,
                state="draft",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(workflow)
            session.commit()
            logger.info(f"Created workflow with ID: {workflow_id}")
        return workflow_id

    def update_workflow_state(self, workflow_id: str, update_data: Dict[str, Any]) -> bool:
        """Update workflow state and metadata"""
        with Session(self.engine) as session:
            workflow = session.query(Workflow).filter_by(id=workflow_id).first()
            if workflow:
                if "state" in update_data:
                    workflow.state = update_data["state"]
                if "current_step" in update_data:
                    workflow.current_step = update_data["current_step"]
                if "crew_result" in update_data:
                    if not workflow.data:
                        workflow.data = {}
                    workflow.data["crew_result"] = update_data["crew_result"]
                workflow.updated_at = datetime.now()
                session.commit()
                logger.info(f"Updated workflow {workflow_id} state to {update_data}")
                return True
            return False

    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        with Session(self.engine) as session:
            workflow = session.query(Workflow).filter_by(id=workflow_id).first()
            if workflow:
                return {
                    "id": workflow.id,
                    "data": workflow.data,
                    "state": workflow.state,
                    "created_at": workflow.created_at.isoformat(),
                    "updated_at": workflow.updated_at.isoformat()
                }
            return {}

    def store_form(self, form_data: Dict[str, Any]) -> str:
        form_id = f"form_{datetime.now().timestamp()}"
        with Session(self.engine) as session:
            form = Form(
                id=form_id,
                data=form_data,
                created_at=datetime.now()
            )
            session.add(form)
            session.commit()
            logger.info(f"Stored form with ID: {form_id}")
        return form_id

    def get_form(self, form_id: str) -> Dict[str, Any]:
        with Session(self.engine) as session:
            form = session.query(Form).filter_by(id=form_id).first()
            if form:
                return {
                    "id": form.id,
                    "data": form.data,
                    "created_at": form.created_at.isoformat()
                }
            return {}

    def store_notification(self, notification_data: Dict[str, Any]) -> str:
        notification_id = f"notif_{datetime.now().timestamp()}"
        with Session(self.engine) as session:
            notification = Notification(
                id=notification_id,
                data=notification_data,
                status="sent",
                created_at=datetime.now()
            )
            session.add(notification)
            session.commit()
            logger.info(f"Stored notification with ID: {notification_id}")
        return notification_id

    def get_notification(self, notification_id: str) -> Dict[str, Any]:
        with Session(self.engine) as session:
            notification = session.query(Notification).filter_by(id=notification_id).first()
            if notification:
                return {
                    "id": notification.id,
                    "data": notification.data,
                    "status": notification.status,
                    "created_at": notification.created_at.isoformat()
                }
            return {}

    def create_approval(self, request_data: Dict[str, Any]) -> str:
        approval_id = f"appr_{datetime.now().timestamp()}"
        with Session(self.engine) as session:
            approval = Approval(
                id=approval_id,
                data=request_data,
                status="pending",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(approval)
            session.commit()
            logger.info(f"Created approval with ID: {approval_id}")
        return approval_id

    def update_approval(self, approval_id: str, decision: str) -> bool:
        with Session(self.engine) as session:
            approval = session.query(Approval).filter_by(id=approval_id).first()
            if approval:
                approval.status = decision
                approval.updated_at = datetime.now()
                session.commit()
                logger.info(f"Updated approval {approval_id} status to {decision}")
                return True
            return False

    def get_approval(self, approval_id: str) -> Dict[str, Any]:
        with Session(self.engine) as session:
            approval = session.query(Approval).filter_by(id=approval_id).first()
            if approval:
                return {
                    "id": approval.id,
                    "data": approval.data,
                    "status": approval.status,
                    "created_at": approval.created_at.isoformat(),
                    "updated_at": approval.updated_at.isoformat()
                }
            return {}

    def get_all_workflows(self) -> List[Dict[str, Any]]:
        """Retrieve all workflows from the database"""
        with Session(self.engine) as session:
            workflows = session.query(Workflow).all()
            return [
                {
                    "id": w.id,
                    "data": w.data,
                    "state": w.state,
                    "created_at": w.created_at.isoformat(),
                    "updated_at": w.updated_at.isoformat()
                }
                for w in workflows
            ]

    def get_workflow_progress(self, workflow_id: str) -> Dict[str, Any]:
        """Get detailed workflow progress information"""
        with Session(self.engine) as session:
            workflow = session.query(Workflow).filter_by(id=workflow_id).first()
            if not workflow:
                return {}

            # Get all forms for this workflow
            forms = session.query(Form).filter_by(workflow_id=workflow_id).all()
            
            # Get all approvals for this workflow
            approvals = session.query(Approval).filter_by(workflow_id=workflow_id).all()
            
            # Get all notifications for this workflow
            notifications = session.query(Notification).filter_by(workflow_id=workflow_id).all()
            
            return {
                "id": workflow.id,
                "state": workflow.state,
                "current_step": workflow.current_step,
                "data": workflow.data,
                "created_at": workflow.created_at.isoformat(),
                "updated_at": workflow.updated_at.isoformat(),
                "forms": [
                    {
                        "id": form.id,
                        "form_type": form.form_type,
                        "submitted_by": form.submitted_by,
                        "created_at": form.created_at.isoformat()
                    }
                    for form in forms
                ],
                "approvals": [
                    {
                        "id": approval.id,
                        "approver_id": approval.approver_id,
                        "status": approval.status,
                        "decision": approval.decision,
                        "comments": approval.comments,
                        "created_at": approval.created_at.isoformat()
                    }
                    for approval in approvals
                ],
                "notifications": [
                    {
                        "id": notification.id,
                        "recipient_id": notification.recipient_id,
                        "status": notification.status,
                        "created_at": notification.created_at.isoformat()
                    }
                    for notification in notifications
                ]
            }