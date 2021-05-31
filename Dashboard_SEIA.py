import pandas as pd
import plotly.express as px
import dash
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go


tabela = pd.DataFrame(pd.read_csv("C:/Users/aliss/Desktop/Codigos/WebScraping/prec.csv"))

#tabela2 = pd.DataFrame(tabela)

#municipio_options = [{'label':i, 'value':i} for i in tabela["Município"].unique()]

region_options = [{'label':i, 'value':i} for i in tabela["Região"].unique()]

date_options = [{ 'label': i, 'value': i} for i in tabela.columns[8:]]


app = dash.Dash(external_stylesheets=[dbc.themes.SOLAR])


#px.set_mapbox_access_token(open(".mapbox_token").read())

contagem_estacoes = tabela.groupby('Região')['Nome_Estação'].agg({'count'})
contagem_estacoes = pd.DataFrame(contagem_estacoes).reset_index()
contagem_total = contagem_estacoes['count'].sum()


app.layout = html.Div([ 
    html.H1('Precipitação Diária no Estado da Bahia - Maio/2021', style={ 'textAlign': 'center'}),
    html.P([
        html.A('SEIA Monitoramento',
        href = 'http://monitoramento.seia.ba.gov.br/',
        target = '_blank')], style={ 'textAlign': 'center'}),
    dbc.Row([
        dbc.Col(dcc.Graph(id='estacoes-graph'), width={"size": 5 ,"offset": 1}, md=4),
        dbc.Col([html.H5(id = 'dia_dados', style={ 'textAlign': 'center'}),
            html.H5('Quantidade Estações'),
            html.Div(id = 'tabela-contagem'),
            html.H6(id = 'total-estações')
        ], width="auto", style={ 'textAlign': 'center'}),
        dbc.Col(dcc.Graph(id ='density-graph'), width={"size": 5 ,"offset": 0}, md=4)
    ], justify="start"),
        html.H2('Grafico de precipitação por Região Climática', style={ 'textAlign': 'center'}),
    dbc.Row([
        dbc.Col([
            html.H5('Selecione o dia ou Total'),
            dcc.Dropdown(id = 'date_dropdown', options = date_options, value = date_options[-1]['value']),
            html.H1(' '),
            html.H5('Regiões Climáticas: '),
            dcc.Dropdown(id = 'regiao-dropdown', options = region_options, value= 'Recôncavo')
            ],width={"size": 1.5, "offset": 1}),
        dbc.Col(dcc.Graph(id = 'municipio-graph'), width={"size": 9 }),
    ], justify="start"),

    html.H2('Tabela de Dados de Precipitação(mm)', style={ 'textAlign': 'center'}),
    #dash_table.DataTable(
        #id='dados-info',
        #columns=[{'name': col, 'id': col} for col in tabela.columns]),
    dbc.Row([
        dbc.Col(html.Div(id ='dados-info1'), width={"size": 4, "offset": 0}),
        dbc.Col(html.Div(id ='dados-info2'), width={"size": 4, "offset": 0}),
        dbc.Col(html.Div(id ='dados-info3'), width={"size": 4, "offset": 0} )
        ], justify="center")
])


@app.callback(
    Output('tabela-contagem', 'children'),
    Output('total-estações', 'children'),
    Input('date_dropdown', 'value')
)

def update_contagem_table(select_date):
    contagem_estacoes = tabela.groupby('Região')[select_date].agg({'count'})
    contagem_estacoes = pd.DataFrame(contagem_estacoes).reset_index()
    contagem_total = contagem_estacoes['count'].sum()

    table1 = dbc.Table.from_dataframe(contagem_estacoes, striped=True, bordered=True, hover=True, size = 'sm')

    return table1, f'Total de estações: {str(contagem_total)}'


@app.callback(
    Output('municipio-graph', 'figure'),
    Output('dia_dados', 'children'),
    Input('regiao-dropdown', 'value'),
    Input('date_dropdown', 'value')
    
)

