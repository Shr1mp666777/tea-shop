"""ระบบบริหารจัดการร้านชาเย็น (Streamlit Web Application)

ใช้หลัก OOP ประกอบด้วย 3 คลาสหลัก: Product, Customer และ Order
เมธอดของคลาสไม่ใช้ print()/input() โดยตรง แต่คืนค่าข้อความหรือข้อมูลกลับมา
เพื่อให้ส่วนติดต่อผู้ใช้ (Streamlit) นำไปแสดงผลเอง

วิธีรัน:  streamlit run app.py
"""

import pandas as pd
import streamlit as st

# รายการ Add-on: หมายเลข -> (ชื่อ, ราคาเพิ่ม)
ADDONS = {
    1: ("แยมสตรอวเบอรี่", 5),
    2: ("ครีมชีส", 20),
}

# เมนูเริ่มต้น: ชื่อเครื่องดื่ม แก้วละ 50 บาท
BASE_PRICE = 50
DEFAULT_STOCK = 20
LOW_STOCK = 5
MAX_RESTOCK = 999
MENU_NAMES = ["ชาไทย", "ชานม", "โกโก้", "มัทฉะ", "นมสดสตรอวเบอรี่"]

MODE_OLD = "ลูกค้าเดิม"
MODE_NEW = "ลูกค้าใหม่"
MODE_GUEST = "ลูกค้าทั่วไป (ไม่เก็บข้อมูล)"
GUEST_NAME = "ลูกค้าทั่วไป"


# ---------------------------------------------------------------------------
# คลาสตามข้อกำหนด OOP
# ---------------------------------------------------------------------------

class Product:
    """คลาสสินค้า (เครื่องดื่ม)"""

    def __init__(self, name, base_price, stock):
        self.name = name              # ชื่อเครื่องดื่ม
        self.base_price = base_price  # ราคาเริ่มต้นต่อแก้ว
        self.stock = stock            # จำนวนคงเหลือในสต็อก

    def display_info(self):
        """คืนข้อความรายละเอียดสินค้า"""
        status = " (หมด)" if self.stock <= 0 else ""
        return (f"{self.name} - {self.base_price} บาท | "
                f"คงเหลือ {self.stock} แก้ว{status}")

    def update_stock(self, quantity):
        """ตัดสต็อกตามจำนวนที่ระบุ

        คืนค่า True ถ้าสต็อกเพียงพอและตัดสำเร็จ, False ถ้าไม่เพียงพอ
        """
        if quantity <= 0 or quantity > self.stock:
            return False
        self.stock -= quantity
        return True

    def add_stock(self, quantity):
        """เติมสต็อกตามจำนวนที่ระบุ คืนค่า True ถ้าเติมสำเร็จ"""
        if quantity <= 0:
            return False
        self.stock += quantity
        return True


class Customer:
    """คลาสลูกค้า"""

    def __init__(self, name, phone, total_spent=0):
        self.name = name                # ชื่อลูกค้า
        self.phone = phone              # เบอร์โทรศัพท์
        self.total_spent = total_spent  # ยอดซื้อสะสม

    def add_spending(self, amount):
        """บันทึกยอดซื้อสะสมของลูกค้า"""
        if amount > 0:
            self.total_spent += amount

    def display_customer_info(self):
        """คืนข้อความข้อมูลลูกค้าและยอดสะสม"""
        return (f"{self.name} | โทร {self.phone} | "
                f"ยอดสะสม {self.total_spent:,.2f} บาท")

    def is_member(self):
        """เป็นสมาชิกหรือไม่ (ลูกค้าทั่วไปไม่มีเบอร์โทร ไม่เก็บข้อมูล)"""
        return bool(self.phone)

    def display_label(self):
        """คืนข้อความชื่อลูกค้าสำหรับแสดงในตะกร้าและใบเสร็จ"""
        if self.is_member():
            return f"{self.name} ({self.phone})"
        return self.name


