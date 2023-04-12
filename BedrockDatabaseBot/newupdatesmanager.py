import json

from env import RELEASES_PATH, PREVIEWS_PATH
from requester import UpdateInfo

# Mojang seems to have stopped releasing betas for Windows.
# The last beta released is 1.19.34.0 released on May 19, 2022.
# For this reason we don't touch betas here.


def get_actual_new_updates(new_updates: list[UpdateInfo]) -> list[UpdateInfo]:
    existing_update_strings = _get_existing_update_strings()
    existing_update_string_list = existing_update_strings['release'] + existing_update_strings['preview']

    existing_update_info_list = [
        UpdateInfo(*existing_update_string.split()) for existing_update_string in existing_update_string_list
    ]

    return [new_update for new_update in new_updates if new_update not in existing_update_info_list]


def save_new_updates(new_updates: list[UpdateInfo]):
    existing_update_strings = _get_existing_update_strings()

    new_update_strings = _get_new_update_strings(new_updates)

    update_strings_to_save = {}
    for type_ in 'release', 'preview':
        update_strings_to_save[type_] = existing_update_strings[type_] + new_update_strings[type_]

    for type_, path in ('release', RELEASES_PATH), ('preview', PREVIEWS_PATH):
        with open(path, 'w') as f:
            json.dump(update_strings_to_save[type_], f, indent=4)


def get_commit_message(new_updates: list[UpdateInfo]) -> str:
    new_update_strings = _get_new_update_strings(new_updates)

    commit_message = ''
    for type_ in 'release', 'preview':
        if new_update_strings[type_]:
            version_name = new_update_strings[type_][0].removesuffix('__8wekyb3d8bbwe').split('_')[1]
            commit_message += f'{version_name} ({type_.capitalize()}) '
    return commit_message.rstrip()


def _get_new_update_strings(new_updates: list[UpdateInfo]) -> dict[str, list[str]]:
    new_update_strings = {}
    for type_, prefix in ('release', 'Microsoft.MinecraftUWP_'), ('preview', 'Microsoft.MinecraftWindowsBeta_'):
        new_update_strings[type_] = [
            str(update_info) for update_info in new_updates if update_info.package_moniker.startswith(prefix)
        ]
    return new_update_strings


def _get_existing_update_strings() -> dict[str, list[str]]:
    existing_update_strings = {}
    for type_, path in ('release', RELEASES_PATH), ('preview', PREVIEWS_PATH):
        with open(path) as f:
            existing_update_strings[type_] = json.load(f)
    return existing_update_strings
