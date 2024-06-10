import networkx as nx
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.utils import resample
from data_preparation.balancing import balancing_kmeans


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


def predict_esg_with_confidence(company_name, model, feature_names, n_bootstrap=1000, alpha=0.05):
    features = extract_features(company_name)
    feature_values = pd.DataFrame([features], columns=feature_names)

    # Bootstrap
    predictions = []
    for _ in range(n_bootstrap):
        sample_indices = resample(range(len(X_train)), replace=True)
        X_sample = X_train.iloc[sample_indices]
        y_sample = y_train.iloc[sample_indices]

        model_sample = RandomForestRegressor(n_estimators=100, random_state=42)
        model_sample.fit(X_sample, y_sample)

        predictions.append(model_sample.predict(feature_values)[0])

    lower_bound = np.percentile(predictions, 100 * alpha / 2)
    upper_bound = np.percentile(predictions, 100 * (1 - alpha / 2))

    return model.predict(feature_values)[0], lower_bound, upper_bound


if __name__ == '__main__':

    companies_df = pd.read_csv('../data/label_with_metrics.csv')
    links_df = pd.read_csv('../data/filtered_links.csv')

    G = nx.Graph()

    # Aggiungi nodi con attributi ESG
    for _, row in companies_df.iterrows():
        G.add_node(row['name'], esg=row['esg'])

    # Aggiungi archi con attributi dai link filtrati
    for _, row in links_df.iterrows():
        if row['home_name'] in G and row['link_name'] in G:
            G.add_edge(row['home_name'], row['link_name'], relationship=row['type'])

    features = []
    print(G.graph)
    for node in G.nodes:
        feature = extract_features(G, node)
        feature['name'] = node
        feature['esg'] = G.nodes[node]['esg']
        features.append(feature)

    features_df = pd.DataFrame(features)
    print(features_df.head())
    feature_names = ['num_links', 'mean_esg_neighbors', 'var_esg_neighbors', 'sum_esg_neighbors', 'sum_partnership',
                     'sum_customers', 'sum_investment', 'sum_competitor']

    X, y = balancing_kmeans(features_df[feature_names + ['esg']])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    print(f"MSE: {mse}")
    print(f"MAE: {mae}")
    print(f"RMSE: {rmse}")
    print(f"R²: {r2}")

    print('---------------------')
    company_name = 'Apple'
    predicted_esg, lower_bound, upper_bound = predict_esg_with_confidence(company_name, model)
    print(f"Predicted ESG for {company_name}: {predicted_esg}")
    print(f"95% Confidence Interval for {company_name}: ({lower_bound}, {upper_bound})")
