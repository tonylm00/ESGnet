from sklearn.cluster import KMeans
import pandas as pd
import smogn


def balancing_kmeans(df):
    X = df.drop(columns=['esg'])
    y = df['esg']

    kmeans = KMeans(n_clusters=10, random_state=42)
    clusters = kmeans.fit_predict(y.values.reshape(-1, 1))

    X['cluster'] = clusters
    data_balanced = pd.concat([X, y], axis=1)

    max_size = data_balanced['cluster'].value_counts().max()
    lst = [data_balanced]

    for cluster in data_balanced['cluster'].unique():
        df_cluster = data_balanced[data_balanced['cluster'] == cluster]
        lst.append(df_cluster.sample(max_size - len(df_cluster), replace=True))

    data_balanced = pd.concat(lst)
    data_balanced.drop(columns=['cluster'], inplace=True)

    X_balanced = data_balanced.drop(columns=['esg'])
    y_balanced = data_balanced['esg']

    return X_balanced, y_balanced


def balancing_smogn(df):
    esg_smogn = smogn.smoter(
        data=df.dropna(),
        y='esg',
        k=20,  # positive integer (k < n)
        pert=0.04,  # real number (0 < R < 1)
        samp_method='extreme',  # string ('balance' or 'extreme')
        replace=False,  # boolean (True or False)

        # phi relevance arguments
        rel_thres=0.10,  # real number (0 < R < 1)
        rel_method='auto',  # string ('auto' or 'manual')
        rel_xtrm_type='both',  # unused (rel_method = 'manual')
        rel_coef=1.50,  # unused (rel_method = 'manual')
    )
    X_balanced = esg_smogn.drop(columns=['esg'])
    y_balanced = esg_smogn['esg']

    return X_balanced, y_balanced
