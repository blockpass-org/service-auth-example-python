import json
import requests
from config import Config
from modules.utils.logger import get_logger

LOGGER = get_logger()


class BlockpassApi (object):
    @staticmethod
    def handshake(code, session_code):
        bp_url = Config.BP_URL
        bp_client_id = Config.BP_CLIENT_ID
        bp_secret_id = Config.BP_SECRET_ID

        endpoint = bp_url + '/api/v0.3/oauth2/token/'
        LOGGER.info(['BlockpassApi', endpoint, bp_client_id, bp_secret_id])
        
        handShakeResponse = requests.post(endpoint, json={
            'client_id': bp_client_id,
            'client_secret': bp_secret_id,
            'code': code,
            'session_code': session_code,
            'grant_type': 'authorizationcode'
        })

        return handShakeResponse


    @staticmethod
    def queryBlockpassProfile(user_access_token):
        bp_url = Config.BP_URL

        endpoint = bp_url + '/api/v0.3/oauth2/profile'
        LOGGER.info(['BlockpassApi', endpoint])

        bpProfileResponse = requests.post(endpoint, headers = {
            'Authorization': user_access_token
        })

        return bpProfileResponse

    @staticmethod
    def refreshBlockpassToken(user_access_token, refresh_token, client_secret):
        bp_url = Config.BP_URL

        endpoint = bp_url + '/api/v0.3/service/renewStoc'
        LOGGER.info(['BlockpassApi', endpoint])

        bpNewTokenResponse = requests.post(endpoint, json={
            stoc: user_access_token,
            stoc_refresh: refresh_token,
            client_secret: client_secret
        })

        return bpNewTokenResponse

    @staticmethod
    def sendPN(user_access_token, title, message):
        bp_url = Config.BP_URL

        endpoint = bp_url + '/api/v0.3/certificate_new/feedBack'
        LOGGER.info(['BlockpassApi', endpoint])

        bpPnResponse = requests.post(endpoint, headers = {
            'Authorization': user_access_token
        }, json={
            noti: {
                type: 'info',
                title: title,
                mssg: message
            }
        })

        return bpPnResponse

    @staticmethod
    def ssoComplete(user_access_token, session_code, your_service_accessControl):
        bp_url = Config.BP_URL

        endpoint = bp_url + '/api/v0.3/service/complete/'
        LOGGER.info(['BlockpassApi', endpoint])

        bpProfileResponse = requests.post(endpoint, json={
            'result': 'success',
            'custom_data': json.dumps({
                'session_Code': session_code,
                'extraData': {
                    'your_service_accessControl': your_service_accessControl
                }
            })
        }, headers={
            'Authorization': user_access_token
        })

        return bpProfileResponse
