import pathlib

import attr
import toml


@attr.s
class Config:
    secret_key = attr.ib()
    db = attr.ib()

    @classmethod
    def from_toml(cls, path):
        path = pathlib.Path(path)
        with path.open(mode="rt") as fd:
            config = toml.loads(fd)

        return cls(config["app"]["secret-key"], config["db"])