def update_graph (selected_regiao, selected_date):
    filtered_erro = tabela[tabela['Região']==selected_regiao]
    filtered_erro = filtered_erro[selected_date].sum()
    if filtered_erro == 0:
        filtered_tabela_erro = tabela[tabela['Região']==selected_regiao]
        bar_fig_erro = px.bar(x = (filtered_tabela_erro["Município"] + " - " + filtered_tabela_erro["Código"]), y = filtered_tabela_erro[selected_date])
        return bar_fig_erro, f'Precipitação {selected_date.replace("_","/")}'
    else:
        filtered_tabela = tabela[tabela['Região']==selected_regiao]
        filtered_tabela = filtered_tabela[filtered_tabela[selected_date] > 0]
        filtered_tabela = filtered_tabela.sort_values(selected_date, ascending=False)
        bar_fig = px.bar(x = (filtered_tabela["Município"] + " - " + filtered_tabela["Código"]), y = filtered_tabela[selected_date], hover_name=filtered_tabela['Nome_Estação'],text=list(filtered_tabela[selected_date]),
                    opacity=0.7, template= 'simple_white')
        bar_fig.layout.xaxis.title = 'Estações'
        bar_fig.layout.yaxis.title = 'Total de Precipitação(mm)'
        bar_fig.update_layout(
    margin=dict(l=50, r=50, t=30, b=30),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor='rgba(0,0,0,0)', font_color="gray",
)
        return bar_fig, f'Precipitação {selected_date.replace("_","/")}'

@app.callback(
    Output('dados-info1', 'children'),
    Output('dados-info2', 'children'),
    Output('dados-info3', 'children'),
    Input('regiao-dropdown', 'value'),
    Input('date_dropdown', 'value')
)

def update_table (selected_regiao, selected_date):
    filtered_tabela = tabela[tabela['Região']==selected_regiao]

    filtered_tabela = filtered_tabela[filtered_tabela[selected_date] > 0]
    filtered_tabela = filtered_tabela[['Estação',selected_date]]
    filtered_tabela = filtered_tabela.sort_values(selected_date, ascending=False)

    total_col = int(filtered_tabela['Estação'].count())
    cont = int(total_col/3)
    parte1 = filtered_tabela.iloc[:cont+1]
    parte2 = filtered_tabela.iloc[cont+1:(total_col - cont)]
    parte3 = filtered_tabela.iloc[(total_col - cont):]

    table1 = dbc.Table.from_dataframe(parte1, striped=True, bordered=True, hover=True, size = 'sm')
    table2 = dbc.Table.from_dataframe(parte2, striped=True, bordered=True, hover=True, size = 'sm')
    table3 = dbc.Table.from_dataframe(parte3, striped=True, bordered=True, hover=True, size = 'sm')

    return table1, table2, table3

@app.callback(
    Output('estacoes-graph', 'figure'),
    Output('density-graph', 'figure'),
    Input('date_dropdown', 'value')
)

def update_maps(date):

    table_map = tabela
    sequential1 = ['#e0fefc', '#befefe','#73f1fd', '#11d4ff','#21b5fb', '#3698fd', '#4975f9', '#5c56f4', '#4e37e7', '#4217d6', '#390cc7', '#3300b8']
    density = px.density_mapbox(table_map, lat="Latitude", lon="Longitude", z = date, radius=20 , zoom=5, height=400 ,color_continuous_scale= sequential1, range_color=[0,150], opacity=0.8)
    points = px.scatter_mapbox(table_map, lat="Latitude", lon="Longitude", zoom=5 ,color= date, text= 'Município', hover_name='Código', hover_data=["Município", "Nome_Estação"], height=400, color_continuous_scale=px.colors.diverging.Temps)

    figure_1 = go.Figure(data = points)
    figure_1.update_layout()
    figure_1.update_traces(marker_symbol="circle", marker_colorscale= 'Bluered', marker_size = 9)
    figure_1.update_layout(mapbox_style="open-street-map")
    figure_1.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor='rgba(0,0,0,0)', font_color="gray")

    figure_2 = go.Figure(data=density)
    figure_2.update_layout(mapbox_style="open-street-map")
    figure_2.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor='rgba(0,0,0,0)',font_color="gray")

    return figure_1, figure_2

if __name__ == '__main__':
    app.run_server(debug=True)