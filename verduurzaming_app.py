import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from fpdf import FPDF
import numpy as np


def calculate_energy_label(kwh_per_m2_per_year):
    if kwh_per_m2_per_year > 355.01:
        return "G"
    elif 355.01 >= kwh_per_m2_per_year > 325.01:
        return "F"
    elif 325.01 >= kwh_per_m2_per_year > 295.01:
        return "E"
    elif 295.01 >= kwh_per_m2_per_year > 260.01:
        return "D"
    elif 260.01 >= kwh_per_m2_per_year > 230.01:
        return "C"
    elif 230.01 >= kwh_per_m2_per_year > 210.01:
        return "B"
    elif 210.01 >= kwh_per_m2_per_year > 180.01:
        return "A"
    elif 180.01 >= kwh_per_m2_per_year > 135.01:
        return "A+"
    elif 135.01 >= kwh_per_m2_per_year > 90.01:
        return "A++"
    elif 90.01 >= kwh_per_m2_per_year > 45.01:
        return "A+++"
    elif 45.01 >= kwh_per_m2_per_year > 0.01:
        return "A++++"
    else:
        return "A+++++"

def calculate_u_value(rc_value):
    return 1 / rc_value

# Functie om energieverlies te berekenen
def calculate_energy_loss(u_value, area, delta_t, hours_per_year=4800):
    return (u_value * area * delta_t * hours_per_year) / 1000

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

def calculate_CO2(kWh,emissie):
    return kWh * emissie 

# Functie voor de berekening van kosten, besparing, CO2-besparing en terugverdientijd
def calculate_costs_with_rc(area, current_rc, desired_rc, cost_per_m2, emissie_per_kwh, delta_t, hours_per_year, subsidy_percentage, energy_kost, material_kost, installation_kost):
    # Berekening van U-waarde
    current_u = calculate_u_value(current_rc)
    desired_u = calculate_u_value(desired_rc)

    # Warmteverlies en energieverbruik
    current_energy_loss = calculate_energy_loss(current_u, area, delta_t)
    desired_energy_loss = calculate_energy_loss(desired_u, area, delta_t)

    # kWh kosten besparing
    current_kWh = current_energy_loss
    desired_kWh = desired_energy_loss
    saved_kWh = current_kWh - desired_kWh
    savings_euro = saved_kWh * energy_kost 

    # verduurzaming
    total_kost_without = (material_kost * area) + (installation_kost * area)
    Add_subsidie = (total_kost_without / 100) * subsidy_percentage
    total_kost_with = total_kost_without - Add_subsidie

    # CO2 to kg
    co2_savings = saved_kWh * emissie_per_kwh

    # Terugverdientijd
    payback_time = total_kost_with / savings_euro if savings_euro != 0 else float('inf')

    return total_kost_with, saved_kWh, co2_savings, payback_time, savings_euro, desired_kWh


# Functie voor PDF generatie met professionele opmaak
def generate_pdf(data, totals):
    pdf = FPDF()
    pdf.add_page()
    
    # Voeg het standaard DejaVu-lettertype toe
    pdf.add_font('DejaVu', '', 'dejavu-sans-bold.ttf', uni=True)
    pdf.set_font("DejaVu", size=12)
    
    # Add local logo
    logo_path = "logo-Bb-DW.jpg"  # Update this path to your local image file
    pdf.image(logo_path, x=80, y=10, w=50)  # Centered on the page
    pdf.ln(30)  # Add some space below the logo

    pdf.set_font("DejaVu", size=16)
    pdf.cell(200, 10, txt="BBDW - Resultaten Verduurzaming", ln=True, align='C')
    pdf.ln(10)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)

    # Hoofdtekst
    pdf.set_font("DejaVu", size=12)
    for category, (cost, savings, co2_savings, payback, total_savings_euro) in data.items():
        pdf.cell(200, 10, txt=f"{category} - Resultaten", ln=True)
        text = (f"Kosten: €{cost:,.2f}\n"
                f"Besparing per jaar: {savings:,.2f} kWh\n"
                f"CO2-besparing: {co2_savings:,.2f} kg\n"
                f"Terugverdientijd: {payback:,.2f} jaar\n"
                f"Bespaarde energiekosten: €{total_savings_euro:,.2f}")
        pdf.multi_cell(0, 10, txt=text)
        pdf.ln(5)

    pdf.ln(10)
    pdf.cell(200, 10, txt="Totale Resultaten", ln=True)
    totals_text = (f"Totaal Kosten: €{totals['cost']:,.2f}\n"
                   f"Totaal Besparing per jaar: {totals['savings']:,.2f} kWh\n"
                   f"Totaal CO2-besparing: {totals['co2_savings']:,.2f} kg\n"
                   f"Totaal Terugverdientijd: {totals['payback']:,.2f} jaar\n"
                   f"Totaal Bespaarde energiekosten: €{totals['total_savings_euro']:,.2f}\n")
    pdf.multi_cell(0, 10, txt=totals_text)
    
    # Add energy label with background color
    label_color = get_label_color(totals["energy_label"])
    r, g, b = tuple(int(label_color[i:i+2], 16) for i in (1, 3, 5))  # Convert hex to RGB
    pdf.set_fill_color(r, g, b)
    pdf.cell(200, 10, txt=f"Energielabel: {totals['energy_label']}", ln=True, fill=True)
    pdf.ln(10)

    pdf.set_font("DejaVu", size=8)
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
    material_kost = st.number_input(f"Materiaal kosten {category_name.lower()} (m²):", min_value=1.0, max_value=2000.0, value=20.0, step=1.0)
    installatie_kost = st.number_input(f"Installatie kosten {category_name.lower()} (m²):", min_value=1.0, max_value=2000.0, value=10.0, step=1.0)
    return area, current_rc, desired_rc, material_kost, installatie_kost

