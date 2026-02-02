import streamlit as st
import pandas as pd

st.set_page_config(page_title="Eeki Farms Vegetables", page_icon="🥬", layout="wide")

# Vegetable master list (your exact list)
VEGETABLES = [
    "Cucumber", "Cucumber", "Bellpepper", "Tomato", "Chilli", "Coriander",
    "Musk Melon", "Radish", "Cauliflower", "Spinach", "Lettuce", "Rocket",
    "Pak Choy", "Zucchini", "Basil", "Kale", "Broccoli", "Cabbage",
    "Yellow Candy", "Red Cherry", "Red Candy", "Parsley", "Mint",
    "Bottle Gourd", "Swiss Chard", "Yellow Cherry", "Celery"
]

def calculate_charges(km, weight, rate=2.5):
    return km * weight * rate

# Header
st.title("🥬 Eeki Farms Vegetable Logistics Dashboard")
st.markdown("**Track Inventory → Calculate Charges → Generate Quotes**")

# Sidebar - Vegetable selection & rates
st.sidebar.header("🌱 Vegetables")
selected_veg = st.sidebar.multiselect("Select Vegetables", VEGETABLES, default=["Cucumber", "Tomato"])

st.sidebar.header("💰 Rates")
rate_per_km_per_kg = st.sidebar.number_input("Rate (₹/km/kg)", value=2.5, step=0.1)

# Tabs
tab1, tab2, tab3 = st.tabs(["📦 Inventory", "🚚 Charges", "📋 Quotes"])

with tab1:
    st.subheader("Current Inventory")
    
    # Session state for inventory
    if "inventory" not in st.session_state:
        st.session_state.inventory = pd.DataFrame(columns=["Vegetable", "Weight_KG", "KM", "Date"])
    
    # Add inventory
    with st.form("add_inventory"):
        veg = st.selectbox("Vegetable", VEGETABLES)
        weight = st.number_input("Weight (KG)", min_value=0.1)
        km = st.number_input("Distance (KM)", min_value=1.0)
        submitted = st.form_submit_button("➕ Add to Inventory")
        
        if submitted:
            new_row = pd.DataFrame({
                "Vegetable": [veg], "Weight_KG": [weight], "KM": [km],
                "Date": [pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")]
            })
            st.session_state.inventory = pd.concat([st.session_state.inventory, new_row])
            st.success("Added!")
    
    # Display filtered inventory
    if not st.session_state.inventory.empty:
        filtered = st.session_state.inventory[
            st.session_state.inventory["Vegetable"].isin(selected_veg)
        ]
        st.dataframe(filtered, use_container_width=True)
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Total Weight", f"{filtered['Weight_KG'].sum():.1f} KG")
        with col2: st.metric("Total KM", f"{filtered['KM'].sum():.0f} KM")
        with col3: st.metric("Items", len(filtered))

with tab2:
    st.subheader("Calculate Charges")
    
    col1, col2 = st.columns(2)
    with col1:
        km_input = st.number_input("Distance (KM)", min_value=1.0, value=100.0)
        weight_input = st.number_input("Weight (KG)", min_value=0.1, value=50.0)
    
    charges = calculate_charges(km_input, weight_input, rate_per_km_per_kg)
    
    with col2:
        st.metric("Total Charges", f"₹{charges:,.2f}")
        st.info(f"Rate: ₹{rate_per_km_per_kg}/km/kg")
    
    # Quick inventory charges
    if not st.session_state.inventory.empty:
        st.subheader("Inventory Charges")
        inv_charges = st.session_state.inventory.copy()
        inv_charges['Charges'] = inv_charges.apply(
            lambda row: calculate_charges(row['KM'], row['Weight_KG'], rate_per_km_per_kg), axis=1
        )
        st.dataframe(inv_charges[['Vegetable', 'Weight_KG', 'KM', 'Charges']])
        st.metric("Grand Total", f"₹{inv_charges['Charges'].sum():,.2f}")

with tab3:
    st.subheader("Generate Quotes")
    
    # Quote form
    with st.form("quote_form"):
        customer = st.text_input("Customer Name")
        veg_quote = st.multiselect("Vegetables", VEGETABLES)
        total_weight = st.number_input("Total Weight (KG)", min_value=0.1)
        total_km = st.number_input("Total KM", min_value=1.0)
        quote_rate = st.number_input("Quote Rate (₹/km/kg)", value=rate_per_km_per_kg)
        gst = st.number_input("GST %", value=18.0)
        
        q_submitted = st.form_submit_button("📄 Generate Quote")
    
    if q_submitted and customer:
        quote_charges = calculate_charges(total_km, total_weight, quote_rate)
        gst_amount = quote_charges * (gst / 100)
        final_amount = quote_charges + gst_amount
        
        st.success("**QUOTE GENERATED**")
        
        # Quote display
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            **Eeki Farms Logistics Quote**
            
            **Customer**: {customer}
            **Date**: {pd.Timestamp.now().strftime("%Y-%m-%d")}
            
            **Vegetables**: {', '.join(veg_quote[:3])}{'...' if len(veg_quote)>3 else ''}
            **Weight**: {total_weight} KG
            **Distance**: {total_km} KM
            """)
        
        with col2:
            st.markdown(f"""
            **Pricing**:
            - Base Charges: ₹{quote_charges:,.2f}
            - GST ({gst}%): ₹{gst_amount:,.2f}
            **Final Amount: ₹{final_amount:,.2f}** ⚡
            """)
        
        # Download quote
        quote_data = {
            "Customer": [customer],
            "Vegetables": [', '.join(veg_quote)],
            "Weight_KG": [total_weight],
            "KM": [total_km],
            "Rate": [quote_rate],
            "Base_Charges": [quote_charges],
            "GST": [gst_amount],
            "Final_Amount": [final_amount]
        }
        csv = pd.DataFrame(quote_data).to_csv(index=False).encode('utf-8')
        st.download_button("💾 Download Quote", csv, f"eeki_quote_{customer}_{pd.Timestamp.now().strftime('%Y%m%d')}.csv")

# Footer
st.markdown("---")
st.markdown("*Eeki Farms Vegetable Logistics | All 28 crops supported*")
