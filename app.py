import streamlit as st
import pandas as pd

st.set_page_config(page_title="Eeki Farms Vegetable Rates", page_icon="🥬", layout="wide")

# Vegetable rates (₹ per km per kg) - your values + defaults
VEGETABLE_RATES = {
    "Pak Choy": 0.001320,
    "Cucumber": 0.0000201
    "Bellpepper":0.0000576,
    "Tomato": 0.0000533,
    "Chilli": 0.0006957,
    "Coriander": 0.0002910,
    "Musk Melon": 0.0004050,
    "Radish": 0.0021217,
    "Cauliflower": 0.0004917,
    "Spinach": 0.0008897,
    "Lettuce": 0.0016,
    "Rocket": 0.0017,
    "Zucchini": 0.0021,
    "Basil": 0.0014,
    "Kale": 0.0019,
    "Broccoli": 0.0028,
    "Cabbage": 0.0013,
    "Yellow Candy": 0.0023,
    "Red Cherry": 0.0024,
    "Red Candy": 0.0023,
    "Parsley": 0.0015,
    "Mint": 0.0012,
    "Bottle Gourd": 0.0027,
    "Swiss Chard": 0.0018,
    "Yellow Cherry": 0.0024,
    "Celery": 0.0019
}

def calculate_charges(veg, km, weight):
    rate = VEGETABLE_RATES.get(veg, 0.0025)  # Default rate
    return km * weight * rate

# Header
st.title("🥬 Eeki Farms Vegetable Logistics Calculator")
st.markdown("*Individual rates per vegetable (₹/km/kg)*")

# Rates table
st.markdown("---")
col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("📊 Current Rates")
    rates_df = pd.DataFrame(list(VEGETABLE_RATES.items()), 
                           columns=["Vegetable", "Rate (₹/km/kg)"])
    st.dataframe(rates_df.sort_values("Rate (₹/km/kg)", ascending=False), 
                use_container_width=True, height=400)

with col2:
    st.subheader("✏️ Update Rates")
    with st.form("rate_form"):
        veg_update = st.selectbox("Select Vegetable", list(VEGETABLE_RATES.keys()))
        new_rate = st.number_input("New Rate (₹/km/kg)", 
                                  value=VEGETABLE_RATES[veg_update], step=0.0001)
        if st.form_submit_button("💾 Update Rate"):
            VEGETABLE_RATES[veg_update] = new_rate
            st.success(f"✅ {veg_update} updated to ₹{new_rate:.6f}")
            st.rerun()

# Calculator tabs
tab1, tab2, tab3 = st.tabs(["🧮 Quick Calc", "📦 Batch Calc", "📋 Quotes"])

with tab1:
    st.subheader("Single Shipment Calculator")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        vegetable = st.selectbox("Vegetable", list(VEGETABLE_RATES.keys()))
    with col2:
        km = st.number_input("KM", min_value=1.0, value=100.0)
    with col3:
        weight = st.number_input("Weight (KG)", min_value=0.1, value=50.0)
    
    if st.button("Calculate", type="primary"):
        rate = VEGETABLE_RATES[vegetable]
        charges = calculate_charges(vegetable, km, weight)
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Rate", f"₹{rate:.6f}")
        with col_b:
            st.metric("Charges", f"₹{charges:,.2f}")
        with col_c:
            st.metric("Per KG", f"₹{charges/weight:.2f}")

with tab2:
    st.subheader("Batch Inventory Calculator")
    
    # Session state for batch
    if "batch_data" not in st.session_state:
        st.session_state.batch_data = pd.DataFrame()
    
    with st.form("batch_form"):
        col1, col2, col3 = st.columns(3)
        with col1: veg_batch = st.selectbox("Add Vegetable", list(VEGETABLE_RATES.keys()))
        with col2: km_batch = st.number_input("KM", value=100.0)
        with col3: weight_batch = st.number_input("KG", value=50.0)
        if st.form_submit_button("➕ Add Batch"):
            new_row = pd.DataFrame({
                "Vegetable": [veg_batch], "KM": [km_batch], "Weight_KG": [weight_batch],
                "Rate": [VEGETABLE_RATES[veg_batch]],
                "Charges": [calculate_charges(veg_batch, km_batch, weight_batch)]
            })
            st.session_state.batch_data = pd.concat([st.session_state.batch_data, new_row])
            st.success("Added!")
    
    if not st.session_state.batch_data.empty:
        st.dataframe(st.session_state.batch_data, use_container_width=True)
        st.metric("TOTAL CHARGES", f"₹{st.session_state.batch_data['Charges'].sum():,.2f}")
        
        # Download
        csv = st.session_state.batch_data.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Batch", csv, "batch_charges.csv")

with tab3:
    st.subheader("Professional Quote")
    
    with st.form("quote_form"):
        customer = st.text_input("Customer")
        veg_list = st.multiselect("Vegetables", list(VEGETABLE_RATES.keys()), max_selections=5)
        total_km = st.number_input("Total KM", value=100.0)
        total_weight = st.number_input("Total Weight KG", value=200.0)
        gst_pct = st.number_input("GST %", value=18.0)
        
        if st.form_submit_button("📄 Generate Quote"):
            # Average rate for multiple veggies
            avg_rate = sum(VEGETABLE_RATES[v] for v in veg_list) / len(veg_list)
            base_charges = total_km * total_weight * avg_rate
            gst_amount = base_charges * (gst_pct / 100)
            final_total = base_charges + gst_amount
            
            st.markdown(f"""
            # **Eeki Farms Logistics Quote**
            
            **Customer**: {customer}  
            **Date**: {pd.Timestamp.now().strftime("%d/%m/%Y")}
            
            **Vegetables**: {', '.join(veg_list)}
            **Distance**: {total_km} KM
            **Weight**: {total_weight} KG
            **Avg Rate**: ₹{avg_rate:.6f}/km/kg
            
            ---
            **Base Charges**: ₹{base_charges:,.2f}
            **GST ({gst_pct}% )**: ₹{gst_amount:,.2f}
            **TOTAL**: **₹{final_total:,.2f}** 💰
            """)
            
            # Quote CSV
            quote_df = pd.DataFrame({
                "Customer": [customer], "Vegetables": [', '.join(veg_list)],
                "KM": [total_km], "Weight_KG": [total_weight],
                "Avg_Rate": [avg_rate], "Base": [base_charges],
                "GST": [gst_amount], "Total": [final_total]
            })
            csv_quote = quote_df.to_csv(index=False).encode('utf-8')
            st.download_button("💾 Download Quote PDF/CSV", csv_quote, f"quote_{customer}.csv")

st.markdown("---")
st.caption("Eeki Farms | Vegetable-specific rates | Updated 2026")
