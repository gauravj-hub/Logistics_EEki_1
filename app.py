import streamlit as st
import pandas as pd

st.set_page_config(page_title="Eeki Farms Vegetable Pricing", page_icon="🥬", layout="wide")

# --- INITIALIZATION ---
# Move rates to session state so we can add to them dynamically
if "veg_rates" not in st.session_state:
    st.session_state.veg_rates = {
        "Coriander": 9.58, "Yellow bellpepper": 6.32, "Red bellpepper": 6.26,
        "Spring onion": 7.32, "Chilli": 6.89, "Muskmelon": 6.60,
        "Green Bellpepper": 6.55, "Spinach": 5.71, "Parsley": 5.37,
        "Yellow candy": 4.73, "Bellpepper": 4.44, "Kale": 4.42,
        "Cauliflower": 4.37, "Lettuce": 4.23, "Basil": 4.20,
        "Tomato": 4.13, "Zucchini": 3.93, "Rocket": 3.79,
        "Pak choy": 3.79, "Mint": 3.62, "Cucumber": 3.62,
        "Cabbage": 3.27, "Broccoli": 2.04, "Radish": 0.95
    }

def calculate_charges(veg, weight):
    rate = st.session_state.veg_rates.get(veg, 0.00)
    return weight * rate

# --- SIDEBAR: ADD NEW CROP ---
with st.sidebar:
    st.header("🚜 Inventory Management")
    with st.form("add_crop_form"):
        new_veg = st.text_input("New Vegetable Name")
        new_rate = st.number_input("Rate (₹/kg)", min_value=0.0, step=0.1)
        if st.form_submit_button("➕ Add Crop to List"):
            if new_veg:
                st.session_state.veg_rates[new_veg] = new_rate
                st.success(f"Added {new_veg}!")
                st.rerun()

# --- HEADER ---
st.title("🥬 Eeki Farms Pricing & Logistics")

tab1, tab2, tab3 = st.tabs(["🧮 Quick Calc", "📦 Batch Calc", "📋 Quotes & Transport"])

# --- TAB 1: QUICK CALC ---
with tab1:
    st.subheader("Single Vegetable Calculator")
    col1, col2 = st.columns(2)
    with col1:
        vegetable = st.selectbox("Select Vegetable", list(st.session_state.veg_rates.keys()), key="single_sel")
    with col2:
        weight = st.number_input("Weight (KG)", min_value=0.1, value=50.0, key="single_w")
    
    rate = st.session_state.veg_rates[vegetable]
    charges = calculate_charges(vegetable, weight)
    
    c_a, c_b = st.columns(2)
    c_a.metric("Rate/kg", f"₹{rate:.2f}")
    c_b.metric("Total Cost", f"₹{charges:,.2f}")

# --- TAB 2: BATCH CALC ---
with tab2:
    st.subheader("Batch Calculator")
    if "batch_data" not in st.session_state:
        st.session_state.batch_data = pd.DataFrame()
    
    with st.form("batch_form"):
        b_col1, b_col2 = st.columns(2)
        with b_col1: veg_b = st.selectbox("Vegetable", list(st.session_state.veg_rates.keys()))
        with b_col2: weight_b = st.number_input("Weight (KG)", value=10.0)
        if st.form_submit_button("➕ Add to Batch"):
            new_row = pd.DataFrame({
                "Vegetable": [veg_b], "Weight_KG": [weight_b],
                "Rate": [st.session_state.veg_rates[veg_b]],
                "Amount": [calculate_charges(veg_b, weight_b)]
            })
            st.session_state.batch_data = pd.concat([st.session_state.batch_data, new_row])
            st.rerun()
    
    if not st.session_state.batch_data.empty:
        st.dataframe(st.session_state.batch_data, use_container_width=True)
        if st.button("🗑️ Clear Batch"):
            st.session_state.batch_data = pd.DataFrame()
            st.rerun()

# --- TAB 3: QUOTES & TRANSPORT ---
with tab3:
    st.subheader("Generate Customer Quote")
    
    TRANSPORT_MODES = {
        "Truck": 2.50,        # Example ₹2.5 per kg
        "Bus/Train": 1.50,    # Example ₹1.5 per kg
        "Self Pickup": 0.00
    }

    with st.form("quote_form"):
        q_col1, q_col2 = st.columns(2)
        customer = q_col1.text_input("Customer Name")
        t_source = q_col2.selectbox("Transportation Source", list(TRANSPORT_MODES.keys()))
        
        gst = st.number_input("GST %", value=18.0)
        selected_veggies = st.multiselect("Select Vegetables", list(st.session_state.veg_rates.keys()))
        
        quote_items = []
        for v in selected_veggies:
            w = st.number_input(f"Weight for {v} (KG)", min_value=0.0, step=1.0)
            if w > 0:
                quote_items.append({"Vegetable": v, "Weight_KG": w, 
                                   "Rate": st.session_state.veg_rates[v], 
                                   "Amount": st.session_state.veg_rates[v] * w})
        
        submit_quote = st.form_submit_button("📄 Generate Final Quote")

    if submit_quote and quote_items:
        df_q = pd.DataFrame(quote_items)
        total_w = df_q["Weight_KG"].sum()
        veg_total = df_q["Amount"].sum()
        
        # Transport Cost Calculation
        t_cost = total_w * TRANSPORT_MODES[t_source]
        tax = (veg_total + t_cost) * (gst/100)
        grand_total = veg_total + t_cost + tax

        st.markdown(f"### Quote for {customer}")
        st.table(df_q)
        
        st.markdown(f"""
        | Description | Amount |
        | :--- | :--- |
        | **Vegetables Total** | ₹{veg_total:,.2f} |
        | **Transport ({t_source})** | ₹{t_cost:,.2f} |
        | **GST ({gst}%)** | ₹{tax:,.2f} |
        | --- | --- |
        | **GRAND TOTAL** | **₹{grand_total:,.2f}** |
        """)
