"""Implementation of the replaceitem command."""

from mcipc.rcon.proto import Client
from mcipc.rcon.proxy import CommandProxy
from mcipc.rcon.types import Vec3


__all__ = ['replaceitem']


class ReplaceitemProxy(CommandProxy):
    """Proxy for replaceitem related commands."""

    def block(self, pos: Vec3, slot: str, item: str, count: int = None) -> str:
        """Replaces a block."""
        self._run('block', pos, slot, item, count)

    def entity(self, targets: str, slot: str, item: str, count: int = None) -> str:
        """Replaces an entity."""
        self._run('entity', targets, slot, item, count)


def replaceitem(self: Client) -> ReplaceitemProxy:
    """Delegates to a command proxy."""

    return ReplaceitemProxy(self, 'replaceitem')
