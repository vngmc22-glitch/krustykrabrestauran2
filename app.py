
from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import get_db, init_db

app = Flask(__name__)
app.secret_key = 'krusty_krab_secret_key'


# Trang chủ
@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')


# Trang thực đơn
@app.route('/menu')
@app.route('/menu.html')
def menu():
    cart = session.get('cart', [])

    # Tính tổng tiền
    total_price = sum(
        int(item['price']) * int(item['quantity'])
        for item in cart
    )

    return render_template(
        'menu.html',
        cart=cart,
        total_price=total_price
    )


# Trang liên hệ
@app.route('/contact')
@app.route('/contact.html')
def contact():
    return render_template('contact.html')


# Trang đặt bàn
@app.route('/reservation')
@app.route('/reservation.html')
def reservation():
    return render_template('reservation.html')


# Thêm món vào giỏ hàng
@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    item_name = request.form.get('item_name', '').strip()
    quantity = request.form.get('quantity', 1, type=int)

    if not item_name or quantity is None or quantity < 1 or quantity > 20:
        flash('Tên món hoặc số lượng không hợp lệ.')
        return redirect(url_for('menu'))

    conn = get_db()

    try:
        # Lấy món và giá trực tiếp từ database
        dish = conn.execute(
            '''
            SELECT name, price
            FROM menu_items
            WHERE name = ? AND available = 1
            ''',
            (item_name,)
        ).fetchone()

        if dish is None:
            flash('Không tìm thấy món ăn hoặc món đã hết.')
            return redirect(url_for('menu'))

        price = int(dish['price'])

        cart = session.get('cart', [])

        # Nếu món đã có trong giỏ thì cộng số lượng
        found = False

        for item in cart:
            if item.get('name') == item_name:
                item['quantity'] = int(item['quantity']) + quantity
                item['price'] = price
                found = True
                break

        # Nếu chưa có thì thêm món mới
        if not found:
            cart.append({
                'name': item_name,
                'price': price,
                'quantity': quantity
            })

        session['cart'] = cart
        session.modified = True

        flash(f'Đã thêm {item_name} vào phiếu gọi món.')

    finally:
        conn.close()

    return redirect(url_for('menu'))


# Gửi đơn hàng và lưu vào SQLite
@app.route('/submit-table-order', methods=['POST'])
def submit_table_order():
    cart = session.get('cart', [])

    table_number = request.form.get('table_number', '').strip()
    customer_name = request.form.get('customer_name', '').strip()
    order_notes = request.form.get('order_notes', '').strip()
    payment_method = request.form.get('payment_method', 'cash')

    if not cart:
        flash('Giỏ hàng đang trống.')
        return redirect(url_for('menu'))

    if not table_number or not customer_name:
        flash('Vui lòng nhập số bàn và tên khách.')
        return redirect(url_for('menu'))

    if payment_method not in ('cash', 'transfer'):
        payment_method = 'cash'

    conn = get_db()

    try:
        total_price = 0
        details = []

        # Kiểm tra lại từng món và lấy giá từ database
        for item in cart:
            name = item.get('name')
            quantity = int(item.get('quantity', 0))

            if quantity < 1 or quantity > 20:
                raise ValueError('Số lượng món không hợp lệ.')

            dish = conn.execute(
                '''
                SELECT id, name, price
                FROM menu_items
                WHERE name = ? AND available = 1
                ''',
                (name,)
            ).fetchone()

            if dish is None:
                raise ValueError(f'Món {name} không còn trong thực đơn.')

            price = int(dish['price'])
            total_price += price * quantity

            details.append({
                'id': dish['id'],
                'quantity': quantity,
                'price': price
            })

        # Lưu đơn hàng
        cursor = conn.execute(
            '''
            INSERT INTO orders
            (table_number, customer_name, order_notes,
             payment_method, total_price)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (
                table_number,
                customer_name,
                order_notes,
                payment_method,
                total_price
            )
        )

        order_id = cursor.lastrowid

        # Lưu chi tiết từng món
        for detail in details:
            conn.execute(
                '''
                INSERT INTO order_details
                (order_id, menu_item_id, quantity, unit_price)
                VALUES (?, ?, ?, ?)
                ''',
                (
                    order_id,
                    detail['id'],
                    detail['quantity'],
                    detail['price']
                )
            )

        conn.commit()

        session.pop('cart', None)

        flash(
            f'Đã lưu đơn hàng #{order_id}. '
            f'Tổng tiền: {total_price:,.0f} VNĐ.'
        )

    except (ValueError, TypeError) as error:
        conn.rollback()
        flash(str(error))

    except Exception:
        conn.rollback()
        app.logger.exception('Lỗi lưu đơn hàng')
        flash('Không thể lưu đơn hàng. Vui lòng kiểm tra database.')

    finally:
        conn.close()

    return redirect(url_for('menu'))


# Xóa món khỏi giỏ hàng
@app.route('/remove-from-cart', methods=['POST'])
def remove_from_cart():
    item_name = request.form.get('item_name', '').strip()

    cart = session.get('cart', [])

    cart = [
        item for item in cart
        if item.get('name') != item_name
    ]

    session['cart'] = cart
    session.modified = True

    flash('Đã xóa món khỏi phiếu gọi món.')

    return redirect(url_for('menu'))

app.secret_key = 'krusty_krab_secret_key'

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
