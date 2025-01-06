import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from fpdf import FPDF

# Functie voor de berekening van kosten, besparing, CO2-besparing en terugverdientijd
def calculate_costs_with_rc(area, current_rc, desired_rc, cost_per_m2, heating_cost_per_kwh, delta_t, hours_per_year):
    # Berekening van U-waarde
    current_u = 1 / current_rc if current_rc > 0 else float('inf')
    desired_u = 1 / desired_rc if desired_rc > 0 else float('inf')

    # Warmteverlies en energieverbruik
    current_energy_loss = current_u * area * delta_t * hours_per_year
    desired_energy_loss = desired_u * area * delta_t * hours_per_year

    # Energieverbruik in kWh
    current_energy_kwh = current_energy_loss / 3.6e6
    desired_energy_kwh = desired_energy_loss / 3.6e6

    # Kosten en besparingen
    energy_savings_kwh = current_energy_kwh - desired_energy_kwh
    heating_costs = current_energy_kwh * heating_cost_per_kwh
    cost = area * cost_per_m2 * (desired_rc - current_rc)
    co2_savings = energy_savings_kwh * 0.2
    payback_period = cost / (energy_savings_kwh * heating_cost_per_kwh) if energy_savings_kwh > 0 else float('inf')

    return cost, energy_savings_kwh, co2_savings, payback_period, heating_costs

# Functie voor PDF generatie met professionele opmaak
def generate_pdf(data, totals):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="BBDW - Resultaten Verduurzaming", ln=True, align='C')
    pdf.ln(10)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)

    # Hoofdtekst
    pdf.set_font("Arial", size=12)
    for category, (cost, savings, co2_savings, payback, heating_cost) in data.items():
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt=f"{category} - Resultaten", ln=True)

        pdf.set_font("Arial", size=12)
        text = (f"Kosten: €{cost:,.2f}\n"
                f"Besparing per jaar: {savings:,.2f} kWh\n"
                f"CO2-besparing: {co2_savings:,.2f} kg\n"
                f"Terugverdientijd: {payback:,.2f} jaar\n"
                f"Jaarlijkse verwarmingkosten: €{heating_cost:,.2f}")
        pdf.multi_cell(0, 10, txt=text)
        pdf.ln(5)

    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Totale Resultaten", ln=True)
    pdf.set_font("Arial", size=12)
    totals_text = (f"Totaal Kosten: €{totals['cost']:,.2f}\n"
                   f"Totaal Besparing per jaar: {totals['savings']:,.2f} kWh\n"
                   f"Totaal CO2-besparing: {totals['co2_savings']:,.2f} kg\n"
                   f"Totaal Terugverdientijd: {totals['payback']:,.2f} jaar\n"
                   f"Totaal Jaarlijkse verwarmingkosten: €{totals['heating_costs']:,.2f}")
    pdf.multi_cell(0, 10, txt=totals_text)
    pdf.ln(10)

    pdf.set_font("Arial", 'I', 8)
    pdf.cell(200, 10, txt="Contact: info@bbdw.nl | www.bbdw.nl", ln=True, align='C')

    pdf_output = "verduurzaming_resultaten_professioneel.pdf"
    pdf.output(pdf_output)
    return pdf_output

# Functie voor het genereren van de invoer voor elke categorie
def generate_category_input(category_name, default_area, default_current_rc, default_desired_rc, cost_per_m2):
    st.subheader(category_name)
    area = st.number_input(f"Oppervlakte {category_name.lower()} (m²):", min_value=1, max_value=1000, value=default_area)
    current_rc = st.number_input(f"Huidige RC-waarde {category_name.lower()}:", min_value=0.1, max_value=5.0, value=default_current_rc, step=0.1)
    desired_rc = st.number_input(f"Gewenste RC-waarde {category_name.lower()}:", min_value=0.1, max_value=5.0, value=default_desired_rc, step=0.1)
    return area, current_rc, desired_rc

# Streamlit layout
st.title("Verduurzamingscalculator voor BBDW")
subsidie_percentage = st.slider('Kies het percentage subsidie:', 0, 30, 20) / 100

delta_t = st.number_input("Temperatuurverschil (ΔT) tussen binnen en buiten (°C):", min_value=1, max_value=50, value=20)
hours_per_year = 8760
heating_cost_per_kwh = st.number_input("Kosten per kWh voor verwarming (in €):", min_value=0.01, value=0.10)

# Categorieën voor vloer, dak, wanden en ramen
floor_area, floor_current_rc, floor_desired_rc = generate_category_input('Vloer', 50, 0.4, 2.5, 16)
roof_area, roof_current_rc, roof_desired_rc = generate_category_input('Dak', 50, 0.5, 4.5, 50)
wall_area, wall_current_rc, wall_desired_rc = generate_category_input('Wanden', 50, 0.3, 2.5, 30)
window_area, window_current_rc, window_desired_rc = generate_category_input('Ramen', 50, 0.2, 2.0, 100)

# Berekeningen voor alle categorieën
floor_cost, floor_savings, floor_co2_savings, floor_payback, floor_heating_costs = calculate_costs_with_rc(
    floor_area, floor_current_rc, floor_desired_rc, 16, heating_cost_per_kwh, delta_t, hours_per_year)
roof_cost, roof_savings, roof_co2_savings, roof_payback, roof_heating_costs = calculate_costs_with_rc(
    roof_area, roof_current_rc, roof_desired_rc, 50, heating_cost_per_kwh, delta_t, hours_per_year)
