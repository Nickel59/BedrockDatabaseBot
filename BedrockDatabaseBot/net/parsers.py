from xml.etree.ElementTree import Element, fromstring

from net.structs import SyncUpdates, Cookie, UpdateInfo, Config


class ParsingError(ValueError):
    pass


def parse_sync_updates_response_envelope(response: Element) -> SyncUpdates:
    new_updates_element = response.find(
        './{*}Body/{*}SyncUpdatesResponse/{*}SyncUpdatesResult/{*}NewUpdates'
    )
    if new_updates_element is None:
        raise ParsingError('No NewUpdates element has been found.')

    new_updates = []
    for update_info_element in new_updates_element:
        update_info = _parse_update_info_element(update_info_element)
        if update_info:
            new_updates.append(update_info)

    new_encrypted_data = response.findtext(
        './{*}Body/{*}SyncUpdatesResponse/{*}SyncUpdatesResult/{*}NewCookie/{*}EncryptedData'
    )
    new_expiration = response.findtext(
        './{*}Body/{*}SyncUpdatesResponse/{*}SyncUpdatesResult/{*}NewCookie/{*}Expiration'
    )
    if (not new_encrypted_data) or (not new_expiration):
        raise ParsingError('No NewCookie/EncryptedData or NewCookie/Expiration value has been found.')

    return SyncUpdates(new_updates, Cookie(new_encrypted_data, new_expiration))


def parse_get_cookie_response_envelope(response: Element) -> Cookie:
    encrypted_data = response.findtext('./{*}Body/{*}GetCookieResponse/{*}GetCookieResult/{*}EncryptedData')
    expiration = response.findtext('./{*}Body/{*}GetCookieResponse/{*}GetCookieResult/{*}Expiration')
    if (not encrypted_data) or (not expiration):
        raise ParsingError('No EncryptedData or Expiration value has been found.')

    return Cookie(encrypted_data, expiration)


def parse_get_config_response_envelope(response: Element) -> Config:
    last_change = response.findtext('./{*}Body/{*}GetConfigResponse/{*}GetConfigResult/{*}LastChange')
    if not last_change:
        raise ParsingError('No LastChange value has been found.')
    return Config(last_change)


def _parse_update_info_element(update_info_element: Element) -> UpdateInfo | None:
    xml = update_info_element.findtext('./{*}Xml')
    if not xml:
        return None

    xml_element = fromstring('<Xml>' + xml + '</Xml>')

    update_identity = xml_element.find('./{*}UpdateIdentity')
    appx_metadata = xml_element.find('./{*}ApplicabilityRules/{*}Metadata/{*}AppxPackageMetadata/{*}AppxMetadata')
    if (update_identity is None) or (appx_metadata is None):
        return None

    update_id = update_identity.get('UpdateID')
    package_moniker = appx_metadata.get('PackageMoniker')
    if (not update_id) or (not package_moniker):
        return None

    return UpdateInfo(update_id, package_moniker)
