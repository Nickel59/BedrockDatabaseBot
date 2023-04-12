from xml.etree.ElementTree import Element, SubElement
from datetime import datetime, timedelta

from requester.net.structs import Cookie


WUCLIENT = 'http://www.microsoft.com/SoftwareDistribution/Server/ClientWebService'
WSU = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd'


def make_get_cookie_envelope(url: str, config_last_change: str) -> Element:
    return _Envelope(url, _ElementGetCookie(config_last_change))


def make_get_config_envelope(url: str) -> Element:
    return _Envelope(url, _ElementGetConfig())


def make_sync_updates_envelope(url: str, cookie: Cookie, category_ids: list[str]) -> Element:
    return _Envelope(url, _ElementSyncUpdates(cookie, category_ids))


class _ElementGetCookie(Element):
    def __init__(self, config_last_change: str):
        super().__init__('GetCookie')

        last_change = SubElement(self, 'lastChange')
        last_change.text = config_last_change

        current_time = SubElement(self, 'currentTime')
        current_time.text = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

        protocol_version = SubElement(self, 'protocolVersion')
        protocol_version.text = '1.81'


class _ElementGetConfig(Element):
    def __init__(self):
        super().__init__('GetConfig')

        protocol_version = SubElement(self, 'protocolVersion')
        protocol_version.text = '1.81'


class _ElementSyncUpdates(Element):
    def __init__(self, cookie: Cookie, category_ids: list[str]):
        super().__init__('SyncUpdates')

        cookie_element = SubElement(self, 'cookie')

        expiration = SubElement(cookie_element, 'Expiration')
        expiration.text = cookie.expiration

        encrypted_data = SubElement(cookie_element, 'EncryptedData')
        encrypted_data.text = cookie.encrypted_data

        parameters = SubElement(self, 'parameters')

        express_query = SubElement(parameters, 'ExpressQuery')
        express_query.text = 'false'

        installed_non_leaf_update_ids = SubElement(parameters, 'InstalledNonLeafUpdateIDs')
        for installed_non_leaf_update_id in [
            1, 2, 3, 11, 19, 2359974, 5169044, 8788830, 23110993, 23110994, 59830006, 59830007, 59830008, 60484010,
            62450018, 62450019, 62450020, 98959022, 98959023, 98959024, 98959025, 98959026, 129905029, 130040030,
            130040031, 130040032, 130040033, 138372035, 138372036, 139536037, 158941041, 158941042, 158941043,
            158941044,
            # ARM
            133399034, 2359977
        ]:
            int_ = SubElement(installed_non_leaf_update_ids, 'int')
            int_.text = str(installed_non_leaf_update_id)

        skip_software_sync = SubElement(parameters, 'SkipSoftwareSync')
        skip_software_sync.text = 'false'

        need_two_group_out_of_scope_updates = SubElement(parameters, 'NeedTwoGroupOutOfScopeUpdates')
        need_two_group_out_of_scope_updates.text = 'true'

        filter_app_category_ids = SubElement(parameters, 'FilterAppCategoryIds')

        for category_id in category_ids:
            category_identifier = SubElement(filter_app_category_ids, 'CategoryIdentifier')

            id_ = SubElement(category_identifier, 'Id')
            id_.text = category_id

        treat_app_category_ids_as_installed = SubElement(parameters, 'TreatAppCategoryIdsAsInstalled')
        treat_app_category_ids_as_installed.text = 'true'

        also_perform_regular_sync = SubElement(parameters, 'AlsoPerformRegularSync')
        also_perform_regular_sync.text = 'false'

        computer_spec = SubElement(parameters, 'ComputerSpec')
        computer_spec.text = ' '

        extended_update_info_parameters = SubElement(parameters, 'ExtendedUpdateInfoParameters')

        xml_update_fragment_types = SubElement(extended_update_info_parameters, 'XmlUpdateFragmentTypes')

        xml_update_fragment_type1 = SubElement(xml_update_fragment_types, 'XmlUpdateFragmentType')
        xml_update_fragment_type1.text = 'Extended'

        xml_update_fragment_type2 = SubElement(xml_update_fragment_types, 'XmlUpdateFragmentType')
        xml_update_fragment_type2.text = 'LocalizedProperties'

        xml_update_fragment_type3 = SubElement(xml_update_fragment_types, 'XmlUpdateFragmentType')
        xml_update_fragment_type3.text = 'Eula'

        locales = SubElement(extended_update_info_parameters, 'Locales')

        string1 = SubElement(locales, 'string')
        string1.text = 'en-US'

        string2 = SubElement(locales, 'string')
        string2.text = 'en'

        client_preferred_languages = SubElement(parameters, 'ClientPreferredLanguages')

        string3 = SubElement(client_preferred_languages, 'string')
        string3.text = 'en-US'

        products_parameters = SubElement(parameters, 'ProductsParameters')

        sync_current_version_only = SubElement(products_parameters, 'SyncCurrentVersionOnly')
        sync_current_version_only.text = 'false'

        device_attributes = SubElement(products_parameters, 'DeviceAttributes')
        device_attributes.text = 'E:BranchReadinessLevel=CBB&DchuNvidiaGrfxExists=1&ProcessorIdentifier=Intel64%20Family%206%20Model%2063%20Stepping%202&CurrentBranch=rs4_release&DataVer_RS5=1942&FlightRing=Retail&AttrDataVer=57&InstallLanguage=en-US&DchuAmdGrfxExists=1&OSUILocale=en-US&InstallationType=Client&FlightingBranchName=&Version_RS5=10&UpgEx_RS5=Green&GStatus_RS5=2&OSSkuId=48&App=WU&InstallDate=1529700913&ProcessorManufacturer=GenuineIntel&AppVer=10.0.17134.471&OSArchitecture=AMD64&UpdateManagementGroup=2&IsDeviceRetailDemo=0&HidOverGattReg=C%3A%5CWINDOWS%5CSystem32%5CDriverStore%5CFileRepository%5Chidbthle.inf_amd64_467f181075371c89%5CMicrosoft.Bluetooth.Profiles.HidOverGatt.dll&IsFlightingEnabled=0&DchuIntelGrfxExists=1&TelemetryLevel=1&DefaultUserRegion=244&DeferFeatureUpdatePeriodInDays=365&Bios=Unknown&WuClientVer=10.0.17134.471&PausedFeatureStatus=1&Steam=URL%3Asteam%20protocol&Free=8to16&OSVersion=10.0.17134.472&DeviceFamily=Windows.Desktop'

        caller_attributes = SubElement(products_parameters, 'CallerAttributes')
        caller_attributes.text = 'E:Interactive=1&IsSeeker=1&Acquisition=1&SheddingAware=1&Id=Acquisition%3BMicrosoft.WindowsStore_8wekyb3d8bbwe&'

        products_parameters.append(Element('Products'))


