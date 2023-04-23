from dataclasses import dataclass
from operator import itemgetter
from copy import deepcopy
import json

from natsort import natsorted


AVAILABLE_ARCHITECTURES = ['x64', 'x86', 'arm']


def run(releases_str: str, betas_str: str, previews_str: str) -> str:
    line_collection = _read_lines(releases_str, betas_str, previews_str)

    release_parsed_lines = _parse_lines(line_collection.releases, 'release')
    beta_parsed_lines = _parse_lines(line_collection.betas, 'beta')
    preview_parsed_lines = _parse_lines(line_collection.previews, 'preview')

    version_info_list = _get_version_info_list(release_parsed_lines + beta_parsed_lines + preview_parsed_lines)

    version_dict_list = _get_version_dict_list(version_info_list)
    version_dict_list = natsorted(version_dict_list, key=itemgetter(*['name']))

    return json.dumps(version_dict_list, indent=4)


@dataclass(slots=True)
class _ParsedLine:
    name: str
    architecture: str
    type: str
    guid: str


@dataclass(slots=True)
class _VersionInfo:
    name: str
    architecture: str
    type: str
    guids: list[str]


@dataclass(slots=True)
class _LineCollection:
    releases: list[str]
    betas: list[str]
    previews: list[str]


def _read_lines(releases_str: str, betas_str: str, previews_str: str) -> _LineCollection:
    release_lines = json.loads(releases_str)
    beta_lines = json.loads(betas_str)
    preview_lines = json.loads(previews_str)

    return _LineCollection(release_lines, beta_lines, preview_lines)


def _parse_line(line: str, version_type: str) -> _ParsedLine:
    line = line.removesuffix('__8wekyb3d8bbwe')

    guid, rest = line.split(' ')

    _, name, architecture = rest.split('_')

    return _ParsedLine(name, architecture, version_type, guid)


def _parse_lines(lines: list[str], version_type: str) -> list[_ParsedLine]:
    parsed_lines = [_parse_line(line, version_type) for line in lines if '.EAppx' not in line]
    return [parsed_line for parsed_line in parsed_lines if not parsed_line.name.endswith('.70')]


def _get_version_info_list(parsed_lines: list[_ParsedLine]) -> list[_VersionInfo]:
    parsed_lines = deepcopy(parsed_lines)

    version_info_list = []

    while parsed_lines:
        base_parsed_line = parsed_lines.pop(0)
        parsed_lines_to_squash = [
            parsed_line for parsed_line in parsed_lines
            if (parsed_line.name, parsed_line.architecture, parsed_line.type) ==
               (base_parsed_line.name, base_parsed_line.architecture, base_parsed_line.type)
        ]

        version_info_list.append(
            _VersionInfo(
                base_parsed_line.name,
                base_parsed_line.architecture,
                base_parsed_line.type,
                [base_parsed_line.guid] + [parsed_line.guid for parsed_line in parsed_lines_to_squash]
            )
        )

        for parsed_line_to_squash in parsed_lines_to_squash:
            parsed_lines.remove(parsed_line_to_squash)

    return version_info_list


def _get_version_dict_list(version_info_list: list[_VersionInfo]) -> list[dict]:
    version_info_list = deepcopy(version_info_list)

    version_dict_list = []

    while version_info_list:
        base_version_info = version_info_list.pop(0)
        version_infos_to_squash = [
            version_info for version_info in version_info_list
            if (version_info.name, version_info.type) == (base_version_info.name, base_version_info.type)
        ]

        guids_dict = {}
        for architecture in AVAILABLE_ARCHITECTURES:
            guids_dict[architecture] = base_version_info.guids if base_version_info.architecture == architecture else []
            for version_info_to_squash in version_infos_to_squash:
                guids_dict[architecture] += version_info_to_squash.guids if version_info_to_squash.architecture ==\
                                                                            architecture else []

        version_dict_list.append(
            {
                'name': base_version_info.name,
                'type': base_version_info.type,
                'guids': guids_dict
            }
        )

        for version_info_to_squash in version_infos_to_squash:
            version_info_list.remove(version_info_to_squash)

    return version_dict_list
