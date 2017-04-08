"""Render nodes."""

from . import serializable

class Node(serializable.Serializable):

    """Describes a single render node. Nodes are unique for every machine/user/key combination."""

    def __init__(self):
        self.node_id = None


    def unserialize(self, data):
        super().unserialize(data)

        self.node_id = data['node_id']

        return self

    def serialize(self):
        out = super().serialize()

        out['node_id'] = self.node_id

        return out
