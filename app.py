import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import dash
from dash import Dash, dcc, html

url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vThoMrLbYM2Fxkps_AioTfF1NfklbLmSAcbs7mlEc_EWbwUZkOc0SShkvaZ8IkpiV_1VycEg9Mvm4vh/pub?gid=1286856073&single=true&output=csv'
df = pd.read_csv(url)


df['year'] = df['Year'].astype(str) + ' Q' + df['quarter'].astype(str)
df['route'] = df['city1'] + " to " + df['city2']
df['total_revenue'] = df['passengers'] * df['fare']


def create_carrier_fare_plot(df):
    carrier_fare_over_time = df.groupby(['year', 'carrier_lg'])['fare'].mean().reset_index()
    unique_carriers = carrier_fare_over_time['carrier_lg'].unique()
    carrier_data = {
        carrier: carrier_fare_over_time[carrier_fare_over_time['carrier_lg'] == carrier]
        for carrier in unique_carriers
    }

    initial_carrier = unique_carriers[0]
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=carrier_data[initial_carrier]['year'],
            y=carrier_data[initial_carrier]['fare'],
            mode='lines+markers',
            name=initial_carrier
        )
    )

    dropdown_buttons = [
        {
            "label": carrier,
            "method": "update",
            "args": [
                {
                    "x": [carrier_data[carrier]['year']],
                    "y": [carrier_data[carrier]['fare']],
                    "type": "scatter",
                },
                {"title": f"Average Fare Over Time for Carrier: {carrier}"}
            ],
        }
        for carrier in unique_carriers
    ]

    fig.update_layout(
        title="Average Fare Over Time by Carrier",
        xaxis_title="Year",
        yaxis_title="Average Fare",
        xaxis_tickangle=-90,
        updatemenus=[
            {
                "buttons": dropdown_buttons,
                "direction": "down",
                "showactive": True,
                "x": 0.5,
                "xanchor": "center",
                "y": 1.15,
                "yanchor": "top",
            }
        ]
    )

    return fig

def create_passengers_over_time_plot(df):
    average_passengers_over_time = df.groupby(['year', 'carrier_lg'])['passengers'].mean().reset_index()
    unique_carriers = average_passengers_over_time['carrier_lg'].unique()
    carrier_data = {
        carrier: average_passengers_over_time[average_passengers_over_time['carrier_lg'] == carrier]
        for carrier in unique_carriers
    }

    initial_carrier = unique_carriers[0]
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=carrier_data[initial_carrier]['year'],
            y=carrier_data[initial_carrier]['passengers'],
            mode='lines+markers',
            name=initial_carrier
        )
    )

    dropdown_buttons = [
        {
            "label": carrier,
            "method": "update",
            "args": [
                {
                    "x": [carrier_data[carrier]['year']],
                    "y": [carrier_data[carrier]['passengers']],
                    "type": "scatter",
                },
                {"title": f"Average Passengers Over Time for Carrier: {carrier}"}
            ],
        }
        for carrier in unique_carriers
    ]

    fig.update_layout(
        title="Average Passengers Over Time by Carrier",
        xaxis_title="Year",
        yaxis_title="Average Passengers",
        legend_title="Carrier",
        updatemenus=[
            {
                "buttons": dropdown_buttons,
                "direction": "down",
                "showactive": True,
                "x": 0.5,
                "xanchor": "center",
                "y": 1.15,
                "yanchor": "top",
            }
        ]
    )

    return fig


