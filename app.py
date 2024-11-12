import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import requests
import base64
from PIL import Image
import webbrowser

app = dash.Dash(__name__)

## Foncton pour charger les IDs des clients depuis l'API Flask
def get_client_ids():
    response = requests.get('https://api-banque-ebcad8aeb750.herokuapp.com/clients')
    if response.status_code == 200:     # cela signifie que la requête a été exécutée avec succès.
        return response.json()
    else:
        return []
    
client_ids = get_client_ids()

## Créer l' interface graphique (layout) Tableau de bord
app.layout = html.Div([            
    # crée un titre de niveau 1 (H1) ou en tête                                        
    html.H1('BIENVENUE A LA SOCIETE FINANCIERE', style={'textAlign': 'center', 'color': 'pink'}),
    html.Br(),

    dcc.Tabs([
        dcc.Tab(label='PREDICTION ELIGIBILTE', children=[
            html.Div([
                html.H2('Les informations sur le client:'),
                # Crée un composant de menu déroulant (Dropdown) 
                dcc.Dropdown(                                           
                    id='client_id',              
                    options=[{'label': str(client_id), 'value': client_id} for client_id in client_ids],
                    placeholder='Sélectionnez un ID de client',
                    style={'width': '400px', 'height': '40px'}),
                    # Crée un conteneur div avec l'attribut id défini comme "client-info"
                    html.Div(id='client-info', style={'margin-top': '20px'}),
                html.Br(),
                html.H2("Les resultats de prediction d'éligibilité"),
                html.Button('Prédiction', id='predict-button', n_clicks=0, style={'width': '200px', 'height': '40px'}),
                # Afficher le resultat de la prédiction
                html.Div(id='client-prediction', style={'margin-top': '20px'}),
                html.Hr(),
                html.H2('Le graphique de Interpretation locale:'),
                html.Button('Interpretation locale', id='inter-loc', n_clicks=0, style={'width': '200px', 'height': '40px'}),
                # Afficher l'image de l'interpretation locale
                html.Div(id='local-graph', style={'margin-top': '20px'})
            ])
        ]),

        dcc.Tab(label='INTERPRETATION DES RESULTATS', children=[
            html.Div([
                html.H2('Le graphique de Interpretation Globale:',style={'margin-top': '20px'}),
                html.Button('Interpretation Globale', id='inter-glob', n_clicks=0, style={'width': '200px', 'height': '40px'}), 
                # Afficher l'image de l'interpretation globale
                html.Div(id='global-graph', style={'margin-top': '20px'})
            ])
        ]),

        dcc.Tab(label='ANALYSE DE DRIFT', children=[
            html.Div([
                html.H2("L'analyse de drift:", style={'margin-top': '20px'}),
                html.Button('Drift', id='drift-button', n_clicks=0, style={'width': '200px', 'height': '40px'}),
                html.Div(id='drift-analysis', style={'margin-top': '20px'})
            ])
        ]),
    ])
])   
   

