"""
Database models
"""
from web_app.models.user import User
from web_app.models.upload import Upload
from web_app.models.product import Product
from web_app.models.competitor_price import CompetitorPrice
from web_app.models.statistic import Statistic

__all__ = ['User', 'Upload', 'Product', 'CompetitorPrice', 'Statistic']