def create_top_routes_plot(df):

    df['route'] = df['city1'] + " to " + df['city2']
    top_routes_passengers = (
        df.groupby('route', as_index=False)['passengers']
        .sum()
        .sort_values(by='passengers', ascending=False)
        .head(10)
    )

 
    top_routes_fare = (
        df.groupby('route', as_index=False)['fare']
        .mean()
        .sort_values(by='fare', ascending=False)
        .head(10)
    )

    # Assign unique colors for the top 10 routes
    color_scale = px.colors.qualitative.Plotly[:10]

    fig = go.Figure()

    # Add bar trace for top 10 routes by passengers
    for i, route in enumerate(top_routes_passengers['route']):
        fig.add_trace(
            go.Bar(
                x=[route],
                y=[top_routes_passengers[top_routes_passengers['route'] == route]['passengers'].values[0]],
                name=route,
                marker=dict(color=color_scale[i]),
                # Within the create_top_routes_plot function, change the hovertemplate argument:
                hovertemplate=f"Route: {route}<br>Passengers: %{{y}}<extra></extra>"
            )
        )

    # Dropdown buttons for toggle
    dropdown_buttons = [
        dict(
            label="Passengers",
            method="update",
            args=[
                {"visible": [True] * 10 + [False] * 10},  # Show passenger bars
                {"title": "Top 10 Routes by Passengers", "yaxis": {"title": "Passenger Volume"}}
            ]
        ),
        dict(
            label="Fare",
            method="update",
            args=[
                {"visible": [False] * 10 + [True] * 10},  # Show fare bars
                {"title": "Top 10 Routes by Average Fare", "yaxis": {"title": "Average Fare (USD)"}}
            ]
        )
    ]

    # Add bar trace for top 10 routes by fare
    for i, route in enumerate(top_routes_fare['route']):
        fig.add_trace(
            go.Bar(
                x=[route],
                y=[top_routes_fare[top_routes_fare['route'] == route]['fare'].values[0]],
                name=route,
                marker=dict(color=color_scale[i]),
                hovertemplate=f"Route: {route}<br>Average Fare: %{{y}}<extra></extra>"
            )
        )

    # Update layout
    fig.update_layout(
        title="Top 10 Routes by Passengers",
        xaxis_title="Routes",
        yaxis_title="Passenger Volume",
        legend_title="Routes",
        updatemenus=[
            dict(
                buttons=dropdown_buttons,
                direction="down",
                showactive=True,
                x=0.5,
                xanchor="center",
                y=1.15,
                yanchor="top"
            )
        ],
        barmode="stack",
        template="plotly_white",
        margin=dict(t=100, b=100, l=50, r=50),
        height=600,
        width=900
    )

    return fig


def create_carrier_features_plots(df):

    # First figure - Fare and Market Share
    fig1 = go.Figure()
    features1 = ['fare', 'large_ms']
    titles1 = ['Average Fare', 'Market Share']
    colors1 = ['#1f77b4', '#ff7f0e']

    for feature, title, color in zip(features1, titles1, colors1):
        avg_values = df.groupby('carrier_lg')[feature].mean().reset_index()
        fig1.add_trace(
            go.Bar(
                x=avg_values['carrier_lg'],
                y=avg_values[feature],
                name=title,
                text=avg_values[feature].round(2),
                textposition='outside',
                marker_color=color
            )
        )

    # Dynamic annotation for lowest average fare
    lowest_fare_carrier = df.groupby('carrier_lg')['fare'].mean().idxmin()
    lowest_fare_value = df.groupby('carrier_lg')['fare'].mean().min()
    fig1.add_annotation(
        x=lowest_fare_carrier,
        y=lowest_fare_value,
        text="Lowest average fare!",
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-50,
        font=dict(color="black", size=12),
        arrowcolor="black"
    )

    fig1.update_layout(
        title="Carrier-wise Fare and Market Share",
        barmode='group',
        height=400,
        width=800,
        xaxis_title="Carrier",
        yaxis_title="Values",
        legend_title="Features",
        template="plotly_white"
    )

    # Second figure - Passengers, Distance, and Low Fare
    fig2 = go.Figure()
    features2 = ['passengers', 'nsmiles', 'fare_low']
    titles2 = ['Passengers', 'Distance (nsmiles)', 'Low Fare']
    colors2 = ['#2ca02c', '#d62728', '#9467bd']

    for feature, title, color in zip(features2, titles2, colors2):
        avg_values = df.groupby('carrier_lg')[feature].mean().reset_index()
        fig2.add_trace(
            go.Bar(
                x=avg_values['carrier_lg'],
                y=avg_values[feature],
                name=title,
                text=avg_values[feature].round(0),
                textposition='outside',
                marker_color=color
            )
        )

    # Dynamic annotation for highest passenger volume
    highest_passenger_carrier = df.groupby('carrier_lg')['passengers'].mean().idxmax()
    highest_passenger_value = df.groupby('carrier_lg')['passengers'].mean().max()
    fig2.add_annotation(
        x=highest_passenger_carrier,
        y=highest_passenger_value,
        text="Highest passenger volume!",
        showarrow=True,
        arrowhead=2,
        ax=50,
        ay=-50,
        font=dict(color="black", size=12),
        arrowcolor="black"
    )

    fig2.update_layout(
        title="Carrier-wise Passengers, Distance, and Low Fare",
        barmode='group',
        height=400,
        width=800,
        xaxis_title="Carrier",
        yaxis_title="Values",
        legend_title="Features",
        template="plotly_white"
    )

    return fig1, fig2