class Order:
    """คลาสคำสั่งซื้อ (ตะกร้าสินค้าของลูกค้าหนึ่งคน)"""

    def __init__(self, customer, items=None, total_price=0):
        self.customer = customer        # ลูกค้าที่สั่ง
        self.items = items if items is not None else []  # รายการที่เลือก
        self.total_price = total_price  # ราคารวมสุทธิ

    def reserved_quantity(self, product):
        """จำนวนของสินค้านี้ที่อยู่ในตะกร้าแล้ว (ใช้เช็กสต็อกร่วมกับของใหม่)"""
        return sum(item["quantity"] for item in self.items
                   if item["product"] is product)

    def add_item(self, product, addon_ids, quantity):
        """เพิ่มเครื่องดื่มพร้อม Add-on ลงออเดอร์ และคำนวณราคา

        คืนค่า True ถ้าเพิ่มสำเร็จ, False ถ้าสต็อกไม่เพียงพอ
        """
        available = product.stock - self.reserved_quantity(product)
        if quantity <= 0 or quantity > available:
            return False

        addons = [ADDONS[i] for i in addon_ids]
        unit_price = product.base_price + sum(price for _, price in addons)
        self.items.append({
            "product": product,
            "addons": addons,
            "quantity": quantity,
            "unit_price": unit_price,
        })
        self.total_price = self.calculate_total()
        return True

    def calculate_total(self):
        """คำนวณราคารวมสุทธิของทุกรายการ"""
        return sum(i["unit_price"] * i["quantity"] for i in self.items)

    def generate_receipt(self):
        """คำนวณราคารวมและคืนข้อความใบเสร็จรับเงิน"""
        self.total_price = self.calculate_total()
        line = "=" * 44
        lines = [
            line,
            "      ร้านชาเย็น - ใบเสร็จรับเงิน",
            line,
            f"ลูกค้า: {self.customer.display_label()}",
            "-" * 44,
        ]
        for item in self.items:
            subtotal = item["unit_price"] * item["quantity"]
            lines.append(f"{item['product'].name} x{item['quantity']}"
                         f"  @{item['unit_price']}  = {subtotal} บาท")
            for addon_name, addon_price in item["addons"]:
                lines.append(f"    + {addon_name} (+{addon_price})")
        lines += [
            "-" * 44,
            f"ยอดรวมสุทธิ: {self.total_price:,.2f} บาท",
            line,
            "      ขอบคุณที่ใช้บริการค่ะ",
            line,
        ]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# ส่วนติดต่อผู้ใช้ (Streamlit)
# ---------------------------------------------------------------------------

def init_state():
    """สร้างข้อมูลเริ่มต้นเก็บใน session_state (คงอยู่ตลอดการใช้งานหน้าเว็บ)"""
    if "products" not in st.session_state:
        st.session_state.products = [
            Product(name, BASE_PRICE, DEFAULT_STOCK) for name in MENU_NAMES
        ]
        st.session_state.customers = []
        st.session_state.order = None
        st.session_state.last_receipt = None


def find_customers(keyword):
    """ค้นหาลูกค้าจากชื่อหรือเบอร์โทร (ไม่สนตัวพิมพ์เล็ก/ใหญ่)"""
    keyword = keyword.strip().lower()
    return [c for c in st.session_state.customers
            if keyword in c.name.lower() or keyword in c.phone]


def render_menu():
    """แท็บ 1: แสดงรายการเครื่องดื่มและสต็อกคงเหลือ"""
    st.subheader("เมนูเครื่องดื่มและสต็อก")
    products = st.session_state.products
    cols = st.columns(3)
    for i, product in enumerate(products):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"### 🧋 {product.name}")
                st.write(f"**{product.base_price} บาท** / แก้ว")
                st.progress(min(product.stock / DEFAULT_STOCK, 1.0),
                            text=f"คงเหลือ {product.stock} แก้ว")
                if product.stock <= 0:
                    st.error("สินค้าหมด")
                elif product.stock <= LOW_STOCK:
                    st.warning("ใกล้หมด")

    st.subheader("Add-on")
    for name, price in ADDONS.values():
        st.write(f"- {name} (+{price} บาท)")


