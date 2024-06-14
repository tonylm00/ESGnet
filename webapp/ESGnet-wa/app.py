import joblib
import networkx as nx
import pandas as pd
from flask import Flask, request, jsonify, render_template
from data_preparation.cleaning import flatten_dict, clean_decarbonization_target, merge_involvement, \
    drop_controversies_columns
from data_preparation.encoding import involvement_encoding, encoding_colors, encoding_aligned_no
from data_preparation.run import clean_with_metrics, merge_by_esg
from esg_service_value_network.model.model_svn_score import extract_features

app = Flask(__name__)


def load_model(path):
    try:
        return joblib.load(path)
    except FileNotFoundError:
        return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/data')
def from_data():
    return render_template('datacompany.html')


@app.route('/svn')
def from_svn():
    return render_template('svn.html')


def get_esg_value(company_name):
    df = pd.read_csv('../../data/label_with_metrics.csv')
    esg_value = df.loc[df['name'] == company_name, 'esg'].values
    if len(esg_value) > 0:
        return esg_value[0]
    else:
        return None


def construct_graph(companies, relationships):
    G = nx.Graph()
    G.add_node('TARGET')

    for i, company in enumerate(companies):
        esg_value = get_esg_value(company)
        G.add_node(company, esg=esg_value)
        rel_type = relationships[i] if i < len(relationships) else 'unknown'
        G.add_edge('TARGET', company, relationship=rel_type)

    print(f"Graph : {G}")

    return G


@app.route('/predict/svn', methods=['POST'])
def predict():
    data = request.get_json()
    companies = data.get('companies', [])
    relationships = data.get('relationships', [])

    if not companies or not relationships:
        return jsonify({'error': 'List of companies and relationships is required'}), 400

    graph = construct_graph(companies, relationships)
    features = extract_features(graph, 'TARGET')
    print(f"Features: {features}")

    model = load_model(path='../../esg_service_value_network/model/saved/svn_score.pkl')

    if not model:
        return jsonify({'error': 'Model not found'}), 500

    feature_names = ['num_links', 'mean_esg_neighbors', 'var_esg_neighbors', 'sum_esg_neighbors', 'sum_partnership',
                     'sum_customers', 'sum_investment', 'sum_competitor']

    X = [features[feature_name] for feature_name in feature_names]
    print(f"X: {X}")
    prediction = model.predict([X])[0]

    # Round the prediction to two decimal places
    prediction = round(prediction, 2)
    print(prediction)
    # Render the result template with the prediction
    return jsonify({'esg': prediction})


@app.route('/result')
def result():
    esg_value = request.args.get('esg')
    return render_template('result.html', esg=esg_value)


@app.route('/predict/data', methods=['POST'])
def predict_data():
    data = request.get_json()
    flattened_data = flatten_dict(data)

    df = pd.DataFrame({key: [value] for key, value in flattened_data.items()})

    column_mappings = {
        'Decarbonization_Target_target_year': 'Decarbonization_Target_target_year',
        'Decarbonization_Target_comprehensiveness': 'Decarbonization_Target_Comprehensiveness',
        'Decarbonization_Target_ambition_per_annum': 'Decarbonization_Target_Ambition p.a.',
        'Decarbonization_Target_temperature_goal': 'Temperature Goal',
    }
    df = df.rename(columns=column_mappings)

    # Perform necessary cleaning and transformations
    df = clean_decarbonization_target(df)
    df = merge_involvement(df)
    df = involvement_encoding(df)
    df = encoding_colors(df)
    df = encoding_aligned_no(df)
    df = merge_by_esg(df)

    model = load_model(path='../../esg_company_data/saved/data_score.pkl')

    if not model:
        return jsonify({'error': 'Model not found'}), 500

    desired_feature_order = ['employees', 'altman_score', 'piotroski_score',
                             'Decarbonization Target_Target Year',
                             'Decarbonization Target_Comprehensiveness',
                             'Decarbonization Target_Ambition p.a.', 'Temperature Goal',
                             'environmental_metric', 'social_metric', 'governance_metric',
                             'involvement_metric']

    df = df.reindex(columns=desired_feature_order)
    X = df.values

    prediction = model.predict(X)[0]
    prediction = round(prediction, 2)

    return jsonify({'esg': prediction})


if __name__ == '__main__':
    app.run(debug=True)
