from typing import Callable
from xml.etree.ElementTree import Element
import json
import logging

from BedrockDatabaseBot.net.structs import UpdateInfo, Cookie
from BedrockDatabaseBot.net import envelope_factories, parsers, soap

URL = 'https://fe3cr.delivery.mp.microsoft.com/ClientWebService/client.asmx'
SECURED_URL = 'https://fe3cr.delivery.mp.microsoft.com/ClientWebService/client.asmx/secured'


PRODUCT_IDS = {
    'release': '9nblggh2jhxj',
    'beta': '9nblggh2jhxj',
    'preview': '9p5x4qvlc2xr'
}

CATEGORY_IDS = {
    'release': 'd25480ca-36aa-46e6-b76b-39608d49558c',
    'beta': 'd25480ca-36aa-46e6-b76b-39608d49558c',
    'preview': '188f32fc-5eaa-45a8-9f78-7dde4322d131'
}


def run() -> list[UpdateInfo]:
    sync_updates_response_envelope = _get_sync_updates_response_envelope()
    sync_updates = parsers.parse_sync_updates_response_envelope(sync_updates_response_envelope)

    minecraft_update_info_list = [
        update_info for update_info in sync_updates.new_updates
        if update_info.package_moniker.startswith('Microsoft.Minecraft')
    ]

    logging.info(
        str(len(minecraft_update_info_list)) +
        ' Minecraft UpdateInfo items have been returned. ' +
        str(minecraft_update_info_list)
    )

    _save_last_cookie(sync_updates.new_cookie)
    return minecraft_update_info_list


def _load_last_cookie() -> Cookie:
    with open('last_cookie.json') as f:
        cookie_data = json.load(f)
    return Cookie(cookie_data['encrypted_data'], cookie_data['expiration'])


def _save_last_cookie(cookie: Cookie):
    with open('last_cookie.json', 'w') as f:
        json.dump({'encrypted_data': cookie.encrypted_data, 'expiration': cookie.expiration}, f, indent=4)


def _get_sync_updates_response_envelope():
    func: Callable[[Cookie], Element] = lambda cookie: soap.post_envelope(
            SECURED_URL,
            envelope_factories.make_sync_updates_envelope(
                SECURED_URL, cookie, [CATEGORY_IDS['release'], CATEGORY_IDS['preview']]
            )
        )

    try:
        return func(_load_last_cookie())
    except (soap.SOAPError, FileNotFoundError) as e:
        logging.error(str(e) + ' Trying again.')

        get_config_response_envelope = soap.post_envelope(
            SECURED_URL, envelope_factories.make_get_config_envelope(SECURED_URL)
        )
        last_change = parsers.parse_get_config_response_envelope(get_config_response_envelope).last_change

        get_cookie_response_envelope = soap.post_envelope(
            SECURED_URL, envelope_factories.make_get_cookie_envelope(SECURED_URL, last_change)
        )
        return func(parsers.parse_get_cookie_response_envelope(get_cookie_response_envelope))