def add_customer_form():
    """ฟอร์มเพิ่มลูกค้าใหม่ (ถ้าเบอร์ซ้ำจะใช้ลูกค้าเดิม)"""
    customers = st.session_state.customers
    with st.form("new_customer_form", clear_on_submit=True):
        name = st.text_input("ชื่อลูกค้า")
        phone = st.text_input("เบอร์โทรศัพท์ (9-10 หลัก)")
        submitted = st.form_submit_button("บันทึกลูกค้าใหม่")
    if not submitted:
        return

    name, phone = name.strip(), phone.strip()
    if not name:
        st.error("กรุณากรอกชื่อลูกค้า")
    elif not (phone.isdigit() and len(phone) in (9, 10)):
        st.error("เบอร์โทรต้องเป็นตัวเลข 9-10 หลัก")
    else:
        # เบอร์ซ้ำ = ลูกค้าเดิม เพื่อสะสมยอดต่อเนื่อง
        if not any(c.phone == phone for c in customers):
            customers.append(Customer(name, phone))
        # ให้รอบถัดไปเลือกลูกค้าคนนี้ให้เอง (ตั้งค่า widget หลังสร้างไม่ได้)
        st.session_state.pending_customer_phone = phone
        st.rerun()


def pick_existing_customer():
    """ค้นหาและเลือกลูกค้าเดิม คืนค่า Customer หรือ None"""
    total = len(st.session_state.customers)
    keyword = st.text_input("🔍 ค้นหาลูกค้า (ชื่อหรือเบอร์โทร)",
                            key="customer_search")
    matches = find_customers(keyword)
    st.caption(f"พบ {len(matches)} จาก {total} คน")
    if not matches:
        st.warning("ไม่พบลูกค้าที่ค้นหา ลองเปลี่ยนคำค้น "
                   f"หรือเลือก \"{MODE_NEW}\"")
        return None

    by_phone = {c.phone: c for c in matches}
    # ถ้าลูกค้าที่เลือกไว้หลุดจากผลค้นหา ให้ล้างค่า (กลับไปเลือกคนแรก)
    if st.session_state.get("customer_pick") not in by_phone:
        st.session_state.pop("customer_pick", None)
    phone = st.selectbox(
        "เลือกลูกค้า", list(by_phone),
        format_func=lambda p: f"{by_phone[p].name} ({p})",
        key="customer_pick")
    return by_phone[phone]


def select_customer():
    """เลือกลูกค้าเดิม (พร้อมค้นหา) หรือเพิ่มลูกค้าใหม่"""
    # ลูกค้าที่เพิ่งเพิ่ม: ตั้งค่า widget ก่อนสร้างในรอบนี้
    pending = st.session_state.pop("pending_customer_phone", None)
    if pending:
        st.session_state.customer_mode = MODE_OLD
        st.session_state.customer_search = ""
        st.session_state.customer_pick = pending

    modes = [MODE_NEW, MODE_GUEST]
    if st.session_state.customers:
        modes = [MODE_OLD] + modes
    else:
        st.info("ยังไม่มีลูกค้าสมาชิกในระบบ")
    # ถ้าค่าที่จำไว้ไม่อยู่ในตัวเลือก ให้ล้างเพื่อกลับไปค่าเริ่มต้น
    if st.session_state.get("customer_mode") not in modes:
        st.session_state.pop("customer_mode", None)
    mode = st.radio("ประเภทลูกค้า", modes, horizontal=True,
                    key="customer_mode", label_visibility="collapsed")

    if mode == MODE_OLD:
        return pick_existing_customer()
    if mode == MODE_GUEST:
        # ลูกค้าทั่วไป: ไม่ถูกเพิ่มลงรายชื่อลูกค้า และไม่สะสมยอด
        st.info("ไม่บันทึกข้อมูลลูกค้าและไม่สะสมยอด "
                "(ยังตัดสต็อกและออกใบเสร็จตามปกติ)")
        return Customer(GUEST_NAME, "")
    add_customer_form()
    return None


