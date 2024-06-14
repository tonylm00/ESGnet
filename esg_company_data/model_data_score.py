import joblib
from sklearn.ensemble import RandomForestRegressor
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold
from data_preparation.balancing import balancing_kmeans

path = 'saved/data_score.pkl'


def train_save_model(path):
    df = pd.read_csv('../data/label_with_metrics.csv').drop(columns=['ticker', 'name'])
    X, y = balancing_kmeans(df, n_cluster=10)

    print(X.columns)

    model = RandomForestRegressor(
        max_depth=20,
        max_features='sqrt',
        min_samples_leaf=1,
        min_samples_split=2,
        n_estimators=300,
        random_state=42
    )

    kf = KFold(n_splits=10, shuffle=True, random_state=42)

    mae_scores = []
    mse_scores = []
    r2_scores = []

    for train_index, test_index in kf.split(X):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]

        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        mae_scores.append(mae)
        mse_scores.append(mse)
        r2_scores.append(r2)

    avg_mae = sum(mae_scores) / len(mae_scores)
    avg_mse = sum(mse_scores) / len(mse_scores)
    avg_r2 = sum(r2_scores) / len(r2_scores)

    print(f"MAE: {avg_mae}")
    print(f"MSE: {avg_mse}")
    print(f"R²: {avg_r2}")

    joblib.dump(model, path)


if __name__ == '__main__':
    train_save_model(path)
