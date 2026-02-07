import streamlit as st
import pandas as pd

st.set_page_config(page_title="Eeki Farms Vegetable Pricing", page_icon="🥬", layout="wide")

# Updated with your EXACT average cost/kg prices (₹/kg)
VEGETABLE_RATES = {
    "coriander": 9.58,
    "Yellow bellpepper": 7.65,
    "Red bellpepper": 7.53,
    "Spring onion": 7.32,
    "Chilli": 6.89,
    "Muskmelon": 6.60,
    "Green Bellpepper": 6.55,
    "Spinach": 5.71,
    "Parsley": 5.37,
    "Yellow candy": 4.73,
    "Bellpepper": 4.44,
    "Kale": 4.42,
    "cauliflower": 4.37,
    "lettuce": 4.23,
    "Basil": 4.20,
    "tomato": 4.13,
    "Zucchini": 3.93,
    "Rocket": 3.79,
    "Pak choy": 3.79,
    "Mint": 3.62,
    "cucumber": 3.62,
    "Cabbage": 3.27,
    "Broccoli": 2.04,
    "Radish": 0.95
}

def calculate_charges(veg, weight):
    rate = VEGETABLE_RATES.get(veg, 4.00)  # Default average
    return weight * rate

# Header
st.title("🥬 Eeki Farms Vegetable Pricing Calculator")
st.markdown("*Average Cost per KG from your data*")

# Calculator tabs
tab1, tab2, tab3 = st.tabs(["🧮 Quick Calc", "📦 Batch Calc", "📋 Quotes"])

with tab1:
    st.subheader("Single Vegetable Calculator")
    
    col1, col2 = st.columns(2)
    with col1:
        vegetable = st.selectbox("Vegetable", list(VEGETABLE_RATES.keys()))
    with col2:
        weight = st.number_input("Weight (KG)", min_value=0.1, value=50.0)
    
    if st.button("Calculate", type="primary"):
        rate = VEGETABLE_RATES[vegetable]
        charges = calculate_charges(vegetable, weight)
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Rate/kg", f"₹{rate:.2f}")
        with col_b:
            st.metric("Total", f"₹{charges:,.2f}")
        with col_c:
            st.metric("Per KG", f"₹{rate:.2f}")

with tab2:
    st.subheader("Batch Calculator")
    
    if "batch_data" not in st.session_state:
        st.session_state.batch_data = pd.DataFrame()
    
    with st.form("batch_form"):
        col1, col2 = st.columns(2)
        with col1: veg_batch = st.selectbox("Vegetable", list(VEGETABLE_RATES.keys()))
        with col2: weight_batch = st.number_input("Weight (KG)", value=50.0)
        if st.form_submit_button("➕ Add"):
            new_row = pd.DataFrame({
                "Vegetable": [veg_batch], "Weight_KG": [weight_batch],
                "Rate": [VEGETABLE_RATES[veg_batch]],
                "Amount": [calculate_charges(veg_batch, weight_batch)]
            })
            st.session_state.batch_data = pd.concat([st.session_state.batch_data, new_row])
            st.success("Added!")
            st.rerun()
    
    if not st.session_state.batch_data.empty:
        st.dataframe(st.session_state.batch_data.round(2), use_container_width=True)
        st.metric("GRAND TOTAL", f"₹{st.session_state.batch_data['Amount'].sum():,.2f}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear All"):
                st.session_state.batch_data = pd.DataFrame()
                st.rerun()
        with col2:
            csv = st.session_state.batch_data.round(2).to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", csv, "eeki_order.csv")

with tab3:
    st.subheader("Customer Quote")
    
    with st.form("quote_form"):
        customer = st.text_input("Customer Name")
        veg_list = st.multiselect("Select Vegetables", list(VEGETABLE_RATES.keys()), max_selections=8)
        total_weight = st.number_input("Total Weight (KG)", value=500.0)
        gst = st.number_input("GST %", value=18.0, step=1.0)
        
        q_submit = st.form_submit_button("📄 Generate Quote")
    
    if q_submit and customer and veg_list:
        avg_rate = sum(VEGETABLE_RATES[v] for v in veg_list) / len(veg_list)
        subtotal = total_weight * avg_rate
        gst_amount = subtotal * (gst / 100)
        grand_total = subtotal + gst_amount
        
        st.markdown(f"""
        # **Eeki Farms - Vegetable Quote**
        
        **To**: {customer.upper()}
        **Date**: {pd.Timestamp.now().strftime("%d Feb %Y")}
        
        **Order Summary**:
        - Vegetables: {', '.join(veg_list[:5])}{'...' if len(veg_list)>5 else ''}
        - Total Weight: **{total_weight:,.0f} KG**
        - Average Rate: **₹{avg_rate:.2f}/kg**
        
        **Pricing**:
        | Item | Amount |
        |------|--------|
        | Subtotal | ₹{subtotal:,.2f} |
        | GST @{gst}% | ₹{gst_amount:,.2f} |
        | **GRAND TOTAL** | **₹{grand_total:,.2f}** |
        """)
        
        # Download quote
        quote_data = {
            "Customer": customer,
            "Vegetables": ', '.join(veg_list),
            "Total_Weight_KG": total_weight,
            "Avg_Rate": avg_rate,
            "Subtotal": subtotal,
            "GST": gst_amount,
            "Grand_Total": grand_total
        }
        csv_quote = pd.DataFrame([quote_data]).to_csv(index=False).encode('utf-8')
        st.download_button("💾 Download Quote", csv_quote, f"eeki_quote_{customer.replace(' ','_')}.csv")

st.markdown("---")
st.caption("Eeki Farms | Updated with your exact average costs per KG")
