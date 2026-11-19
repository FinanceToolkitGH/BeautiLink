
import streamlit as st
import sqlite3
from pathlib import Path
from datetime import datetime

# ==========================================
# BEAUTILINK FOLDER
# ==========================================

BASE_DIR = Path(r"C:\Users\JAY\BeautiLink")
PIC_DIR = BASE_DIR / "images"
VIDEO_DIR = BASE_DIR / "videos"
DB = BASE_DIR / "bookings.db"

PIC_DIR.mkdir(exist_ok=True)
VIDEO_DIR.mkdir(exist_ok=True)

st.set_page_config(
    page_title="BeautiLink",
    page_icon="💅",
    layout="wide"
)

# ==========================================
# DATABASE
# ==========================================

def get_db():
    return sqlite3.connect(str(DB), check_same_thread=False)


def initialise_database():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT,
            phone TEXT,
            service TEXT,
            professional TEXT,
            appointment_date TEXT,
            location TEXT,
            status TEXT DEFAULT 'Pending'
        )
    """)

    cur.execute("PRAGMA table_info(bookings)")
    columns = [row[1] for row in cur.fetchall()]

    if "design_code" not in columns:
        cur.execute("ALTER TABLE bookings ADD COLUMN design_code TEXT")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS service_prices (
            service TEXT PRIMARY KEY,
            price REAL
        )
    """)

    for service, price in [
        ("Hair Braiding", 100),
        ("Nail Technology", 80),
        ("Manicure", 50),
        ("Pedicure", 60)
    ]:
        cur.execute(
            "INSERT OR IGNORE INTO service_prices VALUES (?, ?)",
            (service, price)
        )

    cur.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT,
            rating INTEGER,
            comment TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


initialise_database()

# ==========================================
# FIND ALL PICTURES AND VIDEOS
# ==========================================

def identify_category(filename):
    name = filename.lower()

    if any(x in name for x in [
        "braid", "cornrow", "twist", "knotless",
        "loc", "hair"
    ]):
        return "Hair Braiding", "HB"

    if any(x in name for x in [
        "manicure", "nailart", "nail_art", "nails"
    ]):
        return "Manicure", "MN"

    if any(x in name for x in ["pedicure", "foot"]):
        return "Pedicure", "PD"

    if "nailtechnology" in name or "nail_technology" in name:
        return "Nail Technology", "NT"

    return "Other Styles", "OT"


def get_designs():
    designs = []
    counters = {"HB": 0, "MN": 0, "PD": 0, "NT": 0, "OT": 0}

    image_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    video_extensions = {".mp4", ".mov", ".webm", ".m4v"}

    files = []

    for folder, extensions, media_type in [
        (PIC_DIR, image_extensions, "image"),
        (VIDEO_DIR, video_extensions, "video")
    ]:
        for file in folder.iterdir():
            if file.is_file() and file.suffix.lower() in extensions:
                files.append((file, media_type))

    files.sort(key=lambda x: x[0].name.lower())

    for file, media_type in files:
        category, prefix = identify_category(file.name)
        counters[prefix] += 1

        designs.append({
            "code": f"{prefix}{counters[prefix]:02d}",
            "name": file.stem.replace("_", " ").replace("-", " ").title(),
            "category": category,
            "type": media_type,
            "path": file
        })

    return designs


designs = get_designs()


def show_media(design):
    if design["type"] == "image":
        st.image(str(design["path"]), use_container_width=True)
    else:
        st.video(str(design["path"]))


def get_prices():
    conn = get_db()
    rows = conn.execute(
        "SELECT service, price FROM service_prices"
    ).fetchall()
    conn.close()
    return dict(rows)


def designs_for_service(service):
    categories = {
        "Hair Braiding": ["Hair Braiding", "Other Styles"],
        "Manicure": ["Manicure", "Other Styles"],
        "Pedicure": ["Pedicure", "Other Styles"],
        "Nail Technology": ["Nail Technology", "Manicure", "Other Styles"]
    }

    return [
        d for d in designs
        if d["category"] in categories.get(service, [])
    ]


# ==========================================
# WEBSITE DESIGN
# ==========================================