class _Envelope(Element):
    def __init__(self, url: str, element: Element):
        super().__init__(
            's:Envelope',
            {'xmlns:a': 'http://www.w3.org/2005/08/addressing', 'xmlns:s': 'http://www.w3.org/2003/05/soap-envelope'}
        )

        self.append(_Header(url, element.tag))

        body = SubElement(self, 's:Body')
        body.append(element)

        element.set('xmlns', WUCLIENT)


class _Header(Element):
    def __init__(self, url: str, method_name: str):
        super().__init__('s:Header')

        action = SubElement(self, 'a:Action', {'s:mustUnderstand': '1'})
        action.text = WUCLIENT + '/' + method_name
        message_id = SubElement(self, 'a:MessageID')
        message_id.text = 'urn:uuid:1a88ab88-d8eb-47bb-82d9-f2bd82654c6e'
        to = SubElement(self, 'a:To', {'s:mustUnderstand': '1'})
        to.text = url
        security = SubElement(
            self,
            'o:Security',
            {
                's:mustUnderstand': '1',
                'xmlns:o': 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd'
            }
        )
        timestamp = SubElement(security, 'Timestamp', {'xmlns': WSU})
        created = SubElement(timestamp, 'Created')
        created.text = (created_time := datetime.now()).strftime('%Y-%m-%dT%H:%M:%SZ')
        expires = SubElement(timestamp, 'Expires')
        expires.text = (created_time + timedelta(minutes=5)).strftime('%Y-%m-%dT%H:%M:%SZ')
        windows_update_tickets_token = SubElement(
            security,
            'wuws:WindowsUpdateTicketsToken',
            {
                'wsu:id': 'ClientMSA',
                'xmlns:wsu': WSU,
                'xmlns:wuws': 'http://schemas.microsoft.com/msus/2014/10/WindowsUpdateAuthorization'
            }
        )
        ticket_type = SubElement(
            windows_update_tickets_token, 'TicketType', {'Name': 'AAD', 'Version': '1.0', 'Policy': 'MBI_SSL'}
        )
        # if user.token:
        # ticket_type = ET.SubElement(
        #     windows_update_tickets_token, 'TicketType', {'Name': 'MSA', 'Version': '1.0', 'Policy': 'MBI_SSL'}
        # )
        #     user = ET.SubElement(ticket_type, 'User')
        #     user.text = 'some stuff that matters'
