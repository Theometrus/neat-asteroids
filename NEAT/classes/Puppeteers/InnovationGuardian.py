class InnovationGuardian:
    """
    Responsible for keeping track of all unique nodes and connections,
    and assigning innovation numbers to them.
    Note: only keeps a record of innovations made in the current generation. As a result, it is possible for
    the same innovation to occur in a later generation and get assigned a different innovation number.
    This is intentional.
    """

    def __init__(self):
        self.conn_innov = 0
        self.node_innov = 0
        self.current_conn_innovations = {}  # Keys: tuples (from_node_innov, to_node_innov)
        self.current_node_innovations = {}  # Keys: tuples (from_node_innov, to_node_innov)

    def new_generation(self):
        self.current_node_innovations = {}
        self.current_conn_innovations = {}

    def register_node(self, from_innov, to_innov):
        if self.current_node_innovations.get((from_innov, to_innov)) is None:
            self.current_node_innovations[(from_innov, to_innov)] = self.node_innov
            self.node_innov += 1

        return self.current_node_innovations[(from_innov, to_innov)]

    def register_connection(self, from_innov, to_innov):
        if self.current_conn_innovations.get((from_innov, to_innov)) is None:
            self.current_conn_innovations[(from_innov, to_innov)] = self.conn_innov
            self.conn_innov += 1

        return self.current_conn_innovations[(from_innov, to_innov)]
