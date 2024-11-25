# Import required libraries
import base64
import io
from flask import Flask, render_template
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
import seaborn as sns

#Initialize the flask app
app = Flask(__name__)

#Load and clean the dataset
def load_data():
    df = pd.read_csv('population.csv')
    print(df.columns)  
    columns_to_convert = ["Population", "Males", "Females", "Rural Population", "Urban Population", "Area (km*km)", "Density (1/km*km)"]
    for col in columns_to_convert:
        df[col] = pd.to_numeric(df[col].str.replace(",", ""), errors='coerce')
    df["Decadal Growth (%)"] = pd.to_numeric(df["Decadal Growth (%)"].str.replace("%", ""), errors='coerce')
    df["Urbanization Rate"] = df["Urban Population"] / df["Population"]
    return df

data = load_data()

@app.route('/')
def index():
    #Gender distribution pie chart
    gender_data = pd.DataFrame({
        'Gender': ['Male', 'Female'],
        'Population': [data['Males'].sum(), data['Females'].sum()]
    })
    plt.figure(figsize=(4, 2))
    plt.pie(gender_data['Population'], labels=gender_data['Gender'], autopct='%1.1f%%', colors=['blue', 'pink'])
    gender_img = io.BytesIO()
    plt.savefig(gender_img, format='png')
    gender_img.seek(0)
    gender_chart = base64.b64encode(gender_img.getvalue()).decode()

    # Calculate percentage values for Rural and Urban populations
    data['Rural Population (%)'] = (data['Rural Population'] / data['Population']) * 100
    data['Urban Population (%)'] = (data['Urban Population'] / data['Population']) * 100

    # Plot the Rural vs Urban Population Distribution in terms of percentage
    plt.figure(figsize=(25, 20))
    sns.barplot(data=data.sort_values("Population", ascending=False), x="State", y="Rural Population (%)", color='skyblue', label='Rural Population (%)')
    sns.barplot(data=data.sort_values("Population", ascending=False), x="State", y="Urban Population (%)", color='orange', label='Urban Population (%)')
    plt.xticks(rotation=90)
    plt.title("Rural vs Urban Population Distribution by State (Percentage)")
    plt.ylabel("Population (%)")
    plt.xlabel("State")
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)  # Add grid lines on y-axis

    # Save the plot
    urban_rural_img = io.BytesIO()
    plt.savefig(urban_rural_img, format='png')
    urban_rural_img.seek(0)
    urban_rural_chart = base64.b64encode(urban_rural_img.getvalue()).decode()

    # Population Density Distribution
    # Sort states by population density
    density_data = data[['State', 'Density (1/km*km)']].sort_values(by='Density (1/km*km)', ascending=False)

    # Plot the population density distribution across states
    plt.figure(figsize=(25, 20))
    plt.bar(density_data['State'], density_data['Density (1/km*km)'], color='purple')
    plt.xticks(rotation=90)
    plt.xlabel("State")
    plt.ylabel("Population Density (per km²)")
    plt.title("Distribution of Population Density Across States")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Set a higher y-axis limit for more range and add grid lines for readability
    plt.ylim(0, 12000)  # Set y-axis limit; adjust 12000 to a suitable maximum if needed
    plt.yticks(range(0, 12001, 500))  # Define ticks every 1000 units up to 12000
    plt.grid(axis='y', linestyle='--', alpha=0.7)  # Add grid lines on y-axis


    # Save the plot to a BytesIO object and encode it for rendering
    density_img = io.BytesIO()
    plt.savefig(density_img, format='png')
    density_img.seek(0)
    density_chart = base64.b64encode(density_img.getvalue()).decode()

    # Correlation Heatmap
    columns_of_interest = ['Literacy Rate (%)', 'Urban Population', 'Density (1/km*km)']
    correlation_matrix = data[columns_of_interest].corr()
    plt.figure(figsize=(8, 6))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", cbar=True)
    heatmap_img = io.BytesIO()
    plt.savefig(heatmap_img, format='png')
    heatmap_img.seek(0)
    heatmap_chart = base64.b64encode(heatmap_img.getvalue()).decode()
    
    # Calculate total values for males, females, urban, and rural populations
    total_males = data['Males'].sum()
    total_females = data['Females'].sum()
    total_urban = data['Urban Population'].sum()
    total_rural = data['Rural Population'].sum()

    # Data for the column chart
    categories = ['Males', 'Females', 'Urban Population', 'Rural Population']
    totals = [total_males, total_females, total_urban, total_rural]
    colors = ['blue', 'pink', 'orange', 'green']

    # Plot the column chart
    plt.figure(figsize=(7, 4.5))
    plt.bar(categories, totals, color=colors)
    plt.xlabel('Category')
    plt.ylabel('Population')
    plt.title('Total Population by Category (Males, Females, Urban, Rural)')
    plt.grid(axis='y', linestyle='--', alpha=0.7)  # Add grid lines on y-axis

    
    # Save the plot to a BytesIO object and encode it for rendering
    column_img = io.BytesIO()
    plt.savefig(column_img, format='png')
    column_img.seek(0)
    column_chart = base64.b64encode(column_img.getvalue()).decode()
    
    # Get top 10 states by highest decadal growth
    top_10_growth_states = data.sort_values(by='Decadal Growth (%)', ascending=False).head(10)

    # Generate the pie chart
    plt.figure(figsize=(10, 10))
    colors = cm.get_cmap('viridis', 10)(range(10))  # Define colors from the viridis colormap
    plt.pie(top_10_growth_states['Decadal Growth (%)'], 
            labels=top_10_growth_states['State'], 
            autopct='%1.1f%%', 
            startangle=140, 
            colors=colors)
    plt.title("Top 10 States by Highest Decadal Growth (%)")

    # Save pie chart to a BytesIO object
    pie_img = io.BytesIO()
    plt.savefig(pie_img, format='png')
    pie_img.seek(0)
    pie_chart = base64.b64encode(pie_img.getvalue()).decode()
    
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

    # Save line chart
    line_img = io.BytesIO()
    plt.savefig(line_img, format='png')
    line_img.seek(0)
    line_chart = base64.b64encode(line_img.getvalue()).decode()

    return render_template('index.html', gender_chart=gender_chart, urban_rural_chart=urban_rural_chart, 
                           density_chart=density_chart, heatmap_chart=heatmap_chart, 
                           column_chart=column_chart,pie_chart=pie_chart,line_chart=line_chart)
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)