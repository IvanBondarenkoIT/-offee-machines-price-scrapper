"""
CompetitorPrice model - represents competitor's price for a product
"""
from web_app.database import db

class CompetitorPrice(db.Model):
    """Competitor price model - prices from different competitors"""
    __tablename__ = 'competitor_prices'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    
    competitor = db.Column(db.String(50), nullable=False, index=True)  # ALTA, KONTAKT, ELITE, etc.
    price = db.Column(db.Numeric(10, 2))  # Main price (discount if available, regular otherwise)
    regular_price = db.Column(db.Numeric(10, 2))
    discount_price = db.Column(db.Numeric(10, 2))
    has_discount = db.Column(db.Boolean, default=False)
    url = db.Column(db.Text)
    
    def __repr__(self):
        return f'<CompetitorPrice {self.competitor}: {self.price}>'
    
    def get_display_price(self):
        """Get formatted price for display"""
        if self.has_discount and self.regular_price and self.discount_price:
            return f"{float(self.regular_price):.2f} \\ {float(self.discount_price):.2f}"
        elif self.regular_price:
            return f"{float(self.regular_price):.2f}"
        elif self.price:
            return f"{float(self.price):.2f}"
        else:
            return "-"

