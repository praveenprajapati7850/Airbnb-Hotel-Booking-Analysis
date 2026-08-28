
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Airbnb Hotel Booking Analysis",
    page_icon="🏠",
    layout="wide",
)

PALETTE = ["#B85042", "#E7A11A", "#A7BEAE", "#6D2E46", "#50808E"]

st.title("🏠 Airbnb Hotel Booking Analysis")
st.caption("Interactive dashboard based on the original Airbnb Hotel Booking Analysis notebook")

@st.cache_data
# Sidebar
st.sidebar.header("📁 Data")

# Automatically load the dataset from GitHub
DATA_FILE = "Airbnb_Open_Data.xlsx"

raw = pd.read_excel(DATA_FILE)

st.sidebar.success("Dataset loaded automatically ✅")

st.sidebar.markdown("---")
st.sidebar.info(
    "The dashboard follows the cleaning steps and analysis questions "
    "from the original notebook."
)

df = clean_data(raw)
def clean_data(df):
    df = df.copy()

    df = df.drop_duplicates()

    for c in ["house_rules", "license"]:
        if c in df.columns:
            df = df.drop(columns=c)

    for c in ["price", "service fee"]:
        if c in df.columns:
            df[c] = pd.to_numeric(
                df[c].astype(str)
                .str.replace("$", "", regex=False)
                .str.replace(",", "", regex=False)
                .str.strip(),
                errors="coerce",
            )

    df = df.rename(
        columns={
            "price": "price ($)",
            "service fee": "service fee ($)",
        }
    )

    if "neighbourhood group" in df.columns:
        df["neighbourhood group"] = df["neighbourhood group"].replace(
            {
                "brookln": "Brooklyn",
                "brooklyn": "Brooklyn",
                "manhatan": "Manhattan",
            }
        )

    df = df.dropna()

    int_cols = [
        "Construction year",
        "minimum nights",
        "number of reviews",
        "review rate number",
        "calculated host listings count",
        "availability 365",
    ]
    existing = [c for c in int_cols if c in df.columns]
    for c in existing:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=existing)
    for c in existing:
        df[c] = df[c].astype(int)

    if "availability 365" in df.columns:
        df = df[(df["availability 365"] >= 0) & (df["availability 365"] <= 365)]

    return df

# Sidebar
st.sidebar.header("📁 Data")
uploaded = st.sidebar.file_uploader(
    "Upload Airbnb_Open_Data.xlsx or Airbnb_Open_Data.csv",
    type=["xlsx", "xls", "csv"],
)

st.sidebar.markdown("---")
st.sidebar.info(
    "The dashboard follows the cleaning steps and analysis questions in the "
    "original notebook."
)

if uploaded is None:
    st.info("👆 Upload the Airbnb dataset from the sidebar to start the interactive dashboard.")
    st.markdown("### Project overview")
    st.write(
        "This dashboard converts the original Jupyter Notebook into an interactive "
        "web application. It covers room types, neighbourhood groups, pricing, "
        "construction year, hosts, verification, service fees, ratings, availability "
        "and correlations."
    )
    st.stop()

raw = load_data(uploaded)
df = clean_data(raw)

# Filters
st.sidebar.header("🔎 Filters")

if "neighbourhood group" in df.columns:
    neighborhoods = sorted(df["neighbourhood group"].dropna().unique())
    selected_neighborhoods = st.sidebar.multiselect(
        "Neighbourhood group",
        neighborhoods,
        default=neighborhoods,
    )
    filtered = df[df["neighbourhood group"].isin(selected_neighborhoods)].copy()
else:
    filtered = df.copy()

if "room type" in filtered.columns:
    rooms = sorted(filtered["room type"].dropna().unique())
    selected_rooms = st.sidebar.multiselect(
        "Room type",
        rooms,
        default=rooms,
    )
    filtered = filtered[filtered["room type"].isin(selected_rooms)].copy()

# KPI row
c1, c2, c3, c4 = st.columns(4)
c1.metric("Listings", f"{len(filtered):,}")
if "price ($)" in filtered.columns:
    c2.metric("Average price", f"${filtered['price ($)'].mean():,.2f}")
if "review rate number" in filtered.columns:
    c3.metric("Average rating", f"{filtered['review rate number'].mean():.2f} ⭐")
if "availability 365" in filtered.columns:
    c4.metric("Avg. availability", f"{filtered['availability 365'].mean():.0f} days")

tabs = st.tabs([
    "📊 Overview",
    "🏘️ Neighbourhoods & Prices",
    "👤 Hosts",
    "⭐ Reviews",
    "📈 Relationships",
    "📋 Data",
    "💡 Conclusions",
])

with tabs[0]:
    st.subheader("Listings by Room Type")
    if "room type" in filtered.columns:
        room_counts = filtered["room type"].value_counts()
        st.bar_chart(room_counts)

    st.subheader("Listings by Neighbourhood Group")
    if "neighbourhood group" in filtered.columns:
        ng = filtered["neighbourhood group"].value_counts()
        st.bar_chart(ng)

with tabs[1]:
    st.subheader("Average Price by Neighbourhood Group")
    if {"neighbourhood group", "price ($)"}.issubset(filtered.columns):
        avg_price = (
            filtered.groupby("neighbourhood group")["price ($)"]
            .mean()
            .sort_values(ascending=False)
        )
        st.bar_chart(avg_price)

        st.write("Average prices:")
        st.dataframe(avg_price.round(2).rename("Average price ($)"))

    st.subheader("Average Price by Construction Year")
    if {"Construction year", "price ($)"}.issubset(filtered.columns):
        yearly = filtered.groupby("Construction year")["price ($)"].mean()
        st.line_chart(yearly)

