import json
import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify
from modules.utils.logger import get_logger
from modules.handlers.error_handler import handle_error
from modules.services.blockpass_http import BlockpassApi
from modules.objects.kyc_record_model import KycRecordModel

LOGGER = get_logger()

class BlockpassHandler (object):
  
  @staticmethod
  def status(endpoint):
    try:

      # Step 0: Parse Mobile Client payload (application/json)
      content = request.get_json(silent=True)
      mobileRequestPayload = {
          'code': content.get('code'),
          'sessionCode': content.get('sessionCode', None)
      }
      LOGGER.info(['mobileRequestPayload', mobileRequestPayload])
      
      # Basic Auth
      bpId, bp_user_access_token = BlockpassHandler.basicAuth(
          mobileRequestPayload)
      if bpId == None:
          return jsonify({'err': 500, 'msg': 'basic_auth_failed'}), 500

      # Step 3: Query KycRecord base on bpId
      record = KycRecordModel.find_record_by_blockpassId(bpId)

      if record == None:
        # New User
        message = {
            'status': KycRecordModel.BLOCKPASS_RECORD_STATUS['NOT_FOUND'],
            'identities': KycRecordModel.BLOCKPASS_STATUS_DEFAULT['identities'],
            'certificates': []
        }
        return jsonify(message)
      else:  
        # Old user
        message = {
            'nextAction': 'none',
            'status': KycRecordModel.BLOCKPASS_RECORD_STATUS['APPROVED'],
            'identities': record.generateProfileStatus(),
            'certificates': record.generateCertificateStatus()
        }

        # Notify to Web-page
        session_code = mobileRequestPayload.get('sessionCode')
        if session_code != None:
            BlockpassHandler.ssoComplete(bp_user_access_token, session_code, record)

        return jsonify(message)
      

    except Exception as exception:
      return handle_error(endpoint=endpoint, e=exception)


  #------------------------------------------------------------
  @staticmethod
  def create_record(endpoint):
    try:
     
      # Step 0: Parse Mobile Client payload (application/json)
      content = request.get_json(silent=True)
      mobileRequestPayload = {
          'code': content.get('code'),
          'sessionCode': content.get('sessionCode')
      }
      LOGGER.info(['mobileRequestPayload', mobileRequestPayload])

      # Basic Auth
      bpId, bp_user_access_token, bp_user_refresh_token, bp_user_access_token_expires_in = BlockpassHandler.basicAuth(
          mobileRequestPayload)
      if bpId == None:
          return jsonify({'err': 500, 'msg': 'basic_auth_failed'}), 500
      
      # -- Check old record has any missing fields.
      #     - Missing fields => request upload data again
      #     - No => return action 'none'
      record = KycRecordModel.find_record_by_blockpassId(bpId)
      if record != None and record.isFullfillRecord():
          return jsonify({
              'nextAction': 'none',
          })
    
      # Step 3: Create new record to store user data
      if record == None:
        record = KycRecordModel()
        record.bpId = bpId

      # store this for further query if need
      record.bpToken = bp_user_access_token
      record.bpRefreshToken = bp_user_refresh_token

      # time token expired at
      now = datetime.datetime.now()
      record.bpExpiredAt = now + datetime.timedelta(milliseconds = bp_user_access_token_expires_in)
      
      # temporary data. Which using later on after user complete upload data
      record.session_code = mobileRequestPayload.get('sessionCode')
      
      # save record
      record.save()

      # one_time_pass to upload data
      one_time_pass = 'ugly-pass-for-record:' + str(record.id)

      # request mobile app upload data 
      return jsonify({
          'nextAction': 'upload',
          'accessToken': one_time_pass,
          'requiredFields': KycRecordModel.requiredFields(),
          'certs': KycRecordModel.niceToHaveCertificates()
      })

    except Exception as exception:
      return handle_error(endpoint=endpoint, e=exception)
  
  #------------------------------------------------------------
  @staticmethod
  def upload(endpoint):
    try:
      # Step 0: Parse Mobile Client payload (application/json)
      fields = request.form
      files = request.files

      one_time_pass = fields.get('accessToken')
      email = fields.get('email')
      selfie = files.get('selfie')
      onfido = fields.get('[cer]onfido')
      onfido_service_cert = fields.get('[cer]onfido-service-cert')
      complyadvantage_service_cert = fields.get('[cer]complyadvantage-service-cert')

      LOGGER.info(['mobileRequestPayload', fields, files])

      # Step 1: check one_time_pass
      tmp = one_time_pass.split(':')
      if tmp[0] != 'ugrly-pass-for-record':
        return jsonify({'err': 403, 'msg': 'one_time_pass_wrong'}), 403

      recordId = tmp[1]

      # Step 2: fill data info KycModel
      record = KycRecordModel.find_record_by_id(recordId)
      record.email = email

      # It is just demo. It better if we store it some-where and just store link in DB
      record.selfie = selfie
      
      print record.session_code
      if record.session_code != None:
          BlockpassHandler.ssoComplete(record.bpToken, record.session_code, record)
          record.session_code = None

    
      # Save it!
      record.save()
  
      return jsonify({
          'nextAction': 'none',
      })

    except Exception as exception:
      return handle_error(endpoint=endpoint, e=exception)

  #------------------------------------------------------------
  @staticmethod
  def basicAuth(mobileRequestPayload):
      # Step 1: HandShake ensure that it is trusted client
      handShakeResponse = BlockpassApi.handshake(
          mobileRequestPayload['code'],
          mobileRequestPayload['sessionCode']
      )

      # -- LOGGER.info(['handShakeResponse', handShakeResponse.text])
      if handShakeResponse.status_code != 200:
          LOGGER.error(jsonify({'err': 400, 'msg': 'handshake_failed'}))
          return None

      handShakeResponse = json.loads(handShakeResponse.text)
      bp_user_access_token = handShakeResponse['access_token']
      bp_user_refresh_token = handShakeResponse['refresh_token']
      bp_user_access_token_expires_in = handShakeResponse['expires_in']

      # Step 2: Query Blockpass profile (contain BpId)
      bpProfileResponse = BlockpassApi.queryBlockpassProfile(
          bp_user_access_token)

      if bpProfileResponse.status_code != 200:
          LOGGER.error(jsonify({'err': 400, 'msg': 'profile_query_failed'}))
          return None

      bpProfileResponse = json.loads(bpProfileResponse.text)
      bpId = bpProfileResponse['id']
      return bpId, bp_user_access_token, bp_user_refresh_token, bp_user_access_token_expires_in

  #------------------------------------------------------------
  @staticmethod
  def ssoComplete(bp_user_access_token, session_code, record):

      # Implement logic for token generated here
      my_service_access_token = 'i am here for id ->' + record.id
      BlockpassApi.ssoComplete(
          bp_user_access_token, session_code, my_service_access_token)
