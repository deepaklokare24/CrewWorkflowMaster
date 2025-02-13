from typing import Dict, Any, List
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime
from sqlalchemy.orm import Session, DeclarativeBase
from sqlalchemy.ext.declarative import declarative_base
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

class Workflow(Base):
    __tablename__ = 'workflows'
    id = Column(String, primary_key=True)
    data = Column(JSON)
    state = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class Form(Base):
    __tablename__ = 'forms'
    id = Column(String, primary_key=True)
    data = Column(JSON)
    created_at = Column(DateTime)

class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(String, primary_key=True)
    data = Column(JSON)
    status = Column(String)
    created_at = Column(DateTime)

class Approval(Base):
    __tablename__ = 'approvals'
    id = Column(String, primary_key=True)
    data = Column(JSON)
    status = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

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

    def update_workflow_state(self, workflow_id: str, new_state: str) -> bool:
        with Session(self.engine) as session:
            workflow = session.query(Workflow).filter_by(id=workflow_id).first()
            if workflow:
                workflow.state = new_state
                workflow.updated_at = datetime.now()
                session.commit()
                logger.info(f"Updated workflow {workflow_id} state to {new_state}")
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