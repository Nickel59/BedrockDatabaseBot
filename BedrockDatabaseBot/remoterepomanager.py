import logging

import json
from github import Github


class RemoteRepositoryManager:
    def __init__(self):
        self._repo = Github(self._get_token()).get_user().get_repo('BedrockDB')

    def get_text(self, remote_path: str):
        return self._repo.get_contents(remote_path).decoded_content.decode().replace('\r', '')

    def update_file(self, local_path: str, remote_path: str, message: str):
        contents = self._repo.get_contents(remote_path)

        with open(local_path) as f:
            new_text = f.read()

        # don't use get_text() to avoid unnecessary API calls
        old_text = contents.decoded_content.decode().replace('\r', '')
        if old_text == new_text:
            logging.info(f'GitHub: Skipping the file "{local_path}" - no difference in content with the remote file.')
            return

        if not self._is_new_file_valid(new_text, old_text):
            logging.info(f'GitHub: Skipping the file "{local_path}" - the file is invalid.')
            return

        self._repo.update_file(contents.path, message, new_text, contents.sha)

    @staticmethod
    def _is_new_file_valid(new_text: str, old_text: str) -> bool:
        if len(new_text) <= len(old_text):
            return False
        try:
            _ = json.loads(new_text)
        except Exception:
            return False
        return True

    @staticmethod
    def _get_token() -> str:
        with open('token.txt') as f:
            lines = f.readlines()
        if not lines:
            raise TokenNotFound
        return lines[0]


class TokenNotFound(Exception):
    def __init__(self, *args):
        super().__init__(*args if args else 'The token has not been found.')
