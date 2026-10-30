
import sqlite3

DB_NAME = "restaurant.db"


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            price INTEGER NOT NULL,
            image TEXT NOT NULL,
            description TEXT DEFAULT '',
            available INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_number TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            order_notes TEXT,
            payment_method TEXT NOT NULL,
            total_price INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS order_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            menu_item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price INTEGER NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (menu_item_id) REFERENCES menu_items(id)
        );

        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            reservation_date TEXT NOT NULL,
            reservation_time TEXT NOT NULL,
            guest_count INTEGER NOT NULL,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Danh sách món ăn
    # Cấu trúc: tên, danh mục, giá, ảnh, mô tả
    dishes = [
        # Món khai vị
        (
            "Gỏi Cuốn Tôm Thịt",
            "Món Khai Vị",
            50000,
            "goicuon.jpg",
            "Gỏi cuốn tôm thịt tươi ngon"
        ),
        (
            "Súp Cua",
            "Món Khai Vị",
            45000,
            "supcua.jpg",
            "Súp cua nóng thơm ngon"
        ),
        (
            "Súp Bò",
            "Món Khai Vị",
            50000,
            "supbo.jpg",
            "Súp bò nóng thơm ngon"
        ),
        (
            "Chả Giò Hải Sản",
            "Món Khai Vị",
            65000,
            "chagio.jpg",
            "Chả giò hải sản giòn rụm"
        ),

        # Món chính
        (
            "Phở Bò",
            "Món Chính",
            65000,
            "phobo.jpg",
            "Phở bò truyền thống"
        ),
        (
            "Cơm Chiên Hải Sản",
            "Món Chính",
            70000,
            "comchien.jpg",
            "Cơm chiên hải sản"
        ),
        (
            "Gà Rán",
            "Món Chính",
            55000,
            "garan.jpg",
            "Gà rán giòn"
        ),
        (
            "Bánh Mì",
            "Món Chính",
            35000,
            "banhmi.jpg",
            "Bánh mì thơm ngon"
        ),
        (
            "Bún Chả",
            "Món Chính",
            60000,
            "buncha.jpg",
            "Bún chả Hà Nội"
        ),
        (
            "Bánh Canh Cua",
            "Món Chính",
            75000,
            "banhcanhcua.jpg",
            "Bánh canh cua"
        ),
        (
            "Cá Kho",
            "Món Chính",
            55000,
            "cakho.jpg",
            "Cá kho đậm đà"
        ),
        (
            "Mì Quảng",
            "Món Chính",
            60000,
            "miquang.jpg",
            "Mì Quảng truyền thống"
        ),
        (
            "Bún Đậu",
            "Món Chính",
            50000,
            "bundau.jpg",
            "Bún đậu đầy đủ"
        ),

        # Rau xanh và món trộn
        (
            "Nộm Hoa Chuối Tai Heo",
            "Rau Xanh & Món Trộn",
            55000,
            "nomhoachuoi.jpg",
            "Nộm hoa chuối tai heo thanh mát"
        ),

        # Đồ uống
        (
            "Nước Ép Dứa",
            "Đồ Uống",
            40000,
            "nuocep.jpg",
            "Nước ép dứa tươi"
        ),
        (
            "Trà Đào",
            "Đồ Uống",
            35000,
            "tradao.jpg",
            "Trà đào mát lạnh"
        ),
        (
            "Trà Sen",
            "Đồ Uống",
            40000,
            "trasen.jpg",
            "Trà sen thơm dịu"
        ),
        (
            "Cà Phê",
            "Đồ Uống",
            30000,
            "caphe.jpg",
            "Cà phê thơm ngon"
        )
    ]

    # Thêm món mới, không tạo trùng tên
    conn.executemany(
        """
        INSERT OR IGNORE INTO menu_items
        (name, category, price, image, description)
        VALUES (?, ?, ?, ?, ?)
        """,
        dishes
    )

    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()
    print("Đã khởi tạo cơ sở dữ liệu!")