# Function to create city-level passenger and revenue visualization
def create_city_level_plots(df):
    
    city_passenger_data = df.groupby('city1')['passengers'].sum().reset_index()
    city_passenger_data.columns = ['City', 'Total Passengers']


    city_revenue_data = df.groupby('city1')['total_revenue'].sum().reset_index()
    city_revenue_data.columns = ['City', 'Total Revenue']

    # Create the bar traces for both metrics
    trace1 = go.Bar(
        x=city_passenger_data.sort_values('Total Passengers', ascending=False).head(20)['City'],
        y=city_passenger_data.sort_values('Total Passengers', ascending=False).head(20)['Total Passengers'],
        name="Passenger Volume"
    )

    trace2 = go.Bar(
        x=city_revenue_data.sort_values('Total Revenue', ascending=False).head(20)['City'],
        y=city_revenue_data.sort_values('Total Revenue', ascending=False).head(20)['Total Revenue'],
        name="Revenue Contribution"
    )


    fig = go.Figure()

    # Add both traces to the figure
    fig.add_trace(trace1)
    fig.add_trace(trace2)

    # Update the layout to include dropdowns for filtering
    fig.update_layout(
        title="Top 20 Cities: Passenger Volume and Revenue Contribution",
        xaxis=dict(title="City"),
        yaxis=dict(title="Value"),
        updatemenus=[
            dict(
                buttons=[
                    dict(
                        label="Passenger Volume",
                        method="update",
                        args=[
                            {"visible": [True, False]},  # Show only the first trace
                            {"title": "Top 20 Cities by Passenger Volume", "yaxis": {"title": "Passenger Volume"}}
                        ]
                    ),
                    dict(
                        label="Revenue Contribution",
                        method="update",
                        args=[
                            {"visible": [False, True]},  # Show only the second trace
                            {"title": "Top 20 Cities by Revenue Contribution", "yaxis": {"title": "Revenue (USD)"}}
                        ]
                    )
                ],
                direction="down",
                showactive=True,
            )
        ]
    )

    return fig

# Create Dash app
app = Dash(__name__)

# Create visualizations
fare_over_time_fig = create_carrier_fare_plot(df)
passengers_over_time_fig = create_passengers_over_time_plot(df)
top_routes_fig = create_top_routes_plot(df)
carrier_fare_fig, carrier_passengers_fig = create_carrier_features_plots(df)
city_level_fig = create_city_level_plots(df)

# App layout
app.layout = html.Div([
    html.H1("Airline Features Analysis", style={'textAlign': 'center'}),

    # Fare Over Time Visualization
    dcc.Graph(figure=fare_over_time_fig),
    dcc.Markdown("""
        ### Fare Over Time
        - Average fare trends for different carriers
        - Dropdown menu allows easy comparison between carriers
    """),

    # Passengers Over Time Visualization
    dcc.Graph(figure=passengers_over_time_fig),
    dcc.Markdown("""
        ### Passengers Over Time
        - Track passenger numbers for different carriers across years
        - All the carriers have see their all time passenger low during the year 2020
    """),

    # Top Routes Visualization
    dcc.Graph(figure=top_routes_fig),
    dcc.Markdown("""
        ### Top Routes Analysis
        - Compare top routes by passengers and average fare
        - Switch between views using the dropdown menu
    """),

    # City-Level Analysis
    dcc.Graph(figure=city_level_fig),
    dcc.Markdown("""
        ### City-Level Analysis
        - Explore top cities by passenger volume and revenue contribution
        - Toggle between views using the dropdown menu
    """),

    # Carrier Features Visualizations
    html.Div([
        dcc.Graph(figure=carrier_fare_fig, style={'display': 'inline-block', 'width': '50%'}),
        dcc.Graph(figure=carrier_passengers_fig, style={'display': 'inline-block', 'width': '50%'})
    ]),
    dcc.Markdown("""
        ### Carrier Comparison
        - Left: Average Fare and Market Share by Carrier
        - Right: Passengers, Distance, and Low Fare Metrics
        - Annotations highlight key insights
    """)
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)