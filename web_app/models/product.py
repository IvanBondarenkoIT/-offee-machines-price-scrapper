"""
Product model - represents a product in our inventory
"""
from web_app.database import db

class Product(db.Model):
    """Product model - our inventory products"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    upload_id = db.Column(db.Integer, db.ForeignKey('uploads.id', ondelete='CASCADE'), nullable=False, index=True)
    
    model = db.Column(db.String(100), index=True)
    name = db.Column(db.String(500))
    quantity = db.Column(db.Integer)
    our_price = db.Column(db.Numeric(10, 2))
    brand = db.Column(db.String(50), index=True)  # DeLonghi, Melitta, Nivona
    competitor_count = db.Column(db.Integer, default=0)
    
    # Relationships
    competitor_prices = db.relationship('CompetitorPrice', backref='product', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Product {self.model}>'
    
    def get_competitors_with_prices(self):
        """Get all competitors with their prices"""
        return {
            cp.competitor: {
                'price': float(cp.price) if cp.price else None,
                'regular_price': float(cp.regular_price) if cp.regular_price else None,
                'discount_price': float(cp.discount_price) if cp.discount_price else None,
                'has_discount': cp.has_discount,
                'url': cp.url
            }
            for cp in self.competitor_prices.all()
        }

