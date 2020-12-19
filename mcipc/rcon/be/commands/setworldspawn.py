"""Implementation of the setworldspawn command."""

from mcipc.rcon.proto import Client
from mcipc.rcon.types import Vec3


__all__ = ['setworldspawn']


def setworldspawn(self: Client, position: Vec3 = None) -> str:
    """Sets the world spawn."""

    return self.run('setworldspawn', position)