# Streamlit layout
st.title("Verduurzamingscalculator voor BBDW")
subsidie_percentage = st.slider('Kies het percentage subsidie:', 0, 30, 20)

delta_t = st.number_input("Temperatuurverschil (ΔT) tussen binnen en buiten (°C):", min_value=1, max_value=50, value=15)
hours_per_year = 4800
heating_type = st.selectbox("Kies het type verwarming:", ["Gas", "Elektriciteit gemiddeld", "Stadsverwarming","Zonne energie"])
Energy_kost = st.number_input("Energie kosten (euro/kWh)", min_value=0.0, max_value=50.0, value=0.6)

emissie = {
        "Gas": 0.184,
        "Elktriciteit gemiddeld": 0.4,
        "Stadsverwarming": 0.18,
        "Zonne energie": 0.02, 
    }

emissie_per_kwh = emissie.get(heating_type, 0.10)

# Categorieën voor vloer, dak, wanden en ramen
floor_area, floor_current_rc, floor_desired_rc, floor_materiaal_kost, floor_installatie_kost = generate_category_input('Vloer', 50, 2.5, 4.0, 20)
roof_area, roof_current_rc, roof_desired_rc, roof_materiaal_kost, roof_installatie_kost = generate_category_input('Dak', 50, 2.5, 4.0, 50)
wall_area, wall_current_rc, wall_desired_rc, wall_materiaal_kost, wall_installatie_kost = generate_category_input('Wanden', 50, 2.5, 4.0, 30)
window_area, window_current_rc, window_desired_rc, window_materiaal_kost, window_installatie_kost = generate_category_input('Ramen', 50, 2.5, 4.0, 100)

# Berekeningen voor alle categorieën
floor_total_kost_with, floor_saved_kWh, floor_co2_savings, floor_payback_time, floor_savings_euro, floor_desired_kWh = calculate_costs_with_rc(
    floor_area, floor_current_rc, floor_desired_rc, 16, emissie_per_kwh, delta_t, hours_per_year,subsidie_percentage,Energy_kost,floor_materiaal_kost,floor_installatie_kost)
roof_total_kost_with, roof_saved_kWh, roof_co2_savings, roof_payback_time, roof_savings_euro, roof_desired_kWh = calculate_costs_with_rc(
    roof_area, roof_current_rc, roof_desired_rc, 50, emissie_per_kwh, delta_t, hours_per_year,subsidie_percentage,Energy_kost,roof_materiaal_kost,roof_installatie_kost)
wall_total_kost_with, wall_saved_kWh, wall_co2_savings, wall_payback_time, wall_savings_euro, wall_desired_kWh = calculate_costs_with_rc(
    wall_area, wall_current_rc, wall_desired_rc, 30, emissie_per_kwh, delta_t, hours_per_year,subsidie_percentage,Energy_kost,wall_materiaal_kost,wall_installatie_kost)
