import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.utils import resample
from esg_service_value_network.model.model_svn_score import extract_features, create_graph
from data_preparation.balancing import balancing_kmeans

model_path = 'saved/svn_range.pkl'


def predict_esg_with_confidence(G, company_name, model, feature_names, n_bootstrap=1000, alpha=0.05):
    features = extract_features(G, company_name)
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

    # return esg_company_data.predict(feature_values)[0], lower_bound, upper_bound
    return lower_bound, upper_bound


if __name__ == '__main__':

    companies_df = pd.read_csv('../../data/label_with_metrics.csv')
    links_df = pd.read_csv('../../data/filtered_links.csv')

    G = create_graph(companies_df, links_df)

    features = []
    print("Graph:", G)
    for node in G.nodes:
        feature = extract_features(G, node)
        feature['name'] = node
        feature['esg'] = G.nodes[node]['esg']
        features.append(feature)

    features_df = pd.DataFrame(features)
    feature_names = ['num_links', 'mean_esg_neighbors', 'var_esg_neighbors', 'sum_esg_neighbors', 'sum_partnership',
                     'sum_customers', 'sum_investment', 'sum_competitor']

    X, y = balancing_kmeans(features_df[feature_names + ['esg']], n_cluster=12)
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

    joblib.dump(model, model_path)
    print("Model saved successfully!")

    '''    
    company_name = 'IBM'
    # predicted_esg, lower_bound, upper_bound = predict_esg_with_confidence(G, company_name, esg_company_data, feature_names)
    lower_bound, upper_bound = predict_esg_with_confidence(G, company_name, model, feature_names)
    # print(f"Predicted ESG for {company_name}: {predicted_esg}")
    print(f"95% Confidence Interval for {company_name}: ({lower_bound}, {upper_bound})")
    '''