def render_order():
    """แท็บ 2: สั่งซื้อเครื่องดื่ม (เลือกลูกค้า -> เมนู -> Add-on -> ตะกร้า)"""
    st.subheader("สั่งซื้อเครื่องดื่ม")
    order = st.session_state.order
    if order is not None and order.items:
        customer = order.customer
        st.info(f"ตะกร้าของ **{customer.display_label()}** "
                "- ชำระเงินหรือล้างตะกร้าก่อนจึงจะเปลี่ยนลูกค้าได้")
    else:
        customer = select_customer()
        if customer is None:
            return

    with st.form("add_item_form"):
        # เลือกด้วยลำดับ แล้วดึงสินค้าตัวจริงจาก session_state
        # (selectbox อาจคืนสำเนาของ object ทำให้ตัดสต็อกไม่ถูกตัว)
        products = st.session_state.products
        product_idx = st.selectbox(
            "เมนู", range(len(products)),
            format_func=lambda i: products[i].display_info())
        addon_ids = st.multiselect(
            "Add-on (เลือกได้หลายอย่าง)", list(ADDONS),
            format_func=lambda i: f"{ADDONS[i][0]} (+{ADDONS[i][1]} บาท)")
        quantity = st.number_input("จำนวน (แก้ว)", min_value=1, max_value=99,
                                   value=1, step=1)
        submitted = st.form_submit_button("เพิ่มลงตะกร้า", type="primary")

    if submitted:
        product = products[product_idx]
        if st.session_state.order is None or not st.session_state.order.items:
            st.session_state.order = Order(customer)
        order = st.session_state.order
        st.session_state.last_receipt = None
        if order.add_item(product, sorted(addon_ids), int(quantity)):
            st.success(f"เพิ่ม {product.name} x{int(quantity)} ลงตะกร้าแล้ว "
                       f"(ยอดรวมปัจจุบัน {order.total_price} บาท) "
                       "- ไปที่แท็บ \"ตะกร้าและชำระเงิน\"")
        else:
            left = product.stock - order.reserved_quantity(product)
            st.error(f"สต็อกไม่เพียงพอ: {product.name} "
                     f"สั่งเพิ่มได้อีก {left} แก้ว")


def pay_order(order):
    """ยืนยันชำระเงิน: ตัดสต็อก บันทึกยอดสะสม และสร้างใบเสร็จ"""
    products = {item["product"].name: item["product"] for item in order.items}
    for product in products.values():
        if order.reserved_quantity(product) > product.stock:
            st.error(f"สต็อก {product.name} ไม่เพียงพอ กรุณาแก้ไขตะกร้า")
            return
    for item in order.items:
        item["product"].update_stock(item["quantity"])
    if order.customer.is_member():  # ลูกค้าทั่วไปไม่สะสมยอด
        order.customer.add_spending(order.calculate_total())
    st.session_state.last_receipt = order.generate_receipt()
    st.session_state.order = None
    st.rerun()


def render_checkout():
    """แท็บ 3: ตะกร้าและชำระเงิน"""
    st.subheader("ตะกร้าและชำระเงิน")
    if st.session_state.last_receipt:
        st.success("ชำระเงินสำเร็จ!")
        st.code(st.session_state.last_receipt, language=None)
        if st.button("ปิดใบเสร็จ"):
            st.session_state.last_receipt = None
            st.rerun()

    order = st.session_state.order
    if order is None or not order.items:
        if not st.session_state.last_receipt:
            st.info("ยังไม่มีรายการในตะกร้า กรุณาสั่งซื้อก่อน")
        return

    st.write(f"ลูกค้า: **{order.customer.display_label()}**")
    rows = [{
        "เมนู": item["product"].name,
        "Add-on": ", ".join(name for name, _ in item["addons"]) or "-",
        "จำนวน": item["quantity"],
        "ราคา/แก้ว": item["unit_price"],
        "รวม (บาท)": item["unit_price"] * item["quantity"],
    } for item in order.items]
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    st.metric("ยอดรวมสุทธิ", f"{order.calculate_total():,.2f} บาท")

    col_pay, col_clear = st.columns(2)
    if col_pay.button("ยืนยันชำระเงิน", type="primary", width="stretch"):
        pay_order(order)
    if col_clear.button("ล้างตะกร้า", width="stretch"):
        st.session_state.order = None
        st.rerun()


