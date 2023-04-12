import xml.etree.ElementTree as ET

import requests


class SOAPError(Exception):
    pass


def post_envelope(url: str, envelope: ET.Element) -> ET.Element:
    res = requests.post(
        url,
        data=ET.tostring(envelope),
        headers={'content-type': 'application/soap+xml; charset=utf-8'},
        verify=False
    )

    if res.status_code != 200:
        error_message = ET.fromstring(res.content).findtext('./{*}Body/{*}Fault/{*}Reason/{*}Text')
        error_message = error_message if error_message else 'An unknown error has occurred'
        error_message = error_message.strip()
        error_message = error_message + '.' if not error_message.endswith('.') else error_message
        raise SOAPError(error_message)

    return ET.fromstring(res.content)
