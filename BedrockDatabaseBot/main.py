from typing import TypedDict
import json
import os
import logging
from logging.handlers import TimedRotatingFileHandler
import time

from env import RELEASES_PATH, BETAS_PATH, PREVIEWS_PATH, VERSIONS_PATH
import requester
from database import Database
import dbparser
from remoterepomanager import RemoteRepositoryManager


repo_manager = RemoteRepositoryManager()


def setup_timed_rotating_logger(log_path: str = 'logs', base_filename: str = 'bdb'):
    def namer(name: str) -> str:
        parent_dir_path, filename = os.path.split(name)
        filename = (filename.replace('.log', '') + '.log').lstrip('.')
        return os.path.join(parent_dir_path, filename)

    os.makedirs(log_path, exist_ok=True)

    log_filename = os.path.join(log_path, base_filename + '.log')

    handler = TimedRotatingFileHandler(log_filename, when="midnight", backupCount=30)
    handler.setLevel(logging.DEBUG)
    handler.suffix = "%Y-%m-%d"
    handler.namer = namer

    logging.basicConfig(
        handlers=[handler, logging.StreamHandler()],
        format='%(asctime)s | %(threadName)-10s | %(levelname)-5s | %(name)-22s | %(lineno)06d | %(message)s',
        level=logging.DEBUG
    )
    logging.getLogger('github.Requester').setLevel(logging.WARNING)


def main():
    setup_timed_rotating_logger()

    logging.info('--------------------START--------------------')

    number_of_cycles = 3
    for i in range(number_of_cycles):
        try:
            run_one_cycle()
        except Exception as e:
            logging.error(str(e))
        if i < number_of_cycles - 1:
            logging.info('Sleeping...')
            time.sleep(600)
            logging.info('Sleep ended.\n')

    logging.info('---------------------END---------------------')


def run_one_cycle():
    new_updates = requester.run()
    new_update_strings = get_new_update_strings(new_updates)

    db = Database(
        json.loads(repo_manager.get_text(RELEASES_PATH)),
        json.loads(repo_manager.get_text(BETAS_PATH)),
        json.loads(repo_manager.get_text(PREVIEWS_PATH)),
    )

    update_result = db.update(new_update_strings['release'], new_update_strings['preview'])

    if not update_result.did_update:
        logging.info('Did not receive any brand new UpdateInfo items.')
        return

    parsed_db = dbparser.run(db.release_strings, db.beta_strings, db.preview_strings)

    repo_manager.update_file(json.dumps(db.release_strings, indent=4), RELEASES_PATH, update_result.commit_message)
    repo_manager.update_file(json.dumps(db.preview_strings, indent=4), PREVIEWS_PATH, update_result.commit_message)
    repo_manager.update_file(json.dumps(parsed_db, indent=4), VERSIONS_PATH, update_result.commit_message)


# Mojang seems to have stopped releasing betas for Windows.
# The last beta released is 1.19.34.0 released on May 19, 2022.
# For this reason we don't touch betas here.


class NewUpdateStrings(TypedDict):
    release: list[str]
    preview: list[str]


def get_new_update_strings(new_updates: list[requester.UpdateInfo]) -> NewUpdateStrings:
    split_new_updates = {}
    for type_, prefix in ('release', 'Microsoft.MinecraftUWP_'), ('preview', 'Microsoft.MinecraftWindowsBeta_'):
        split_new_updates[type_] = [
            new_update for new_update in new_updates if new_update.package_moniker.startswith(prefix)
        ]

    new_update_strings = {}
    for type_ in 'release', 'preview':
        new_update_strings[type_] = [str(new_update) for new_update in split_new_updates[type_]]

    return new_update_strings


if __name__ == '__main__':
    main()
