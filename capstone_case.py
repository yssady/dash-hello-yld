#%%


import dash
from dash import dcc, html, ctx
import pandas as pd
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go


# global variables references to indicate if in editing mode. callback will run when started and change this to False
is_editing = False

# csv database in IE 271\Capstone Case -Dysangco1
df = pd.read_csv('investment.csv')

# copy of db to be used while data is not saved
df_copy = df.copy()

# where dropdown will get its data
scenarios = df_copy['scenario_name']

# track current selection through its index in dataframe. start at None since it is empty
current_selected_index = None

# for storing inputs in form
form_data = []

# chart figures
donut_figure = {}
waterfall_figure = {}

# for components styling
calculation_input = {'fontSize': 12,
                     'padding': 5,
                     'border': 'hidden',
                     'textAlign': 'right',
                     'outline': None,
                     'width': '100%'}

# csv filename for database. initial empty csv file only has column names
DB_FILENAME = 'investment.csv'

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
application = app.server


app.layout = html.Div([
    html.Div(style={'background-color': 'rgb(0,123,255)', 'width': '100%', 'height': 40}),
    html.Div([
        html.Div([
            html.H2('Return of Investment Inputs:',
                    style={'color': 'rgb(0,123,255)',
                           'fontSize': 18,
                           'fontFamily': 'Verdana',
                           'font-weight': 'bold'}
                    ),
            html.Table([
                html.Tr(children=[
                    html.Td("Scenario Name:",
                            style={'width': '40%',
                                   'font-weight': 'bold',
                                   'fontSize': 12}),
                    html.Td(dcc.Input(id='scenarioName',
                                      type='text',
                                      value=[],
                                      style={'fontSize': 12,
                                             'padding': 5,
                                             "borderWidth": ".1px",
                                             "borderColor": "black"}))
                ]),
                html.Tr(children=[
                    html.Td("Total Hits:",
                            style={'width': '40%',
                                   'font-weight': 'bold',
                                   'fontSize': 12}),
                    html.Td(dcc.Input(id='totalHits',
                                      type='number',
                                      value=1000000,
                                      style={'fontSize': 12,
                                             'padding': 5,
                                             "borderWidth": ".1px",
                                             "borderColor": "black"}))
                ]),
                html.Tr(children=[
                    html.Td("Conversion Rate:",
                            style={'width': '40%',
                                   'font-weight': 'bold',
                                   'fontSize': 12}),
                    html.Td(dcc.Input(id='conversionRate',
                                      type='number',
                                      value=60,
                                      style={'fontSize': 12,
                                             'padding': 5,
                                             "borderWidth": ".1px",
                                             "borderColor": "black"}))
                ]),
                html.Tr(children=[
                    html.Td("Revenue Per Purchase (PhP):",
                            style={'width': '40%',
                                   'font-weight': 'bold',
                                   'fontSize': 12}),
                    html.Td(dcc.Input(id='revenuePerPurchase',
                                      type='number',
                                      value=50,
                                      style={'fontSize': 12,
                                             'padding': 5,
                                             "borderWidth": ".1px",
                                             "borderColor": "black"}))
                    ]),
                html.Tr(children=[
                    html.Td("Number of Times of Purchase per Converted User per Year:",
                            style={'width': '40%',
                                   'font-weight': 'bold',
                                   'fontSize': 12}),
                    html.Td(dcc.Input(id='purchasePerConvertedUser',
                                      type='number',
                                      value=2,
                                      style={'fontSize': 12,
                                             'padding': 5,
                                             "borderWidth": ".1px",
                                             "borderColor": "black"}))
                ]),
                html.Tr(children=[
                    html.Td("Total Cost of Sampling:",
                            style={'width': '40%',
                                   'font-weight': 'bold',
                                   'fontSize': 12}),
                    html.Td(dcc.Input(id='samplingCost',
                                      type='number',
                                      value=25000000,
                                      style={'fontSize': 12,
                                             'padding': 5,
                                             "borderWidth": ".1px",
                                             "borderColor": "black"}))
                ]),
                html.Tr(children=[
                    html.Td("% of Potential You are willing to allocate for sampling:",
                            style={'width': '40%',
                                   'font-weight': 'bold',
                                   'fontSize': 12}),
                    html.Td(dcc.Input(id='potentialRevenue',
                                      type='number',
                                      value=50,
                                      style={'fontSize': 12,
                                             'padding': 5,
                                             "borderWidth": ".1px",
                                             "borderColor": "black"}))
                ]),
            ], style={'width': '100%'}),

            html.Hr(),

            html.Button(
                id='submitButton',
                children='Calculate ROI',
                n_clicks=0,
                style={'fontSize': '15px',
                       'color': 'white',
                       'background-color': 'rgb(0,123,255)',
                       'float': 'middle',
                       'border-radius': '5px',
                       'border': '5px',
                       'cursor': 'pointer',
                       'width': '25%',
                       'padding': 5}
            ),

            html.Hr(),

            html.Div([
                html.Td("Select Scenario:",
                        style={'width': '40%',
                               'font-weight': 'bold',
                               'fontSize': 12}),
                html.Td(dcc.Dropdown(
                        id='scenario',
                        options=[{'label': value, 'value': index} for index, value in scenarios.items()],
                        style={'fontSize': 12,
                               "borderWidth": ".1px",
                               "borderColor": "black",
                               'margin-left': '50%',
                               'width': '115%'}))
            ], style={'width': '100%'}),

            dcc.Checklist(
                options=[
                    {'label': 'Edit Mode',
                     'value': False},
                ],
                id="mode",
                value=[],
                style={'margin-left': '41%',
                       'fontSize': 12,
                       'marginTop': '.5em'}

            ),

            html.Button(
                id='saveButton',
                children='Save Settings',
                n_clicks=0,
                style={'fontSize': '15px',
                       'color': 'white',
                       'background-color': 'rgb(0,123,255)',
                       'float': 'middle',
                       'border-radius': '5px',
                       'border': '5px',
                       'cursor': 'pointer',
                       'width': '25%',
                       'padding': 5,
                       'marginBottom': '.2em'}
            ),

            html.Br(),

            html.Button(
                id='deleteButton',
                children='Delete This Scenario',
                n_clicks=0,
                style={'fontSize': '15px',
                       'color': 'white',
                       'background-color': 'rgb(0,123,255)',
                       'float': 'middle',
                       'border-radius': '5px',
                       'border': '5px',
                       'cursor': 'pointer',
                       'width': '25%',
                       'padding': 5}
            ),

        ], style={'width': '30%',
                  'display': 'inline-block',
                  'float': 'left', 'marginTop': '0px'}
        ),

        html.Div([
            html.H2(children='Investment/Income Breakdown:',
                    style={'textAlign': 'center',
                           'color': 'rgb(0,123,255)',
                           'fontFamily': 'Verdana',
                           'fontSize': 18,
                           'font-weight': 'bold'}
                    ),
            dcc.Graph(id='donut',
                      figure=donut_figure,
                      style={'height': 400}
                      ),
            html.H2(children='ROI Parameters Computed:',
                    style={'color': 'rgb(0,123,255)',
                           'fontFamily': 'Verdana',
                           'textAlign': 'center',
                           'fontSize': 18,
                           'font-weight': 'bold'}
                    ),
            html.Table([
                html.Tr(children=[
                    html.Td("Total Potential Annual Revenue:",
                            style={'width': '50%',
                                   'fontSize': 12,
                                   "borderWidth": ".1px",
                                   "borderColor": "black"}),
                    html.Td(children=[dcc.Input(id='totalPotentialAR',
                                      type='text',
                                      disabled=True,
                                      value=[],
                                      style=calculation_input)],
                            style={"borderWidth": ".1px", "borderColor": "black"})
                ], style={'padding': 0}),
                html.Tr(children=[
                    html.Td("Unconverted Opportunity Revenue:",
                            style={'width': '50%',
                                   'fontSize': 12,
                                   "borderWidth": ".1px",
                                   "borderColor": "black"}),
                    html.Td(children=[dcc.Input(id='unconvertedOR',
                                      type='text',
                                      disabled=True,
                                      value=[],
                                      style=calculation_input)],
                            style={"borderWidth": ".1px", "borderColor": "black"})
                ], style={'padding': 0}),
                html.Tr(children=[
                    html.Td("Converted Revenue:",
                            style={'width': '50%',
                                   'fontSize': 12,
                                   "borderWidth": ".1px",
                                   "borderColor": "black"}),
                    html.Td(children=[dcc.Input(id='convertedRev',
                                      type='text',
                                      disabled=True,
                                      value=[],
                                      style=calculation_input)],
                            style={"borderWidth": ".1px", "borderColor": "black"})
                ], style={'padding': 0}),
                html.Tr(children=[
                    html.Td("Maximum Allowable Spend:",
                            style={'width': '50%',
                                   'fontSize': 12,
                                   "borderWidth": ".1px",
                                   "borderColor": "black"}),
                    html.Td(children=[dcc.Input(id='maxAS',
                                      type='text',
                                      disabled=True,
                                      value=[],
                                      style=calculation_input)],
                            style={"borderWidth": ".1px", "borderColor": "black"})
                ], style={'padding': 0}),
                html.Tr(children=[
                    html.Td("Maximum Spend per Hit:",
                            style={'width': '50%',
                                   'fontSize': 12,
                                   "borderWidth": ".1px",
                                   "borderColor": "black"}),
                    html.Td(children=[dcc.Input(id='maxSH',
                                      type='text',
                                      disabled=True,
                                      value=[],
                                      style=calculation_input)],
                            style={"borderWidth": ".1px", "borderColor": "black"}),
                ], style={'padding': 0}),
            ], style={'width': '100%'}),

            html.Br(),

            html.H2(children='Estimated Net Profit From Sampling:',
                    style={'color': 'rgb(0,123,255)',
                           'fontFamily': 'Verdana',
                           'textAlign': 'center',
                           'fontSize': 18,
                           'font-weight': 'bold'}
                    ),

            html.Table([
                html.Tr(children=[
                    html.Td("Net Profit:",
                            className='netProfit',
                            style={'width': '50%',
                                   'fontSize': 12,
                                   "borderWidth": ".1px",
                                   "borderColor": "black"}),
                    html.Td(children=[dcc.Input(id='netProfit',
                                      type='text',
                                      disabled=True,
                                      value=[],
                                      style=calculation_input)],
                            style={"borderWidth": ".1px", "borderColor": "black"}),
                        ], style={'padding': 0}),
            ], style={'width': '100%'}),



        ], style={'width': '30%',
                  'display': 'inline-block',
                  'float': 'left',
                  'marginTop': '0px'}),

        html.Div([
            html.H2(children='Waterfall Chart',
                    style={'textAlign': 'center',
                           'color': 'rgb(0,123,255)',
                           'fontFamily': 'Verdana',
                           'fontSize': 18,
                           'font-weight': 'bold'}
                    ),
            dcc.Graph(id='waterfall',
                      figure=waterfall_figure,
                      style={'color': 'black',
                             'fontSize': 10,
                             'fontFamily': 'calibri',
                             'height': 600,
                             'width': '120%'}
                      ),

        ], style={'width': '30%',
                  'display': 'inline-block',
                  'float': 'left',
                  'marginTop': '0px'}),

        ]),

    ])


