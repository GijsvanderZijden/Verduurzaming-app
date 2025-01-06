import streamlit as st

# Functie om U-waarde te berekenen
def calculate_u_value(rc_value):
    return 1 / rc_value

# Functie om energieverlies te berekenen
def calculate_energy_loss(u_value, area, delta_t, hours_per_year=8760):
    return u_value * area * delta_t * hours_per_year

# Functie om kostenbesparing te berekenen
def calculate_savings(q1, q2, energy_cost_per_kwh):
    energy_saving = q1 - q2
    cost_saving = energy_saving * energy_cost_per_kwh
    return energy_saving, cost_saving

# Functie om totale kosten te berekenen inclusief subsidie
def calculate_total_cost(area, material_cost, installation_cost, subsidy_percentage):
    total_cost = (material_cost + installation_cost) * area
    subsidized_cost = total_cost * (1 - subsidy_percentage)
    return total_cost, subsidized_cost

# Functie om terugverdientijd te berekenen
def calculate_payback_period(total_cost, annual_savings):
    return total_cost / annual_savings if annual_savings != 0 else float('inf')

# Streamlit interface
st.title("Verduurzaming Berekening - BBDW")

# Algemene inputvelden
delta_t = st.number_input("Gemiddeld temperatuurverschil in °C:", min_value=1.0, value=15.0, step=1.0, format="%.0f")
energy_cost_per_kwh = st.number_input("Energiekosten per kWh:", min_value=0.01, value=0.60, step=0.01, format="%.2f")
heating_type = st.selectbox("Kies het type verwarming:", ["Gas", "Stadsverwarming", "Elektriciteit","Zonne energie"])

verwrmings_type = {
        "Gas": 0.184,
        "Elektriciteit": 0.4,
        "Stadsverwarming": 0.18,
        "Zonne energie": 0.02, 
    }

subsidy_percentage = st.slider("Subsidiepercentage (%):", min_value=0, max_value=100, value=20) / 100

# Categorieën voor berekeningen
categories = ["Vloeren", "Daken", "Wanden", "Ramen"]
results = {}

for category in categories:
    st.subheader(f"Invoer voor {category}")
    area = st.number_input(f"Oppervlakte {category.lower()} in m²:", min_value=1.0, value=50.0, step=1.0, format="%.0f")
    rc1 = st.number_input(f"Huidige RC-waarde {category.lower()}:", min_value=0.1, value=2.5, step=0.1, format="%.1f")
    rc2 = st.number_input(f"Nieuwe RC-waarde {category.lower()}:", min_value=0.1, value=4.0, step=0.1, format="%.1f")
    material_cost = st.number_input(f"Materiaalprijs per m² voor {category.lower()}:", min_value=1.0, value=20.0, step=1.0, format="%.2f")
    installation_cost = st.number_input(f"Installatiekosten per m² voor {category.lower()}:", min_value=1.0, value=10.0, step=1.0, format="%.2f")

    # Berekeningen
    u1 = calculate_u_value(rc1)
    u2 = calculate_u_value(rc2)
    q1 = calculate_energy_loss(u1, area, delta_t)
    q2 = calculate_energy_loss(u2, area, delta_t)
    energy_saving, cost_saving = calculate_savings(q1, q2, energy_cost_per_kwh)
    total_cost, subsidized_cost = calculate_total_cost(area, material_cost, installation_cost, subsidy_percentage)
    payback_period = calculate_payback_period(subsidized_cost, cost_saving)

    # Opslaan resultaten
    results[category] = {
        "Energieverlies oud (kWh/jaar)": q1 / 1000,
        "Energieverlies nieuw (kWh/jaar)": q2 / 1000,
        "Jaarlijkse energiebesparing (kWh)": energy_saving / 1000,
        "Kostenbesparing (€)": cost_saving,
        "Totale kosten (€)": total_cost,
        "Kosten na subsidie (€)": subsidized_cost,
        "Terugverdientijd (jaren)": payback_period,
    }

# Weergave resultaten
st.subheader("Resultaten")
for category, result in results.items():
    st.write(f"**{category}**")
    for key, value in result.items():
        st.write(f"{key}: {value:.2f}")
    st.write("---")
