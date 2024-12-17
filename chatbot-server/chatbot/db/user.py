from sqlmodel import Session, select
from .models import User

def create_user(session: Session, email: str, password: str) -> User:
    user = User(email=email, password=password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def get_user_by_email(session: Session, email: str) -> Optional[User]:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()

def delete_user(session: Session, user_id: UUID) -> bool:
    user = session.get(User, user_id)
    if user:
        session.delete(user)
        session.commit()
        return True
    return False

def update_user(session: Session, user_id: UUID, email: Optional[str] = None, password: Optional[str] = None) -> Optional[User]:
    user = session.get(User, user_id)
    if user:
        if email:
            user.email = email
        if password:
            user.password = password
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    return None