window_total_kost_with, window_saved_kWh, window_co2_savings, window_payback_time, window_savings_euro, window_desired_kWh = calculate_costs_with_rc(
    window_area, window_current_rc, window_desired_rc, 100, emissie_per_kwh, delta_t, hours_per_year,subsidie_percentage,Energy_kost,window_materiaal_kost,window_installatie_kost)

# Toepassing van de subsidie
floor_cost = floor_total_kost_with
roof_cost = roof_total_kost_with
wall_cost = wall_total_kost_with
window_cost = window_total_kost_with
paybacks = np.array([floor_payback_time,roof_payback_time,wall_payback_time,window_payback_time])
total_kwh_per_m2_per_year = (floor_desired_kWh + roof_desired_kWh + wall_desired_kWh + window_desired_kWh) / (floor_area + roof_area + wall_area + window_area)
energy_label = calculate_energy_label(total_kwh_per_m2_per_year)

# Totale kosten, besparingen, CO2-besparing, terugverdientijd inclusief verwarming
total_cost = floor_cost + roof_cost + wall_cost + window_cost
total_savings = floor_saved_kWh + roof_saved_kWh + wall_saved_kWh + window_saved_kWh
total_co2_savings = floor_co2_savings + roof_co2_savings + wall_co2_savings + window_co2_savings
total_payback = paybacks[paybacks.argmax()]
total_savings_euro = floor_savings_euro + roof_savings_euro + wall_savings_euro + window_savings_euro

# Data voor grafieken
categories = ['Vloer', 'Dak', 'Wanden', 'Ramen']
costs = [floor_cost, roof_cost, wall_cost, window_cost]
savings = [floor_saved_kWh, roof_saved_kWh, wall_saved_kWh, window_saved_kWh]
co2_savings = [floor_co2_savings, roof_co2_savings, wall_co2_savings, window_co2_savings]

# Grafiek voor kosten en besparingen met dubbele y-as
fig, ax1 = plt.subplots(figsize=(10, 6))

# Primaire y-as voor kosten
ax1.bar(categories, costs, width=0.35, label="Kosten (€)", color='skyblue', align='center')
ax1.set_ylabel('Kosten (€)', color='blue')
ax1.set_xlabel('Categorieën')
ax1.tick_params(axis='y', labelcolor='blue')

# Secundaire y-as voor besparingen
ax2 = ax1.twinx()  # Maak een tweede y-as die dezelfde x-as deelt
ax2.bar([i + 0.35 for i in range(len(categories))], savings, width=0.35, label="Besparing (kWh)", color='lightgreen', align='center')
ax2.set_ylabel('Besparing (kWh)', color='green')
ax2.tick_params(axis='y', labelcolor='green')

# Titel en legenda
plt.title('Kosten en Besparing per Categorie')
fig.legend(loc="upper left", bbox_to_anchor=(0.1, 0.9))

# Weergeven van de grafiek
st.pyplot(fig)

# Staafdiagram voor CO2-besparing
fig2, ax2 = plt.subplots(figsize=(10, 6))
ax2.bar(categories, co2_savings, color='lightcoral')
ax2.set_title('CO2-besparing per Categorie')
ax2.set_xlabel('Categorieën')
ax2.set_ylabel('CO2-besparing (kg)')
st.pyplot(fig2)

# Resultaten tonen
st.subheader("Resultaten per categorie")
data = {
    "Vloer": (floor_cost, floor_saved_kWh, floor_co2_savings, floor_payback_time, floor_savings_euro),
    "Dak": (roof_cost, roof_saved_kWh, roof_co2_savings, roof_payback_time, roof_savings_euro),
    "Wanden": (wall_cost, wall_saved_kWh, wall_co2_savings, wall_payback_time, wall_savings_euro),
    "Ramen": (window_cost, window_saved_kWh, window_co2_savings, window_payback_time, window_savings_euro)
}

df = pd.DataFrame.from_dict(data, orient='index', columns=["Kosten (€)", "Besparing (kWh)", "CO2-besparing (kg)", "Terugverdientijd (jaar)", "Bespaarde energiekosten (€)"])
st.dataframe(df)

