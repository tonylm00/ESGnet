import networkx as nx
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib
from data_preparation.balancing import balancing_kmeans

'''
def extract_features(graph, company_name):
    neighbors = list(graph.neighbors(company_name))
    if not neighbors:
        return {
            'num_links': 0,
            'mean_esg_neighbors': 0,
            'var_esg_neighbors': 0,
            'sum_esg_neighbors': 0,
            'sum_partnership': 0,
            'sum_customers': 0,
            'sum_investment': 0,
            'sum_competitor': 0,
        }

    esg_scores = [graph.nodes[neighbor]['esg'] for neighbor in neighbors]
    num_links = len(neighbors)
    mean_esg_neighbors = sum(esg_scores) / num_links
    var_esg_neighbors = np.var(esg_scores)
    sum_esg_neighbors = sum(esg_scores)

    sum_partnership = sum(1 for neighbor in neighbors if graph[company_name][neighbor]['relationship'] == 'partnership')
    sum_customers = sum(1 for neighbor in neighbors if graph[company_name][neighbor]['relationship'] == 'customer')
    sum_investment = sum(1 for neighbor in neighbors if graph[company_name][neighbor]['relationship'] == 'investment')
    sum_competitor = sum(1 for neighbor in neighbors if graph[company_name][neighbor]['relationship'] == 'competitor')

    return {
        'num_links': num_links,
        'mean_esg_neighbors': mean_esg_neighbors,
        'var_esg_neighbors': var_esg_neighbors,
        'sum_esg_neighbors': sum_esg_neighbors,
        'sum_partnership': sum_partnership,
        'sum_customers': sum_customers,
        'sum_investment': sum_investment,
        'sum_competitor': sum_competitor,
    }
'''


def extract_features(graph, company_name):
    neighbors = list(graph.neighbors(company_name))
    if not neighbors:
        return {
            'num_links': 0,
            'mean_esg_neighbors': 0,
            'var_esg_neighbors': 0,
            'sum_esg_neighbors': 0,
            'sum_partnership': 0,
            'sum_customers': 0,
            'sum_investment': 0,
            'sum_competitor': 0,
        }

    esg_scores = [graph.nodes[neighbor].get('esg') for neighbor in neighbors if
                  graph.nodes[neighbor].get('esg') is not None]
    num_links = len(neighbors)

    if not esg_scores:
        # Se non ci sono punteggi ESG validi nei vicini, restituisci valori predefiniti
        return {
            'num_links': num_links,
            'mean_esg_neighbors': 0,
            'var_esg_neighbors': 0,
            'sum_esg_neighbors': 0,
            'sum_partnership': sum(
                1 for neighbor in neighbors if graph[company_name][neighbor]['relationship'] == 'partnership'),
            'sum_customers': sum(
                1 for neighbor in neighbors if graph[company_name][neighbor]['relationship'] == 'customer'),
            'sum_investment': sum(
                1 for neighbor in neighbors if graph[company_name][neighbor]['relationship'] == 'investment'),
            'sum_competitor': sum(
                1 for neighbor in neighbors if graph[company_name][neighbor]['relationship'] == 'competitor'),
        }

    mean_esg_neighbors = sum(esg_scores) / len(esg_scores)
    var_esg_neighbors = np.var(esg_scores)
    sum_esg_neighbors = sum(esg_scores)

    sum_partnership = sum(1 for neighbor in neighbors if graph[company_name][neighbor]['relationship'] == 'partnership')
    sum_customers = sum(1 for neighbor in neighbors if graph[company_name][neighbor]['relationship'] == 'customer')
    sum_investment = sum(1 for neighbor in neighbors if graph[company_name][neighbor]['relationship'] == 'investment')
    sum_competitor = sum(1 for neighbor in neighbors if graph[company_name][neighbor]['relationship'] == 'competitor')

    return {
        'num_links': num_links,
        'mean_esg_neighbors': mean_esg_neighbors,
        'var_esg_neighbors': var_esg_neighbors,
        'sum_esg_neighbors': sum_esg_neighbors,
        'sum_partnership': sum_partnership,
        'sum_customers': sum_customers,
        'sum_investment': sum_investment,
        'sum_competitor': sum_competitor,
    }


if __name__ == '__main__':
    companies_df = pd.read_csv('../data/label_with_metrics.csv')
    links_df = pd.read_csv('../data/filtered_links.csv')

    G = nx.Graph()

    for _, row in companies_df.iterrows():
        G.add_node(row['name'], esg=row['esg'])

    for _, row in links_df.iterrows():
        if row['home_name'] in G and row['link_name'] in G:
            G.add_edge(row['home_name'], row['link_name'], relationship=row['type'])

    features = []
    for node in G.nodes:
        feature = extract_features(G, node)
        feature['name'] = node
        feature['esg'] = G.nodes[node]['esg']
        features.append(feature)

    features_df = pd.DataFrame(features)
    feature_names = ['num_links', 'mean_esg_neighbors', 'var_esg_neighbors', 'sum_esg_neighbors', 'sum_partnership',
                     'sum_customers', 'sum_investment', 'sum_competitor']

    X, y = balancing_kmeans(features_df[feature_names + ['esg']])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    joblib.dump(model, 'svn_model.pkl')
    print("Model saved successfully!")
