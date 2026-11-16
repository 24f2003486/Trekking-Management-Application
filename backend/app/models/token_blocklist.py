"""TokenBlocklist model for revoked JWT access tokens."""
from datetime import datetime
from backend.app.extensions import db


class TokenBlocklist(db.Model):
    """Stores revoked JWT unique identifiers (jti) for secure logout."""
    
    __tablename__ = "token_blocklist"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    jti = db.Column(db.String(36), nullable=False, unique=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<TokenBlocklist id={self.id} jti='{self.jti}'>"

