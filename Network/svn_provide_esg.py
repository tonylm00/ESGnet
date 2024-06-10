import networkx as nx
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split


# Definisci una funzione per estrarre le feature dai link con tipi di relazione
def extract_features(graph, company_name):
    neighbors = list(graph.neighbors(company_name))
    if not neighbors:
        return {
            'num_links': 0,
            'mean_esg_neighbors': 0,
            'var_esg_neighbors': 0,
            'sum_esg_neighbors': 0,
            'num_rel_type_1': 0,
            'num_rel_type_2': 0,
            # aggiungi altri tipi di relazione se necessario
        }

    esg_scores = [graph.nodes[neighbor]['esg'] for neighbor in neighbors]
    num_links = len(neighbors)
    mean_esg_neighbors = sum(esg_scores) / num_links
    var_esg_neighbors = np.var(esg_scores)
    sum_esg_neighbors = sum(esg_scores)

    # Conta i tipi di relazione
    num_rel_type_1 = sum(1 for neighbor in neighbors if graph[company_name][neighbor]['relationship'] == 'partnership')
    num_rel_type_2 = sum(1 for neighbor in neighbors if graph[company_name][neighbor]['relationship'] == 'customer')
    num_rel_type_3 = sum(1 for neighbor in neighbors if graph[company_name][neighbor]['relationship'] == 'investment')
    num_rel_type_4 = sum(1 for neighbor in neighbors if graph[company_name][neighbor]['relationship'] == 'competitor')

    # aggiungi altri tipi di relazione se necessario
    return {
        'num_links': num_links,
        'mean_esg_neighbors': mean_esg_neighbors,
        'var_esg_neighbors': var_esg_neighbors,
        'sum_esg_neighbors': sum_esg_neighbors,
        'num_rel_type_1': num_rel_type_1,
        'num_rel_type_2': num_rel_type_2,
        'num_rel_type_3': num_rel_type_3,
        'num_rel_type_4': num_rel_type_4,
    }


# Funzione per predire l'ESG
def predict_esg(company_name):
    if company_name in G:
        features = extract_features(G, company_name)
        feature_values = [[features[f] for f in feature_names]]
        predicted_esg = model.predict(feature_values)
        return predicted_esg[0]
    else:
        return None


# Carica i dataset
companies_df = pd.read_csv('../data/label_with_metrics.csv')
links_df = pd.read_csv('../data/filtered_links.csv')

# Crea un grafo vuoto
G = nx.Graph()

# Aggiungi nodi con attributi ESG
for _, row in companies_df.iterrows():
    G.add_node(row['name'], esg=row['esg'])

# Aggiungi archi con attributi dai link filtrati
for _, row in links_df.iterrows():
    if row['home_name'] in G and row['link_name'] in G:
        G.add_edge(row['home_name'], row['link_name'], relationship=row['type'])

# Estrai le feature per ogni azienda
features = []
for node in G.nodes:
    feature = extract_features(G, node)
    feature['company_name'] = node
    feature['esg'] = G.nodes[node]['esg']
    features.append(feature)

# Converti le feature in un DataFrame
features_df = pd.DataFrame(features)
features_df.to_csv('features.csv', index=False)

# Definisci le feature e il target
feature_names = ['num_links', 'mean_esg_neighbors', 'var_esg_neighbors', 'sum_esg_neighbors', 'num_rel_type_1',
                 'num_rel_type_2', 'num_rel_type_3', 'num_rel_type_4']
X = features_df[feature_names]
y = features_df['esg']

# Dividi i dati in training set e test set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Crea e allena un modello più complesso (Random Forest)
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predici sui dati di test
y_pred = model.predict(X_test)

# Valuta il modello con diverse metriche
mse = mean_squared_error(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print(f"Mean Squared Error (MSE): {mse}")
print(f"Mean Absolute Error (MAE): {mae}")
print(f"Root Mean Squared Error (RMSE): {rmse}")
print(f"R² Score: {r2}")
