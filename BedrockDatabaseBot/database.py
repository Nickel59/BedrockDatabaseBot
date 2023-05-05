from dataclasses import dataclass


@dataclass(slots=True)
class Database:
    release_strings: list[str]
    beta_strings: list[str]
    preview_strings: list[str]

    @dataclass(frozen=True, slots=True)
    class UpdateResult:
        did_update: bool
        commit_message: str

    def update(self, new_release_strings: list[str], new_preview_strings: list[str]) -> UpdateResult:
        """Returns whether the DB was updated."""
        releases_update_result = self._update_slot(self.release_strings, new_release_strings)
        previews_update_result = self._update_slot(self.preview_strings, new_preview_strings)

        did_update = releases_update_result[0] or releases_update_result[0]
        commit_message = ' | '.join([msg for msg in (releases_update_result[1], previews_update_result[1]) if msg])

        return self.UpdateResult(did_update, commit_message)

    def _update_slot(self, slot: list[str], new_update_strings) -> tuple[bool, str]:
        """Returns whether the slot was updated."""
        did_update = False
        commit_message = ''
        for new_update_string in new_update_strings:
            if new_update_string in slot:
                continue
            slot.append(new_update_string)
            did_update = True
            commit_message = self._get_commit_message(new_update_string)
        return did_update, commit_message

    @staticmethod
    def _get_commit_message(update_string: str) -> str:
        version_name = update_string.split()[1].removesuffix('__8wekyb3d8bbwe').split('_')[1]
        if update_string.split()[1].startswith('Microsoft.MinecraftUWP_'):
            type_ = 'Release'
        elif update_string.split()[1].startswith('Microsoft.MinecraftWindowsBeta_'):
            type_ = 'Preview'
        else:  # should never happen
            class InvalidUpdateStringError(ValueError):
                pass
            raise InvalidUpdateStringError('Invalid update string.')
        return f'{version_name} ({type_})'