def render_customers():
    """แท็บ 4: แสดงข้อมูลลูกค้าและยอดซื้อสะสม (ค้นหาได้)"""
    st.subheader("ข้อมูลลูกค้าและยอดซื้อสะสม")
    customers = st.session_state.customers
    if not customers:
        st.info("ยังไม่มีข้อมูลลูกค้า")
        return
    col1, col2 = st.columns(2)
    col1.metric("จำนวนลูกค้า", len(customers))
    col2.metric("ยอดสะสมของสมาชิกรวม",
                f"{sum(c.total_spent for c in customers):,.2f} บาท")

    keyword = st.text_input("🔍 ค้นหาลูกค้า (ชื่อหรือเบอร์โทร)",
                            key="customer_table_search")
    matches = find_customers(keyword)
    st.caption(f"พบ {len(matches)} จาก {len(customers)} คน")
    rows = [{
        "ชื่อ": c.name,
        "เบอร์โทร": c.phone,
        "ยอดสะสม (บาท)": c.total_spent,
    } for c in sorted(matches, key=lambda c: c.total_spent, reverse=True)]
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")


def render_restock():
    """แท็บ 5: เติมสต็อกสินค้า"""
    st.subheader("เติมสต็อก")
    message = st.session_state.pop("restock_msg", None)
    if message:
        st.success(message)

    products = st.session_state.products
    with st.form("restock_form"):
        idx = st.selectbox("เมนูที่ต้องการเติม", range(len(products)),
                           format_func=lambda i: products[i].display_info())
        amount = st.number_input("จำนวนที่เติม (แก้ว)", min_value=1,
                                 max_value=MAX_RESTOCK, value=10, step=1)
        submitted = st.form_submit_button("เติมสต็อก", type="primary")
    if submitted:
        product = products[idx]
        if product.add_stock(int(amount)):
            st.session_state.restock_msg = (
                f"เติม {product.name} +{int(amount)} แก้ว "
                f"(คงเหลือ {product.stock} แก้ว)")
            st.rerun()

    st.divider()
    if st.button(f"เติมทุกเมนูให้ครบ {DEFAULT_STOCK} แก้ว"):
        added = 0
        for product in products:
            missing = DEFAULT_STOCK - product.stock
            if missing > 0 and product.add_stock(missing):
                added += missing
        st.session_state.restock_msg = (
            f"เติมสต็อกรวม {added} แก้ว" if added
            else f"ทุกเมนูมีสต็อกถึง {DEFAULT_STOCK} แก้วอยู่แล้ว")
        st.rerun()


def main():
    """จุดเริ่มต้นของเว็บแอป"""
    st.set_page_config(page_title="ร้านชาเย็น", page_icon="🧋",
                       layout="centered")
    init_state()
    st.title("🧋 ระบบจัดการร้านชาเย็น")
    st.caption("เครื่องดื่มแก้วละ 50 บาท | Add-on: แยมสตรอวเบอรี่ +5, ครีมชีส +20")

    tabs = st.tabs(["📋 เมนูและสต็อก", "🛒 สั่งซื้อ", "💳 ตะกร้าและชำระเงิน",
                    "👤 ลูกค้า", "📦 เติมสต็อก"])
    renderers = [render_menu, render_order, render_checkout,
                 render_customers, render_restock]
    for tab, render in zip(tabs, renderers):
        with tab:
            render()


if __name__ == "__main__":
    main()