with tabs[2]:
    st.subheader("Top 10 Hosts by Calculated Host Listing Count")
    required = {"host name", "calculated host listings count"}
    if required.issubset(filtered.columns):
        top_hosts = (
            filtered.groupby("host name")["calculated host listings count"]
            .max()
            .sort_values(ascending=False)
            .head(10)
        )
        st.bar_chart(top_hosts)
        st.dataframe(top_hosts.rename("Listings"))

    st.subheader("Availability by Host Size")
    required = {"calculated host listings count", "availability 365"}
    if required.issubset(filtered.columns):
        bins = [0, 1, 5, 20, 100, 1000]
        labels = ["1", "2-5", "6-20", "21-100", "100+"]
        temp = filtered.copy()
        temp["host_size"] = pd.cut(
            temp["calculated host listings count"],
            bins=bins,
            labels=labels,
            include_lowest=True,
        )
        avail = temp.groupby("host_size", observed=True)["availability 365"].mean()
        st.bar_chart(avail)
        corr = temp["calculated host listings count"].corr(temp["availability 365"])
        st.metric("Host listings vs availability correlation", f"{corr:.4f}")

with tabs[3]:
    st.subheader("Host Verification and Reviews")
    required = {"host_identity_verified", "review rate number"}
    if required.issubset(filtered.columns):
        verified = filtered.groupby("host_identity_verified").agg(
            avg_review_rate=("review rate number", "mean"),
            listings=("review rate number", "count"),
        )
        st.bar_chart(verified["avg_review_rate"])
        st.dataframe(verified.round(3))

    st.subheader("Average Review Rate by Neighbourhood & Room Type")
    required = {"neighbourhood group", "room type", "review rate number"}
    if required.issubset(filtered.columns):
        pivot = filtered.pivot_table(
            index="neighbourhood group",
            columns="room type",
            values="review rate number",
            aggfunc="mean",
        )
        st.dataframe(pivot.round(2))

with tabs[4]:
    st.subheader("Price vs Service Fee")
    if {"price ($)", "service fee ($)"}.issubset(filtered.columns):
        corr_fee = filtered["price ($)"].corr(filtered["service fee ($)"])
        st.metric("Correlation", f"{corr_fee:.4f}")
        st.scatter_chart(
            filtered[["price ($)", "service fee ($)"]].sample(
                min(4000, len(filtered)), random_state=1
            ).set_index("price ($)")
        )

    st.subheader("Construction Year vs Price")
    if {"Construction year", "price ($)"}.issubset(filtered.columns):
        corr_year = filtered["Construction year"].corr(filtered["price ($)"])
        st.metric("Correlation", f"{corr_year:.4f}")

    st.subheader("Correlation Matrix")
    numeric_candidates = [
        "price ($)",
        "service fee ($)",
        "minimum nights",
        "number of reviews",
        "review rate number",
        "calculated host listings count",
        "availability 365",
        "Construction year",
    ]
    numeric_cols = [c for c in numeric_candidates if c in filtered.columns]
    if len(numeric_cols) >= 2:
        st.dataframe(filtered[numeric_cols].corr().round(2), use_container_width=True)

with tabs[5]:
    st.subheader("Cleaned Dataset")
    st.write(f"Rows: {len(filtered):,} | Columns: {len(filtered.columns):,}")
    st.dataframe(filtered.head(1000), use_container_width=True)

    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download filtered data as CSV",
        csv,
        "airbnb_filtered_data.csv",
        "text/csv",
    )

with tabs[6]:
    st.subheader("Key Findings from the Original Analysis")
    findings = [
        "Four property types exist; Entire home/apt and Private room dominate supply.",
        "Brooklyn has the most listings, with Manhattan a close second.",
        "Average price is essentially uniform across neighbourhood groups in this dataset.",
        "Construction year has no meaningful relationship with price (the notebook reports r ≈ -0.005).",
        "Professional operators such as Blueground and Sonder NYC dominate listing counts.",
        "Identity verification shows only a negligible difference in average ratings.",
        "The notebook reports service fee as a fixed 20% of price (r = 1.00).",
        "Average rating is around 3.29 stars.",
        "Multi-listing hosts have substantially higher annual availability.",
    ]
    for i, finding in enumerate(findings, 1):
        st.markdown(f"**{i}.** {finding}")

    st.subheader("Recommendations")
    recommendations = [
        "Price using room type, amenities and demand seasonality rather than borough or building age.",
        "Drop service fee from predictive models if it is deterministically derived from price.",
        "Coach single-listing hosts on calendar management.",
        "Position verification as a trust/safety signal rather than a ratings lever.",
        "Investigate under-supplied boroughs such as Bronx and Staten Island.",
    ]
    for rec in recommendations:
        st.markdown(f"- {rec}")

    st.subheader("Limitations")
    st.write(
        "The original notebook notes that the dataset lacks booking dates and amenity "
        "fields, so peak-season demand, lead times and amenity preferences cannot be "
        "measured directly."
    )

st.markdown("---")
st.caption("Airbnb Hotel Booking Analysis • Python + Pandas + Streamlit")
