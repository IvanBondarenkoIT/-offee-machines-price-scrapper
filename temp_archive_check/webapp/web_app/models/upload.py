"""
Upload model - represents one data upload session
"""
from datetime import datetime
from web_app.database import db

class Upload(db.Model):
    """Upload session model - one upload per date"""
    __tablename__ = 'uploads'
    
    id = db.Column(db.Integer, primary_key=True)
    upload_date = db.Column(db.Date, unique=True, nullable=False, index=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    file_name = db.Column(db.String(255))
    total_products = db.Column(db.Integer)
    status = db.Column(db.String(50), default='completed')  # completed, processing, failed
    
    # Relationships
    products = db.relationship('Product', backref='upload', lazy='dynamic', cascade='all, delete-orphan')
    statistics = db.relationship('Statistic', backref='upload', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Upload {self.upload_date}>'