# Totale resultaten in een tabel
def get_label_color(energy_label):
    label_colors = {
        "G": "#FF0000",  # Red
        "F": "#FF4000",  # Orange-Red
        "E": "#FF8000",  # Orange
        "D": "#FFBF00",  # Yellow-Orange
        "C": "#FFFF00",  # Yellow
        "B": "#BFFF00",  # Yellow-Green
        "A": "#80FF00",  # Light Green
        "A+": "#40FF00",  # Green
        "A++": "#00FF00",  # Bright Green
        "A+++": "#00FF80",  # Light Blue-Green
        "A++++": "#00FFBF",  # Blue-Green
        "A+++++": "#00FFFF"  # Cyan
    }
    return label_colors.get(energy_label, "#FFFFFF")  # Default to white if not found

st.subheader("Totale resultaten")

totals = {
    "cost": total_cost,
    "savings": total_savings,
    "co2_savings": total_co2_savings,
    "payback": total_payback,
    "total_savings_euro": total_savings_euro,
    "total_kwh_per_m2_per_year": total_kwh_per_m2_per_year,
    "energy_label": energy_label
}

label_color = get_label_color(totals["energy_label"])

totals_text = f"""
**Totale Kosten:** €{totals['cost']:,.2f}  
**Totale Besparing per jaar:** {totals['savings']:,.2f} kWh  
**Totale CO2-besparing:** {totals['co2_savings']:,.2f} kg  
**Totale Terugverdientijd:** {totals['payback']:,.2f} jaar  
**Totale Bespaarde energiekosten:** €{totals['total_savings_euro']:,.2f}  
**Totale kWh per m² per jaar:** {totals['total_kwh_per_m2_per_year']:,.2f}  
**Energielabel:** <span style="background-color:{label_color}; padding: 5px; border-radius: 5px;">{totals['energy_label']}</span>
"""

st.markdown(totals_text, unsafe_allow_html=True)

# PDF knop
if st.button('Genereer PDF'):
    data = {
        'Vloer': (floor_cost, floor_saved_kWh, floor_co2_savings, floor_payback_time, floor_savings_euro),
        'Dak': (roof_cost, roof_saved_kWh, roof_co2_savings, roof_payback_time, roof_savings_euro),
        'Wanden': (wall_cost, wall_saved_kWh, wall_co2_savings, wall_payback_time, wall_savings_euro),
        'Ramen': (window_cost, window_saved_kWh, window_co2_savings, window_payback_time, window_savings_euro)
    }
    totals = {
        'cost': total_cost,
        'savings': total_savings,
        'co2_savings': total_co2_savings,
        'payback': total_payback,
        'total_savings_euro': total_savings_euro,
        'energy_label': energy_label
    }
    
    # PDF genereren
    pdf_file = generate_pdf(data, totals)
    
    # Lees de gegenereerde PDF in binair formaat
    with open(pdf_file, "rb") as file:
        pdf_data = file.read()
    
    # Download knop voor de PDF
    st.download_button(
        label="Download PDF",
        data=pdf_data,
        file_name=pdf_file,
        mime="application/pdf"
    )

# AI Advies
if st.button('Vraag AI Advies'):
    # Calculate a score for each category based on savings and payback time
    scores = {
        'Vloer': floor_savings_euro / floor_payback_time if floor_payback_time != float('inf') else 0,
        'Dak': roof_savings_euro / roof_payback_time if roof_payback_time != float('inf') else 0,
        'Wanden': wall_savings_euro / wall_payback_time if wall_payback_time != float('inf') else 0,
        'Ramen': window_savings_euro / window_payback_time if window_payback_time != float('inf') else 0
    }
    
    # Determine the best category to focus on
    best_category = max(scores, key=scores.get)
    
    # Get the savings and payback time for the best category
    if best_category == 'Vloer':
        savings = floor_savings_euro
        payback_time = floor_payback_time
    elif best_category == 'Dak':
        savings = roof_savings_euro
        payback_time = roof_payback_time
    elif best_category == 'Wanden':
        savings = wall_savings_euro
        payback_time = wall_payback_time
    else:  # 'Ramen'
        savings = window_savings_euro
        payback_time = window_payback_time
    
    # Provide advice based on the best category
    advies = (f"Op basis van uw doel om zoveel mogelijk geld te besparen in de kortst mogelijke tijd, raden wij aan om te focussen op de {best_category.lower()}. "
              f"Dit zal naar verwachting een besparing van €{savings:.2f} per jaar opleveren met een terugverdientijd van {payback_time:.2f} jaar.")
    st.write(advies)
