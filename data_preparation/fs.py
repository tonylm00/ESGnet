import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from itertools import combinations

if __name__ == '__main__':

    df = pd.read_csv('../data/by_esg.csv', low_memory=False)
    X = df.drop(columns=['esg'])
    y = df['esg']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)

    results = []

    for k in range(2, X.shape[1] + 1):
        for combo in combinations(X.columns, k):
            X_train_combo = X_train[list(combo)]
            X_test_combo = X_test[list(combo)]

            model.fit(X_train_combo, y_train)
            y_pred = model.predict(X_test_combo)

            r2 = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)

            results.append({
                'n_features': k,
                'features': combo,
                'r2': r2,
                'mae': mae,
                'mse': mse
            })

            print(f"Number of features: {k}")
            print(f"Features: {combo}")
            print(f"R²: {r2}")
            print(f"MAE: {mae}")
            print(f"MSE: {mse}")
            print('-' * 40)

    results_df = pd.DataFrame(results)
    print(results_df)

    results_df.to_csv('feature_selection_results.csv', index=False)
