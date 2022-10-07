from pyvis.network import Network

from etherscan import get_dataset_for_graph, WALLET_ADDRESS


def create_network_graph() -> None:
    net = Network(height='1080px',
                  width='100%',
                  bgcolor='white',
                  font_color='black')

    dataset = get_dataset_for_graph(WALLET_ADDRESS)
    wallets = dataset['nodes']
    edges_lst = dataset['edges']['final_edges']
    edges_full = dataset['edges']

    nodes_current_wallet = wallets['current_address']
    nodes_in = wallets['in']
    nodes_out = wallets['out']

    labels_current_wallet = wallets['current_address']
    labels_in = wallets['in']
    labels_out = wallets['out']

    colors_current_wallet = 'green'
    colors_in = ['lightblue', 'lightblue', 'lightblue', 'lightblue', 'lightblue', 'lightblue', 'lightblue']
    colors_out = ['blue', 'blue', 'blue']

    title_in = ['', '', '', '', '', '', '']
    title_out = ['', '', '']

    net.add_node(nodes_current_wallet, label=labels_current_wallet, color=colors_current_wallet, title='')
    net.add_nodes(nodes_in, label=labels_in, color=colors_in, title=title_in)
    net.add_nodes(nodes_out, label=labels_out, color=colors_out, title=title_out)

    net.repulsion(node_distance=120, spring_length=240)
    net.add_edges(edges_lst)

    for node in net.nodes:
        for item in edges_full.items():
            if isinstance(item[0], int):
                if item[1].get('from', '') == node.get('id', ''):
                    node['title'] += f"[{item[1].get('block_number', '')}]: {item[1].get('date', '')} | IN\n" \
                                     f"Source: {item[1].get('from', '')}\nTarget: {item[1].get('to', '')}\n" \
                                     f"{item[1].get('coin_name', '')}: {item[1].get('value', '')} | USD: {item[1].get('value_usd', '')}$\n" \
                                     f"Gas: {item[1].get('gas', '')} GWEI\nDate rate: {item[1].get('exch_rate', '')}$" \
                                     f"\n{'-' * 25}\n"
                elif item[1].get('to', '') == node.get('id', '') and item[1].get('to', '') != WALLET_ADDRESS:
                    node['title'] += f"[{item[1].get('block_number', '')}]: {item[1].get('date', '')} | OUT\n" \
                                     f"Source: {item[1].get('from', '')}\nTarget: {item[1].get('to', '')}\n" \
                                     f"{item[1].get('coin_name', '')}: {item[1].get('value', '')} | USD: {item[1].get('value_usd', '')}$\n" \
                                     f"Gas: {item[1].get('gas', '')} GWEI\nDate rate: {item[1].get('exch_rate', '')}$" \
                                     f"\n{'-' * 75}\n"

    # net.show_buttons()
    net.show('nodes.html')


create_network_graph()
