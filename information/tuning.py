from sklearn.model_selection import KFold, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler
from sklearn.ensemble import RandomForestRegressor


def tune_random_forest_params(X, y):
    # Define the parameter grid for the saved
    param_grid = {
        'scaler': [StandardScaler(), RobustScaler(), MinMaxScaler()],
        'model__n_estimators': [50, 100, 200, 300],
        'model__max_features': ['sqrt', 'log2'],
        'model__max_depth': [5, 10, 20, 30],
        'model__min_samples_split': [2, 5, 10],
        'model__min_samples_leaf': [1, 2, 4]
    }

    # Initialize the saved
    model = RandomForestRegressor(random_state=42)

    # Define the number of folds
    k_folds = 10

    # Split the dataset using K-fold cross-validation
    kf = KFold(n_splits=k_folds, shuffle=True, random_state=42)

    # Define the pipeline with scaler and saved
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('saved', model)
    ])

    # Perform grid search with cross-validation for the pipeline
    grid_search = GridSearchCV(estimator=pipeline, param_grid=param_grid, cv=kf, n_jobs=-1)
    grid_search.fit(X, y)

    # Get the best parameters
    best_params = grid_search.best_params_

    return best_params