wall_cost, wall_savings, wall_co2_savings, wall_payback, wall_heating_costs = calculate_costs_with_rc(
    wall_area, wall_current_rc, wall_desired_rc, 30, heating_cost_per_kwh, delta_t, hours_per_year)
window_cost, window_savings, window_co2_savings, window_payback, window_heating_costs = calculate_costs_with_rc(
    window_area, window_current_rc, window_desired_rc, 100, heating_cost_per_kwh, delta_t, hours_per_year)

# Toepassing van de subsidie
floor_cost -= floor_cost * subsidie_percentage
roof_cost -= roof_cost * subsidie_percentage
wall_cost -= wall_cost * subsidie_percentage
window_cost -= window_cost * subsidie_percentage

# Totale kosten, besparingen, CO2-besparing, terugverdientijd inclusief verwarming
total_cost = floor_cost + roof_cost + wall_cost + window_cost
total_savings = floor_savings + roof_savings + wall_savings + window_savings
total_co2_savings = floor_co2_savings + roof_co2_savings + wall_co2_savings + window_co2_savings
total_payback = (floor_cost + roof_cost + wall_cost + window_cost) / (floor_savings + roof_savings + wall_savings + window_savings) if total_savings > 0 else float('inf')
total_heating_costs = floor_heating_costs + roof_heating_costs + wall_heating_costs + window_heating_costs

# Data voor grafieken
categories = ['Vloer', 'Dak', 'Wanden', 'Ramen']
costs = [floor_cost, roof_cost, wall_cost, window_cost]
savings = [floor_savings, roof_savings, wall_savings, window_savings]
co2_savings = [floor_co2_savings, roof_co2_savings, wall_co2_savings, window_co2_savings]

# Grafiek voor kosten en besparingen
fig = plt.figure(figsize=(10, 6))
categories_list = ["Vloer", "Dak", "Wanden", "Ramen"]
costs = [floor_cost, roof_cost, wall_cost, window_cost]
savings = [floor_savings, roof_savings, wall_savings, window_savings]

print(savings)
print('savings')

# Creëren van de grafiek met kosten en besparing
bar_width = 0.35
index = range(len(categories_list))

# Kosten en besparing naast elkaar
plt.bar(index, costs, bar_width, label="Kosten (€)", color='skyblue')
plt.bar([i + bar_width for i in index], savings, bar_width, label="Besparing (kWh)", color='lightgreen')

plt.xlabel('Categorieën')
plt.ylabel('Waarde')
plt.title('Kosten en Besparing per Categorie')
plt.xticks([i + bar_width / 2 for i in index], categories_list)
plt.legend()

# Weergeven van de grafiek
st.pyplot(fig)

# Staafdiagram voor CO2-besparing
fig2, ax2 = plt.subplots(figsize=(10, 6))
ax2.bar(categories_list, co2_savings, color='lightcoral')
ax2.set_title('CO2-besparing per Categorie')
ax2.set_xlabel('Categorieën')
ax2.set_ylabel('CO2-besparing (kg)')
st.pyplot(fig2)

# Resultaten tonen
st.subheader("Resultaten per categorie")
data = {
    "Vloer": (floor_cost, floor_savings, floor_co2_savings, floor_payback, floor_heating_costs),
    "Dak": (roof_cost, roof_savings, roof_co2_savings, roof_payback, roof_heating_costs),
    "Wanden": (wall_cost, wall_savings, wall_co2_savings, wall_payback, wall_heating_costs),
    "Ramen": (window_cost, window_savings, window_co2_savings, window_payback, window_heating_costs)
}

df = pd.DataFrame.from_dict(data, orient='index', columns=["Kosten (€)", "Besparing (kWh)", "CO2-besparing (kg)", "Terugverdientijd (jaar)", "Jaarlijkse verwarmingkosten (€)"])

st.dataframe(df)

# Totale resultaten in een tabel
st.subheader("Totale resultaten")
totals = {
    "cost": total_cost,
    "savings": total_savings,
    "co2_savings": total_co2_savings,
    "payback": total_payback,
    "heating_costs": total_heating_costs
}

df_totals = pd.DataFrame(list(totals.items()), columns=["Categorie", "Waarde"])
st.dataframe(df_totals)

# PDF knop
if st.button('Genereer PDF'):
    data = {
        'Vloer': (floor_cost, floor_savings, floor_co2_savings, floor_payback, floor_heating_costs),
        'Dak': (roof_cost, roof_savings, roof_co2_savings, roof_payback, roof_heating_costs),
        'Wanden': (wall_cost, wall_savings, wall_co2_savings, wall_payback, wall_heating_costs),
        'Ramen': (window_cost, window_savings, window_co2_savings, window_payback, window_heating_costs)
    }
    totals = {
        'cost': total_cost,
        'savings': total_savings,
        'co2_savings': total_co2_savings,
        'payback': total_payback,
        'heating_costs': total_heating_costs
    }
    pdf_file = generate_pdf(data, totals)
    st.download_button("Download PDF", pdf_file)

    # AI Advies
if st.button('Vraag AI Advies'):
    advies = "Overweeg een combinatie van isolatiemaatregelen om zowel kosten als energiebesparingen te optimaliseren. Bijvoorbeeld, het combineren van dakisolatie met vloerisolatie kan de energie-efficiëntie aanzienlijk verbeteren, wat leidt tot lagere verwarmingskosten en een kortere terugverdientijd."
    st.write(advies)

