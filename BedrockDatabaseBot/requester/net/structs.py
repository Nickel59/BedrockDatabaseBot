from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Cookie:
    encrypted_data: str
    expiration: str


@dataclass(frozen=True, slots=True)
class UpdateInfo:
    update_id: str
    package_moniker: str

    def __str__(self):
        return f'{self.update_id} {self.package_moniker}'


@dataclass(frozen=True, slots=True)
class SyncUpdates:
    new_updates: list[UpdateInfo]
    new_cookie: Cookie


@dataclass(frozen=True, slots=True)
class Config:
    last_change: str
