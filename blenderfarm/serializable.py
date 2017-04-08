
import json

class Serializable:

    """A class which can be serialized and deserialized."""

    def unserialize(self, data):
        """Unserializes the data returned by the `serialize()` method."""

        pass

    def serialize(self): # pylint: disable=no-self-use
        """Returns a Python object; this object will eventually be passed to
`json.dumps()` so be sure to use serializable types only."""

        out = {}

        return out

    def serialize_json(self):
        """Returns the JSON string version of this `Node`."""
        return json.dumps(self.serialize())

    def unserialize_json(self, json_data):
        """Unpacks the `json_data` and sends it to the `unserialize()`
method. Inverse of the `serialize_json()` method."""

        self.unserialize(json.loads(json_data))
