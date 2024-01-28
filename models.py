from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Item(db.Model):
    __tablename__ = "Item"

    id = db.Column(db.Integer(), primary_key=True)
    sku = db.Column(db.String(), unique=True)
    name = db.Column(db.String())
    description = db.Column(db.String())
    price = db.Column(db.DECIMAL(9, 2))
    qty = db.Column(db.Integer())

    def __init__(self, sku, name, description, price, qty):
        self.sku = sku
        self.name = name
        self.description = description
        self.price = price
        self.qty = qty

    def __repr__(self):
        return f"{self.name}:{self.sku}"
