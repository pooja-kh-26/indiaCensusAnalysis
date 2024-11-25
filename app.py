import base64
import io
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
import seaborn as sns
import gradio as gr

# Load and clean the dataset
def load_data():
    df = pd.read_csv('population.csv')
    columns_to_convert = [
        "Population", "Males", "Females", "Rural Population",
        "Urban Population", "Area (km*km)", "Density (1/km*km)"
    ]
    for col in columns_to_convert:
        df[col] = pd.to_numeric(df[col].str.replace(",", ""), errors='coerce')
    df["Decadal Growth (%)"] = pd.to_numeric(df["Decadal Growth (%)"].str.replace("%", ""), errors='coerce')
    df["Urbanization Rate"] = df["Urban Population"] / df["Population"]
    return df

data = load_data()

# Function to generate all charts and return them as HTML
def generate_dashboard():
    plots = []

    # Gender distribution pie chart
    gender_data = pd.DataFrame({
        'Gender': ['Male', 'Female'],
        'Population': [data['Males'].sum(), data['Females'].sum()]
    })
    plt.figure(figsize=(4, 2))
    plt.pie(gender_data['Population'], labels=gender_data['Gender'], autopct='%1.1f%%', colors=['blue', 'pink'])
    gender_img = io.BytesIO()
    plt.savefig(gender_img, format='png')
    plt.close()
    plots.append(f'<img src="data:image/png;base64,{base64.b64encode(gender_img.getvalue()).decode()}">')

    # Rural vs Urban Population Distribution
    data['Rural Population (%)'] = (data['Rural Population'] / data['Population']) * 100
    data['Urban Population (%)'] = (data['Urban Population'] / data['Population']) * 100
    plt.figure(figsize=(25, 20))
    sns.barplot(data=data.sort_values("Population", ascending=False), x="State", y="Rural Population (%)", color='skyblue', label='Rural Population (%)')
    sns.barplot(data=data.sort_values("Population", ascending=False), x="State", y="Urban Population (%)", color='orange', label='Urban Population (%)')
    plt.xticks(rotation=90)
    plt.title("Rural vs Urban Population Distribution by State")
    plt.ylabel("Population (%)")
    plt.legend()
    urban_rural_img = io.BytesIO()
    plt.savefig(urban_rural_img, format='png')
    plt.close()
    plots.append(f'<img src="data:image/png;base64,{base64.b64encode(urban_rural_img.getvalue()).decode()}">')

    # Population Density Distribution
    density_data = data[['State', 'Density (1/km*km)']].sort_values(by='Density (1/km*km)', ascending=False)
    plt.figure(figsize=(25, 20))
    plt.bar(density_data['State'], density_data['Density (1/km*km)'], color='purple')
    plt.xticks(rotation=90)
    plt.xlabel("State")
    plt.ylabel("Population Density (per km²)")
    plt.title("Distribution of Population Density Across States")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.ylim(0, 12000)  # Adjust if necessary
    plt.yticks(range(0, 12001, 500))
    plt.grid(axis='y', linestyle='--', alpha=0.7)  # Add grid lines on y-axis
    density_img = io.BytesIO()
    plt.savefig(density_img, format='png')
    plt.close()
    plots.append(f'<img src="data:image/png;base64,{base64.b64encode(density_img.getvalue()).decode()}">')

    # Correlation Heatmap
    columns_of_interest = ['Literacy Rate (%)', 'Urban Population', 'Density (1/km*km)']
    correlation_matrix = data[columns_of_interest].corr()
    plt.figure(figsize=(8, 6))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", cbar=True)
    heatmap_img = io.BytesIO()
    plt.savefig(heatmap_img, format='png')
    plt.close()
    plots.append(f'<img src="data:image/png;base64,{base64.b64encode(heatmap_img.getvalue()).decode()}">')

    # Total Population by Category (Males, Females, Urban, Rural)
    total_males = data['Males'].sum()
    total_females = data['Females'].sum()
    total_urban = data['Urban Population'].sum()
    total_rural = data['Rural Population'].sum()

    categories = ['Males', 'Females', 'Urban Population', 'Rural Population']
    totals = [total_males, total_females, total_urban, total_rural]
    colors = ['blue', 'pink', 'orange', 'green']
    plt.figure(figsize=(7, 4.5))
    plt.bar(categories, totals, color=colors)
    plt.xlabel('Category')
    plt.ylabel('Population')
    plt.title('Total Population by Category (Males, Females, Urban, Rural)')
    plt.grid(axis='y', linestyle='--', alpha=0.7)  # Add grid lines on y-axis
    column_img = io.BytesIO()
    plt.savefig(column_img, format='png')
    plt.close()
    plots.append(f'<img src="data:image/png;base64,{base64.b64encode(column_img.getvalue()).decode()}">')

    # Top 10 States by Highest Decadal Growth
    top_10_growth_states = data.sort_values(by='Decadal Growth (%)', ascending=False).head(10)
    plt.figure(figsize=(10, 10))
    colors = cm.get_cmap('viridis', 10)(range(10))  # Define colors from the viridis colormap
    plt.pie(top_10_growth_states['Decadal Growth (%)'],
            labels=top_10_growth_states['State'],
            autopct='%1.1f%%',
            startangle=140,
            colors=colors)
    plt.title("Top 10 States by Highest Decadal Growth (%)")
    pie_img = io.BytesIO()
    plt.savefig(pie_img, format='png')
    plt.close()
    plots.append(f'<img src="data:image/png;base64,{base64.b64encode(pie_img.getvalue()).decode()}">')

    # Population Percentage by State (Line Chart)
    sorted_data = data.sort_values(by="Population", ascending=False)
    total_population = sorted_data["Population"].sum()
    sorted_data["Population (%)"] = (sorted_data["Population"] / total_population) * 100
    plt.figure(figsize=(15, 13))
    plt.plot(sorted_data["State"], sorted_data["Population (%)"], marker='o', color='b', label='Population (%)')
    plt.xticks(rotation=90)
    plt.xlabel("State")
    plt.ylabel("Population (%)")
    plt.title("Population Percentage by State")
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)  # Add grid lines on y-axis
    plt.grid(axis='x', linestyle='--', alpha=0.7)  # Add grid lines on y-axis
    line_img = io.BytesIO()
    plt.savefig(line_img, format='png')
    plt.close()
    plots.append(f'<img src="data:image/png;base64,{base64.b64encode(line_img.getvalue()).decode()}">')

    # Combine all plots into HTML
    dashboard_html = "<div style='text-align: center;'>"
    for plot in plots:
        dashboard_html += f"<div style='margin-bottom: 20px;'>{plot}</div>"
    dashboard_html += "</div>"

    return dashboard_html

# Create Gradio interface
iface = gr.Interface(
    fn=generate_dashboard,
    inputs=[],
    outputs="html",
    title="Population Analysis Dashboard",
    description="Visualizations and insights from the population dataset"
)

# Launch the Gradio app
if __name__ == "__main__":
    iface.launch(share=True)
