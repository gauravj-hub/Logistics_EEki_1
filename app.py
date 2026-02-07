import streamlit as st
import pandas as pd

st.set_page_config(page_title="Eeki Farms Vegetable Pricing", page_icon="🥬", layout="wide")

# Your exact average cost/kg prices (₹/kg)
VEGETABLE_RATES = {
    "coriander": 9.58,
    "Yellow bellpepper": 6.32,
    "Red bellpepper": 6.26,
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
    rate = VEGETABLE_RATES.get(veg, 4.00)
    return weight * rate

# Header
st.title("🥬 Eeki Farms Vegetable Pricing Calculator")
st.markdown("*Average Cost per KG from your data*")

# Tabs 1 & 2 unchanged
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

# NEW Tab 3: Per-crop weights
with tab3:
    st.subheader("📋 Detailed Customer Quote")
    
    customer = st.text_input("Customer Name", value="Jai Balaji Company")
    gst = st.number_input("GST %", value=18.0, step=1.0)
    
    # Dynamic crop-weight input
    st.markdown("**Enter quantities for each crop:**")
    
    quote_items = []
    for veg in VEGETABLE_RATES.keys():
        weight = st.number_input(f"{veg}", min_value=0.0, value=0.0, key=f"w_{veg}", step=10.0)
        if weight > 0:
            quote_items.append({
                "Vegetable": veg,
                "Weight_KG": weight,
                "Rate": VEGETABLE_RATES[veg],
                "Amount": calculate_charges(veg, weight)
            })
    
    if st.button("📄 Generate Quote", type="primary") and quote_items:
        quote_df = pd.DataFrame(quote_items)
        subtotal = quote_df['Amount'].sum()
        gst_amount = subtotal * (gst / 100)
        grand_total = subtotal + gst_amount
        
        st.success("**Quote Generated!**")
        
        # Detailed quote table
        st.markdown(f"""
        # **Eeki Farms - Detailed Vegetable Quote**
        
        **To**: {customer.upper()}
        **Date**: {pd.Timestamp.now().strftime("%d Feb %Y")}
        **GST**: {gst}%
        
        **Order Details:**
        """)
        
        st.dataframe(quote_df.round(2), use_container_width=True, hide_index=True)
        
        st.markdown(f"""
        **Summary**:
        | Item | Amount |
        |------|--------|
        | **Subtotal** | **₹{subtotal:,.2f}** |
        | GST @{gst}% | ₹{gst_amount:,.2f} |
        | **GRAND TOTAL** | **₹{grand_total:,.2f}** |
        """)
        
        # Download detailed quote
        quote_data = quote_df.copy()
        quote_data.loc['TOTAL'] = ['Subtotal', '', '', subtotal]
        quote_data.loc['GST'] = [f'GSTR @{gst}%', '', '', gst_amount]
        quote_data.loc['GRAND'] = ['GRAND TOTAL', '', '', grand_total]
        
        csv_quote = quote_data.round(2).to_csv(index=False).encode('utf-8')
        st.download_button("💾 Download Detailed Quote", csv_quote, f"detailed_quote_{customer.replace(' ','_')}.csv")

st.markdown("---")
st.caption("Eeki Farms | Per-crop weight quoting enabled")