st.markdown("""
<style>
.stApp {
    background-color: #fffaf8;
}
h1, h2, h3 {
    color: #71394f;
}
.stButton > button {
    background-color: #9b536b;
    color: white;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# HEADER AND MENU
# ==========================================

st.title("🌸 BeautiLink")
st.caption("Connecting You to Beauty")
st.markdown("---")

pages = [
    "Home",
    "Our Services",
    "Gallery",
    "Book Appointment",
    "Check Booking",
    "Customer Reviews",
    "Admin Dashboard"
]

page = st.sidebar.radio("Navigate BeautiLink", pages)

# ==========================================
# HOME PAGE
# ==========================================

if page == "Home":

    st.header("Welcome to BeautiLink")

    st.write("""
    BeautiLink is an online beauty and personal care platform
    connecting customers with professional beauty service providers.

    Discover beautiful styles, explore our services and request
    appointments conveniently.
    """)

    st.subheader("Explore Our Beauty Styles")

    homepage_images = sorted([
        f for f in PIC_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in
        {".jpg", ".jpeg", ".png", ".webp"}
    ])

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 💇🏽‍♀️ Hair Braiding")

        braids = [
            f for f in homepage_images
            if "braid" in f.name.lower()
            or "cornrow" in f.name.lower()
        ]

        if braids:
            st.image(str(braids[0]), use_container_width=True)
        elif homepage_images:
            st.image(str(homepage_images[0]), use_container_width=True)
        else:
            st.info("Add pictures to the images folder.")

        st.caption("Explore our beautiful hair braiding styles.")

    with col2:
        st.markdown("### 💅 Manicure")

        manicures = [
            f for f in homepage_images
            if "manicure" in f.name.lower()
            or "nail" in f.name.lower()
        ]

        if manicures:
            st.image(str(manicures[0]), use_container_width=True)
        elif len(homepage_images) >= 2:
            st.image(str(homepage_images[1]), use_container_width=True)
        else:
            st.info("Add another picture to the images folder.")

        st.caption("Discover beautiful manicure designs.")

    st.divider()

    st.subheader("Why Choose BeautiLink?")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("### 💇")
        st.write("Explore different beauty styles.")

    with c2:
        st.markdown("### 📅")
        st.write("Request appointments easily.")

    with c3:
        st.markdown("### 📍")
        st.write("Choose your preferred service location.")

    st.divider()

    st.subheader("Your Beauty, Your Choice")
    st.write("""
    Browse available designs, select your preferred style
    and connect with beauty professionals through BeautiLink.
    """)

# ==========================================
# SERVICES
# ==========================================

elif page == "Our Services":

    st.header("Our Beauty Services")

    prices = get_prices()

    descriptions = {
        "Hair Braiding": "Explore different braiding styles and professional hair services.",
        "Nail Technology": "Discover nail care and nail enhancement services.",
        "Manicure": "Enjoy professional hand and nail care.",
        "Pedicure": "Enjoy professional foot and toenail care."
    }

    for service, price in prices.items():

        st.subheader(service)
        st.write(descriptions.get(service, "Professional beauty service."))
        st.write(f"Starting price: GH₵{price:.2f}")

        matching = designs_for_service(service)

        if matching:
            cols = st.columns(min(3, len(matching)))

            for i, design in enumerate(matching[:3]):
                with cols[i]:
                    show_media(design)
                    st.caption(f"{design['code']} - {design['name']}")

        st.divider()

# ==========================================
# GALLERY
# ==========================================

elif page == "Gallery":

    st.header("BeautiLink Design Gallery")
    st.write("Explore our available beauty pictures and videos.")

    categories = [
        "All Designs",
        "Hair Braiding",
        "Manicure",
        "Pedicure",
        "Nail Technology",
        "Other Styles"
    ]

    selected_category = st.selectbox(
        "Choose a category",
        categories
    )

    filtered = designs if selected_category == "All Designs" else [
        d for d in designs if d["category"] == selected_category
    ]

    if not filtered:
        st.info("No files found. Please check your images and videos folders.")

    else:
        cols = st.columns(3)

        for i, design in enumerate(filtered):
            with cols[i % 3]:
                show_media(design)
                st.markdown(f"**{design['code']} - {design['name']}**")
                st.caption(f"{design['category']} | {design['type']}")

# ==========================================
# BOOK APPOINTMENT
# ==========================================

elif page == "Book Appointment":

    st.header("Book Your Beauty Appointment")

    prices = get_prices()

    service = st.selectbox(
        "Choose a service",
        list(prices.keys())
    )

    st.write(f"Starting price: GH₵{prices[service]:.2f}")

    available = designs_for_service(service)
    selected_code = None

    if available:
        st.subheader("Choose Your Preferred Design")

        options = {
            f"{d['code']} - {d['name']}": d
            for d in available
        }

        choice = st.selectbox(
            "Select your design",
            list(options.keys())
        )

        selected = options[choice]
        selected_code = selected["code"]

        show_media(selected)
        st.success(f"Selected design: {selected_code}")

    else:
        st.info("No designs are currently available for this service.")

    with st.form("booking_form"):

        customer = st.text_input("Your full name")
        phone = st.text_input("Phone number")
        professional = st.text_input("Preferred professional (optional)")
        appointment_date = st.date_input("Preferred appointment date")

        location = st.selectbox(
            "Where would you like the service?",
            [
                "At the beauty centre",
                "At my home",
                "At my workplace",
                "At my university/campus",
                "Other location"
            ]
        )

        other_location = st.text_input(
            "Enter your location"
        ) if location == "Other location" else ""

        submitted = st.form_submit_button("Submit Booking Request")

    if submitted:

        if not customer.strip() or not phone.strip():
            st.error("Please enter your name and phone number.")

        else:

            final_location = (
                other_location if location == "Other location" else location
            )

            conn = get_db()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO bookings
                (customer, phone, service, professional,
                 appointment_date, location, status, design_code)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                customer.strip(),
                phone.strip(),
                service,
                professional.strip(),
                str(appointment_date),
                final_location,
                "Pending",
                selected_code
            ))

            booking_id = cur.lastrowid

            conn.commit()
            conn.close()

            st.success("Your booking request has been submitted!")
            st.info(f"Your booking reference is BL{booking_id:05d}")
            st.write("Your booking is Pending. BeautiLink will contact you to confirm.")

# ==========================================
# CHECK BOOKING
# ==========================================

elif page == "Check Booking":

    st.header("Check Your Booking")

    reference = st.text_input("Enter booking reference, e.g. BL00001")
    phone = st.text_input("Enter your booking phone number")

    if st.button("Check Booking"):

        try:
            booking_id = int(
                reference.strip().upper().replace("BL", "")
            )

            conn = get_db()

            booking = conn.execute("""
                SELECT id, customer, service, professional,
                       appointment_date, location, status, design_code
                FROM bookings
                WHERE id = ? AND phone = ?
            """, (booking_id, phone.strip())).fetchone()

            conn.close()

            if booking:

                st.success("Booking found!")

                st.write(f"**Reference:** BL{booking[0]:05d}")
                st.write(f"**Customer:** {booking[1]}")
                st.write(f"**Service:** {booking[2]}")
                st.write(f"**Professional:** {booking[3] or 'Not specified'}")
                st.write(f"**Date:** {booking[4]}")
                st.write(f"**Location:** {booking[5]}")
                st.write(f"**Status:** {booking[6]}")
                st.write(f"**Selected design:** {booking[7] or 'Not selected'}")

            else:
                st.error("Booking not found. Check your details.")

        except ValueError:
            st.error("Enter a valid booking reference.")

# ==========================================
# CUSTOMER REVIEWS
# ==========================================

elif page == "Customer Reviews":

    st.header("Customer Reviews")

    with st.form("review_form"):

        customer = st.text_input("Your name")
        rating = st.slider("Rate your experience", 1, 5, 5)
        comment = st.text_area("Share your experience")

        submitted = st.form_submit_button("Submit Review")

    if submitted:

        if customer.strip() and comment.strip():

            conn = get_db()

            conn.execute("""
                INSERT INTO reviews
                (customer, rating, comment, created_at)
                VALUES (?, ?, ?, ?)
            """, (
                customer.strip(),
                rating,
                comment.strip(),
                datetime.now().strftime("%Y-%m-%d %H:%M")
            ))

            conn.commit()
            conn.close()

            st.success("Thank you for your review!")

        else:
            st.error("Please enter your name and review.")

    conn = get_db()

    reviews = conn.execute("""
        SELECT customer, rating, comment, created_at
        FROM reviews ORDER BY id DESC
    """).fetchall()

    conn.close()

    if reviews:

        average = sum(r[1] for r in reviews) / len(reviews)
        st.subheader(f"Average Rating: {average:.1f}/5")

        for review in reviews:
            st.write(f"**{review[0]}** - {'⭐' * review[1]}")
            st.write(review[2])
            st.caption(review[3])
            st.divider()

    else:
        st.info("Be the first to leave a review.")

# ==========================================
# ADMIN DASHBOARD
# ==========================================

elif page == "Admin Dashboard":

    st.header("BeautiLink Admin Dashboard")

    password = st.text_input("Admin password", type="password")

    if password == "beautilink123":

        st.success("Admin access granted.")

        st.subheader("Manage Service Prices")

        conn = get_db()
        current_prices = conn.execute(
            "SELECT service, price FROM service_prices"
        ).fetchall()
        conn.close()

        for service, price in current_prices:

            with st.form(f"price_{service}"):

                new_price = st.number_input(
                    f"{service} price (GH₵)",
                    min_value=0.0,
                    value=float(price),
                    step=5.0
                )

                update = st.form_submit_button(
                    f"Update {service} price"
                )

            if update:

                conn = get_db()
                conn.execute(
                    "UPDATE service_prices SET price = ? WHERE service = ?",
                    (new_price, service)
                )
                conn.commit()
                conn.close()

                st.success("Price updated.")
                st.rerun()

        st.divider()

        st.subheader("Manage Customer Bookings")

        conn = get_db()

        bookings = conn.execute("""
            SELECT id, customer, phone, service, professional,
                   appointment_date, location, status, design_code
            FROM bookings ORDER BY id DESC
        """).fetchall()

        conn.close()

        if bookings:

            for booking in bookings:

                booking_id = booking[0]

                with st.expander(
                    f"BL{booking_id:05d} - {booking[1]} - {booking[3]}"
                ):

                    st.write(f"Phone: {booking[2]}")
                    st.write(f"Professional: {booking[4] or 'Not specified'}")
                    st.write(f"Date: {booking[5]}")
                    st.write(f"Location: {booking[6]}")
                    st.write(f"Selected design: {booking[8] or 'Not selected'}")
                    st.write(f"Current status: {booking[7]}")

                    statuses = [
                        "Pending", "Confirmed", "Completed", "Cancelled"
                    ]

                    current = booking[7] if booking[7] in statuses else "Pending"

                    new_status = st.selectbox(
                        "Update booking status",
                        statuses,
                        index=statuses.index(current),
                        key=f"status_{booking_id}"
                    )

                    if st.button("Save Status", key=f"save_{booking_id}"):

                        conn = get_db()

                        conn.execute(
                            "UPDATE bookings SET status = ? WHERE id = ?",
                            (new_status, booking_id)
                        )

                        conn.commit()
                        conn.close()

                        st.success("Booking status updated.")
                        st.rerun()

        else:
            st.info("No bookings received yet.")

        st.divider()

        st.subheader("Design Library")
        st.write(f"Total pictures and videos: {len(designs)}")

        for design in designs:
            st.write(
                f"{design['code']} - {design['name']} - "
                f"{design['category']} - {design['type']}"
            )

        st.divider()

        st.subheader("Customer Reviews")

        conn = get_db()

        all_reviews = conn.execute("""
            SELECT customer, rating, comment, created_at
            FROM reviews ORDER BY id DESC
        """).fetchall()

        conn.close()

        for review in all_reviews:
            st.write(f"**{review[0]}** - {'⭐' * review[1]}")
            st.write(review[2])
            st.caption(review[3])
            st.divider()

    elif password:
        st.error("Incorrect password.")

# ==========================================
# FOOTER
# ==========================================

st.markdown("---")
st.caption("© BeautiLink | Connecting You to Beauty")


st.markdown("## Contact BeautiLink")
st.write("Call or WhatsApp us:")
st.link_button("WhatsApp: 059 319 8581", "https://wa.me/233593198581")
st.link_button("WhatsApp: 053 713 2650", "https://wa.me/233537132650")
st.write("Phone: 059 319 8581 / 053 713 2650")