## Récupérer les informations du client en fonction de son ID
@app.callback(
    # la valeur de retour du callback sera assignée au conteneur 'client-info'    
    Output('client-info', 'children'),
    # le callback sera déclenchée par les changements de valeur dans le menu déroulant                          
    Input('client_id', 'value')                        
)
def update_client_info(client_id):
    if client_id is not None:
        response = requests.get(f'https://api-banque-ebcad8aeb750.herokuapp.com/client/{client_id}')
        if response.status_code == 200:
            client_info = response.json()[0]
            return html.Div([
                html.H3(f"Informations du Client : {client_id}", style={'textAlign': 'center'}),
                html.Div([
                    html.Div([
                        html.Ul([
                            html.Li(f"Nom du contrat : {client_info.get('NAME_CONTRACT_TYPE', 'N/A')}"),
                            html.Li(f"Genre : {client_info.get('CODE_GENDER', 'N/A')}"),
                            html.Li(f"Date de naissance : {client_info.get('DAYS_BIRTH', 'N/A')}"),
                            html.Li(f"Nombre d'enfants : {client_info.get('CNT_CHILDREN', 'N/A')}")
                        ])
                    ], style={'flex': '1', 'marginRight': '10px'}),
                    html.Div([
                        html.Ul([
                            html.Li(f"Membre de famille : {client_info.get('CNT_FAM_MEMBERS', 'N/A')}"),
                            html.Li(f"Voiture : {client_info.get('FLAG_OWN_CAR', 'N/A')}"),
                            html.Li(f"Immobilier : {client_info.get('FLAG_OWN_REALTY', 'N/A')}"),
                            html.Li(f"Population de la région : {client_info.get('REGION_POPULATION_RELATIVE', 'N/A')}")
                        ])
                    ], style={'flex': '1', 'marginRight': '10px'}),
                    html.Div([
                        html.Ul([
                            html.Li(f"Revenu Total : {client_info.get('AMT_INCOME_TOTAL', 'N/A')}"),
                            html.Li(f"Annuité : {client_info.get('AMT_ANNUITY', 'N/A')}"),
                            html.Li(f"Prix du Bien : {client_info.get('AMT_GOODS_PRICE', 'N/A')}"),
                            html.Li(f"Crédit : {client_info.get('AMT_CREDIT', 'N/A')}")
                        ])
                    ], style={'flex': '1'})
                ], style={'display': 'flex', 'flexWrap': 'wrap'}),
            ])
        else:
            return html.Div([
                html.H3(f"Aucun client trouvé avec l'ID: {client_id}")
            ])
    return None

 

## Mise à jour de la prédiction en fonction de son ID
@app.callback(
    Output('client-prediction', 'children'),
    Input('client_id', 'value'),                  
    Input('predict-button', 'n_clicks')      
)
def update_client_predict(client_id, n_clicks):
    if client_id and n_clicks > 0:
        response = requests.get(f'https://api-banque-ebcad8aeb750.herokuapp.com/predict/{client_id}')
        if response.status_code == 200:
            client_predict = response.json()
            # Vérification de la probabilité et génération de la réponse
            if client_predict <= 50:
                message = "Vous n'êtes pas éligible au prêt"
            else:
                message = "Bravo ! Vous êtes éligible au prêt"
            return html.Div([
                html.P(f"La probabilité du client {client_id} à rembourser son crédit est de: {client_predict} %"),
                html.P(html.Strong(message))
            ])
        else:
            return html.Div([
                html.P(f"Aucun client trouvé avec l'ID: {client_id}")
            ])
    return None


## Interpretation Locale du modèle
@app.callback(
    Output('local-graph', 'children'),
    Input('client_id', 'value'), 
    Input('inter-loc', 'n_clicks')
)
def update_local_interpretation(client_id, n_clicks):
    if n_clicks > 0 :
        # Ouvre le graphique
       return dcc.Location(href=f'https://api-banque-ebcad8aeb750.herokuapp.com/interpretation/local/{client_id}', id='inter-loc')   
    return dash.no_update


## Interpretation Globale du modèle
# Fonction pour charger l'image depuis l'API
def load_image_globale():
    response = requests.get('https://api-banque-ebcad8aeb750.herokuapp.com/interpretation/global')
    if response.status_code == 200:
        return 'data:image/png;base64,' + base64.b64encode(response.content).decode('utf-8')
    return None

@app.callback(
    Output('global-graph', 'children'),
    Input('inter-glob', 'n_clicks')
)
def update_global_interpretation(n_clicks):
    if n_clicks > 0:
       img_src = load_image_globale()
       if img_src:
            return html.Img(src=img_src, style={'width': '100%', 'height': 'auto'})
       return "Erreur lors de la génération du graphique."
    return ""  
   

## Analyse drift des données
@app.callback(
    Output('drift-analysis', 'children'),
    Input('drift-button', 'n_clicks')
)
def analysis_drift(n_clicks):
    if n_clicks > 0:
        # Ouvre l'URL dans un nouvel onglet
        return html.A('Ouvrir l\'analyse de drift dans un nouveau onglet', href='https://api-banque-ebcad8aeb750.herokuapp.com/drift', target="_blank")
    return dash.no_update

# Expose the server variable for Gunicorn
server = app.server

if __name__ == '__main__':
    app.run_server(debug=False)
