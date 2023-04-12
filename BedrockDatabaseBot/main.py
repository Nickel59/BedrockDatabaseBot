import os
import logging
from logging.handlers import TimedRotatingFileHandler
import time

from env import RELEASES_PATH, BETAS_PATH, PREVIEWS_PATH, VERSIONS_PATH
import requester
import newupdatesmanager
import dbparser
from remoterepomanager import RemoteRepositoryManager


repo_manager = RemoteRepositoryManager()


def setup_timed_rotating_logger(log_path: str = 'logs', base_filename: str = 'bdb'):
    def namer(name: str) -> str:
        parent_dir_path, filename = os.path.split(name)
        filename = (filename.replace('.log', '') + '.log').lstrip('.')
        return os.path.join(parent_dir_path, filename)

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
    while True:
        try:
            run_one_cycle()
        except Exception as e:
            logging.error(str(e))
        print('Sleeping...')
        time.sleep(600)
        print('Sleep ended.\n')


def run_one_cycle():
    new_updates = newupdatesmanager.get_actual_new_updates(requester.run())
    logging.info('Brand new UpdateInfo items: ' + str(new_updates))

    if not new_updates:
        return

    newupdatesmanager.save_new_updates(new_updates)
    commit_message = newupdatesmanager.get_commit_message(new_updates)
    repo_manager.update_file(RELEASES_PATH, RELEASES_PATH, commit_message)
    repo_manager.update_file(PREVIEWS_PATH, PREVIEWS_PATH, commit_message)
    time.sleep(20)
    dbparser.run(
        repo_manager.get_text(RELEASES_PATH),
        repo_manager.get_text(BETAS_PATH),
        repo_manager.get_text(PREVIEWS_PATH),
        VERSIONS_PATH
    )
    repo_manager.update_file(VERSIONS_PATH, VERSIONS_PATH, commit_message)


if __name__ == '__main__':
    main()
