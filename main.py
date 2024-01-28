from flask import Flask, request, render_template, redirect, abort, send_file
from sqlalchemy import exc
from models import *
import csv

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


@app.before_first_request
def create_table():
    db.create_all()


@app.route('/')
def index():
    return redirect('/view')


@app.route('/create/', methods=['GET', 'POST'])
def create():
    if request.method == 'GET':
        return render_template('create.html')

    if request.method == 'POST':
        sku = request.form['sku']
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        try:
            qty = int(request.form['qty'])
        except ValueError:
            return render_template('create.html', exc='qty')

        item = Item(sku=sku, name=name, description=description, price=price, qty=qty)

        try:
            db.session.add(item)
            db.session.commit()
        except exc.IntegrityError:
            return render_template('create.html', exc='integrity')
        except exc.StatementError:
            return render_template('create.html', exc='price')

        return redirect('/view')


@app.route('/view/', methods=['GET', 'POST'])
def view_list():
    if request.method == 'POST':
        outfile = open('inventory_export.csv', 'w', newline='')
        outcsv = csv.writer(outfile)
        records = db.session.query(Item).all()
        outcsv.writerow([column.name for column in Item.__mapper__.columns])
        [outcsv.writerow([getattr(curr, column.name) for column in Item.__mapper__.columns]) for curr in records]
        outfile.close()
        return send_file('inventory_export.csv', as_attachment=True)

    items = Item.query.all()
    return render_template('viewlist.html', items=items)


@app.route('/view/<int:sku>/')
def view_item(sku):
    item = Item.query.filter_by(sku=sku).first()
    if item:
        return render_template('viewitem.html', item=item)
    return f"Item {sku} is not found"


@app.route('/update/<int:sku>/', methods=['GET', 'POST'])
def update(sku):
    item = Item.query.filter_by(sku=sku).first()
    if request.method == 'POST':
        if item:
            sku = request.form['sku']
            name = request.form['name']
            description = request.form['description']
            try:
                price = float(request.form['price'])
            except ValueError:
                return render_template('update.html', item=item, exc='price')
            try:
                qty = int(request.form['qty'])
            except ValueError:
                return render_template('update.html', item=item, exc='qty')

            try:
                setattr(item, 'sku', sku)
                setattr(item, 'name', name)
                setattr(item, 'description', description)
                setattr(item, 'price', price)
                setattr(item, 'qty', qty)

                db.session.commit()
            except exc.IntegrityError:
                return render_template('update.html', item=item, exc='integrity')
            except (exc.StatementError, exc.InvalidRequestError) as e:
                return render_template('update.html', item=item, exc='price')

            return redirect(f'/view/')
        return f"Item {sku} is not found"

    return render_template('update.html', item=item)


@app.route('/delete/<int:sku>/', methods=['GET', 'POST'])
def delete(sku):
    item = Item.query.filter_by(sku=sku).first()
    if request.method == 'POST':
        if item:
            db.session.delete(item)
            db.session.commit()
            return redirect('/view')
        abort(404)

    return render_template('delete.html')


if __name__ == '__main__':
    app.run(host='localhost', port=5000)
