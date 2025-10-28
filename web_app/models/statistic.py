"""
Statistic model - aggregated statistics for an upload
"""
from web_app.database import db

class Statistic(db.Model):
    """Statistics model - aggregated data for each upload"""
    __tablename__ = 'statistics'
    
    id = db.Column(db.Integer, primary_key=True)
    upload_id = db.Column(db.Integer, db.ForeignKey('uploads.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    
    total_value = db.Column(db.Numeric(12, 2))  # Total value of all products
    avg_price = db.Column(db.Numeric(10, 2))  # Average product price
    products_cheaper = db.Column(db.Integer)  # Products where we are cheaper
    products_expensive = db.Column(db.Integer)  # Products where we are more expensive
    products_no_competitors = db.Column(db.Integer)  # Products with no competitor data
    
    def __repr__(self):
        return f'<Statistic for upload {self.upload_id}>'
    
    def get_total_value_formatted(self):
        """Get formatted total value"""
        return f"{float(self.total_value):,.2f}" if self.total_value else "0.00"
    
    def get_avg_price_formatted(self):
        """Get formatted average price"""
        return f"{float(self.avg_price):,.2f}" if self.avg_price else "0.00"

