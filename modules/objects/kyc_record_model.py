import json


class KycRecordModel (object):
    UDID = 1
    DB = {}
    BLOCKPASS_RECORD_STATUS = {
        'NOT_FOUND': 'notFound',
        'WAITING': 'waiting',
        'INREVIEW': 'inreview',
        'APPROVED': 'approved'
    }
    BLOCKPASS_STATUS_DEFAULT = {
        'identities': [{
            'slug': 'email',
            'status': ''
        },
            {
            'slug': 'selfie',
            'status': ''
        }]
    }
        
    def __init__(self):
        self.id = str(KycRecordModel.UDID)
        self.bpId = None
        self.bpToken = None
        self.email = None
        self.selfie = None
        self.onfido = None
        self.onfido_service_cert = None
        self.complyadvantage_service_cert = None

        KycRecordModel.UDID = KycRecordModel.UDID + 1


    def save(self):
        KycRecordModel.DB[self.id] = self

    def generateProfileStatus(self):
        return [
            {
                'slug': 'email',
                'status': 'received' if self.email != None else 'missing'
            },
            {
                'slug': 'selfie',
                'status': 'received' if self.selfie != None else 'missing'
            }
        ]

    def generateCertificateStatus(self):
        res = []

        if self.onfido != None:
            res.append({
                    'slug': 'onfido'
            })
        
        if self.onfido_service_cert != None:
            res.append({
                    'slug': 'onfido-service-cert'
            })

        if self.complyadvantage_service_cert != None:
            res.append({
                    'slug': 'complyadvantage-service-cert'
            })
        
        return res
        

    def isFullfillRecord(self):
        return self.email != None and self.selfie != None

    def toJson(self):
        return json.dumps({
            'id': self.id,
            'bpId': self.bpId,
            'email': self.email,
            'selfie': str(self.selfie),
            'onfido': str(self.onfido),
            'onfido-service-cert': str(self.onfido_service_cert),
            'complyadvantage-service-cert': str(self.complyadvantage_service_cert),
        })

    @staticmethod
    def find_record_by_id(id):
        return KycRecordModel.DB.get(id, None)

    @staticmethod
    def find_record_by_blockpassId(bpId):
        print KycRecordModel.DB
        for key, value in KycRecordModel.DB.iteritems():
            if value.bpId == bpId:
                return value
        return None

    @staticmethod
    def requiredFields(): 
        return ['email', 'selfie']

    @staticmethod
    def niceToHaveCertificates():
        return ['onfido', 'onfido-service-cert', 'complyadvantage-service-cert']
