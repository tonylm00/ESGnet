import joblib
import networkx as nx
import pandas as pd
from flask import Flask, request, jsonify, render_template

from Network.train_save_model import extract_features

app = Flask(__name__)


def load_model():
    try:
        return joblib.load('../../Network/svn_model.pkl')
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

    model = load_model()

    if not model:
        return jsonify({'error': 'Model not found'}), 500

    feature_names = ['num_links', 'mean_esg_neighbors', 'var_esg_neighbors', 'sum_esg_neighbors', 'sum_partnership',
                     'sum_customers', 'sum_investment', 'sum_competitor']

    X = [features[feature_name] for feature_name in feature_names]
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


if __name__ == '__main__':
    app.run(debug=True)
