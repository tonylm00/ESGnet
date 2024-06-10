from Network.node import DataNode
from utils.connector import companies, links
from treelib import Tree
from treelib.exceptions import DuplicatedNodeIdError, NodeIDAbsentError


def create_nodes_by_company():
    collection = companies.find({})
    for document in collection:
        tree = Tree()
        tree.create_node(document['name'], document['name'], data=DataNode(name=document['name']))
        forest[document['name']] = tree


def create_nodes_by_links():
    collection = links.find({})
    for document in collection:
        try:

            if not document['home_name'] is forest.keys():
                tree = Tree()
                tree.create_node(document['home_name'], document['home_name'],
                                 data=DataNode(name=document['home_name']))
                forest[document['home_name']] = tree

            if not document['link_name'] is forest.keys():
                tree = Tree()
                tree.create_node(document['link_name'], document['link_name'],
                                 data=DataNode(name=document['link_name']))
                forest[document['link_name']] = tree

        except KeyError as e:
            print("There are few rows without home_name: ", e)


def populate():
    collection = links.find({})
    for document in collection:
        if document['home_name'] in forest.keys():
            try:
                if not forest[document['home_name']].contains(document['link_name']):
                    forest[document['home_name']].create_node(document['link_name'], document['link_name'],
                                                              parent=document['home_name'],
                                                              data=DataNode(name=document['link_name']))

                '''if not forest[document['link_name']].contains(document['home_name']):
                    forest[document['link_name']].create_node(document['home_name'], document['home_name'],
                                                              parent=document['link_name'])'''

            except DuplicatedNodeIdError as e:
                print(e)


if __name__ == '__main__':
    forest = {}
    # create_nodes_by_links()
    create_nodes_by_company()
    populate()


    tree = forest['Microsoft']
    print(tree.show(stdout=False))

    for frasca in tree.all_nodes_itr():
        try:
            frasca.data.print()
        except NodeIDAbsentError as e:
            print('something is happened: ', e)