@app.callback(
    [Output('scenario', 'options'),
     Output('scenario', 'value'),
     Output('scenarioName', 'value'),
     Output('totalHits', 'value'),
     Output('conversionRate', 'value'),
     Output('revenuePerPurchase', 'value'),
     Output('purchasePerConvertedUser', 'value'),
     Output('samplingCost', 'value'),
     Output('potentialRevenue', 'value'),
     Output('totalPotentialAR', 'value'),
     Output('unconvertedOR', 'value'),
     Output('convertedRev', 'value'),
     Output('maxAS', 'value'),
     Output('maxSH', 'value'),
     Output('netProfit', 'value'),
     Output('donut', 'figure'),
     Output('waterfall', 'figure')],
    Input('deleteButton', 'n_clicks'),
    Input('saveButton', 'n_clicks'),
    Input('mode', 'value'),
    Input('scenario', 'value'),
    Input('submitButton', 'n_clicks'),
    [State('scenarioName', 'value'),
     State('totalHits', 'value'),
     State('conversionRate', 'value'),
     State('revenuePerPurchase', 'value'),
     State('purchasePerConvertedUser', 'value'),
     State('samplingCost', 'value'),
     State('potentialRevenue', 'value'),
     State('scenario', 'value')]
)
def action(
        del_btn,
        save_btn,
        edit_checkbox,
        scenario_action_value,
        calculate_btn,
        scenario_name,
        total_hits,
        conversion_rate,
        revenue_per_purchase,
        purchase_per_converted_user,
        sampling_cost,
        potential_revenue,
        scenario_value):
    global form_data
    global df_copy
    global scenarios
    global is_editing
    global current_selected_index
    global donut_figure
    global waterfall_figure

    # initialized variables for calculating ROI output
    total_potential_ar = 0
    unconverted_or = 0
    converted_rev = 0
    net_profit = 0
    max_as = 0
    max_sh = 0

    # this will be the updated list of dropdown options
    new_scenarios = []

    # to know which component is involved in the input
    triggered_id = ctx.triggered_id

    # save button clicked
    if triggered_id == 'saveButton':
        form_data = [scenario_name,
                     total_hits,
                     conversion_rate,
                     revenue_per_purchase,
                     purchase_per_converted_user,
                     sampling_cost,
                     potential_revenue]

        # EDIT MODE
        if is_editing:
            # update existing record by getting index in dataframe then change it with data in form_data
            # it does not matter if scenario name exists or not
            df_copy.loc[scenario_action_value] = form_data
            
        # ADD MODE
        else:
            # if scenario name does not exist and is in add mode, add a new record
            if scenario_name not in df_copy['scenario_name'].tolist():

                # add new row to end of DataFrame
                df_copy.loc[len(df_copy.index)] = form_data

        # save dataframe into csv database
        df_copy.to_csv(DB_FILENAME, index=False)

    # delete button clicked
    if triggered_id == 'deleteButton':

        # delete record and is on edit mode
        if is_editing:

            # delete row from dataframe
            df_copy.drop(index=int(scenario_value), inplace=True)

            # save dataframe into csv database
            df_copy.to_csv(DB_FILENAME, index=False)

            # update dropdown to the last record after delete or set to None if list is empty
            if len(df_copy.index) > 0:
                current_selected_index = current_selected_index - 1

                # populate form with data of last existing record in db
                scenario_name = df_copy['scenario_name'][current_selected_index]
                total_hits = df_copy['total_hits'][current_selected_index]
                conversion_rate = df_copy['conversion_rate'][current_selected_index]
                revenue_per_purchase = df_copy['revenue_per_purchase'][current_selected_index]
                purchase_per_converted_user = df_copy['purchase_per_converted_user'][current_selected_index]
                sampling_cost = df_copy['sampling_cost'][current_selected_index]
                potential_revenue = df_copy['potential_revenue'][current_selected_index]
                form_data = [scenario_name,
                             total_hits,
                             conversion_rate,
                             revenue_per_purchase,
                             purchase_per_converted_user,
                             sampling_cost,
                             potential_revenue]
                
            else:
                current_selected_index = None

                # empty form data
                scenario_name = ''
                total_hits = ''
                conversion_rate = ''
                revenue_per_purchase = ''
                purchase_per_converted_user = ''
                sampling_cost = ''
                potential_revenue = ''
                form_data = []
                
        else:
            pass

    # edit checkbox clicked
    if triggered_id == 'mode':

        is_editing = not is_editing

    # scenario dropdown clicked. this will run also after a delete action
    if triggered_id == 'scenario':

        # assign global current selected index with currently selected option in dropdown
        current_selected_index = scenario_action_value

        # update field with current values
        try:
            scenario_name = df_copy['scenario_name'][scenario_action_value]
            total_hits = df_copy['total_hits'][scenario_action_value]
            conversion_rate = df_copy['conversion_rate'][scenario_action_value]
            revenue_per_purchase = df_copy['revenue_per_purchase'][scenario_action_value]
            purchase_per_converted_user = df_copy['purchase_per_converted_user'][scenario_action_value]
            sampling_cost = df_copy['sampling_cost'][scenario_action_value]
            potential_revenue = df_copy['potential_revenue'][scenario_action_value]
            form_data = [scenario_name,
                         total_hits,
                         conversion_rate,
                         revenue_per_purchase,
                         purchase_per_converted_user,
                         sampling_cost,
                         potential_revenue]

        # handle just in case no value in dropdown appears when clicking on an option
        except:
            # empty form data
            scenario_name = ''
            total_hits = ''
            conversion_rate = ''
            revenue_per_purchase = ''
            purchase_per_converted_user = ''
            sampling_cost = ''
            potential_revenue = ''
            form_data = []

    # when calculate ROI btn is clicked
    if triggered_id == 'submitButton':

        # COMPUTATION FOR CALCULATING ROI
        total_potential_ar = total_hits * revenue_per_purchase * purchase_per_converted_user
        unconverted_or = (1 - (conversion_rate / 100)) * total_potential_ar
        converted_rev = (conversion_rate / 100) * total_potential_ar
        net_profit = converted_rev - sampling_cost
        max_as = (potential_revenue / 100) * net_profit
        max_sh = max_as / total_hits

        net_profit_sampling = (1 - (potential_revenue / 100)) * net_profit

        # render pie chart
        labels = ['Net Profit Not For Sampling', 'Max Allowable Spend', 'Sampling Cost', 'Unconverted Revenue']
        values = [net_profit_sampling, max_as, sampling_cost, unconverted_or]

        donut_figure = go.Figure(go.Pie(labels=labels,
                                        values=values,
                                        hole=.4,
                                        marker_colors=['rgb(255,59,60)', 'rgb(134,169,189)', 'rgb(44,82,103)', 'rgb(242,217,187)'],
                                        textinfo='value+label',
                                        showlegend=False,
                                        textposition='outside'
                                ))

        # render waterfall chart
        labels = [
            'Total Potential Annual Revenue',
            'Unconverted Opportunity Revenue',
            'Converted Revenue',
            'Sampling Cost',
            'Net Profit',
            'Net Profit Not For Sampling',
            'Max Allowable Spend'
        ]
        values = [
            total_potential_ar,
            -unconverted_or,
            0, # converted_rev,
            -sampling_cost,
            0, # net_profit,
            -net_profit_sampling,
            0, # max_as
        ]
        waterfall_figure = go.Figure(go.Waterfall(
            name="20",
            orientation="v",
            measure=["absolute", "relative", "total", "relative", "total", "relative", "total"],
            x=labels,
            y=values,
            totals={"marker": {"color": "rgb(44,82,103)"}},
            decreasing={"marker": {"color": "rgb(255,59,60)"}}  
        ))
        
        waterfall_figure.update_xaxes(title_text = "ROI Parameters")
        
        

    # this will happen only at the start of the application
    if triggered_id is None:
        pass

    # update scenarios for dropdown
    scenarios = df_copy['scenario_name']
    new_scenarios = [{'label': value, 'value': index} for index, value in scenarios.items()]

    # format numbers to Php currency
    total_potential_ar = "Php {:,.2f}".format(total_potential_ar)
    unconverted_or = "Php {:,.2f}".format(unconverted_or)
    converted_rev = "Php {:,.2f}".format(converted_rev)
    max_as = "Php {:,.2f}".format(max_as)
    max_sh = "Php {:,.2f}".format(max_sh)
    net_profit = "Php {:,.2f}".format(net_profit)

    return new_scenarios, current_selected_index, scenario_name, total_hits, conversion_rate, revenue_per_purchase, \
           purchase_per_converted_user, sampling_cost, potential_revenue, total_potential_ar, \
           unconverted_or, converted_rev, max_as, max_sh, net_profit, donut_figure, waterfall_figure


if __name__ == '__main__':
    application.run(port=8080)
