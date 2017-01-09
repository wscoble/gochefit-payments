import boto3
import requests
from dotenv import load_dotenv, find_dotenv
import os
from authorizenet import apicontractsv1
from authorizenet.apicontrollers import *
from decimal import *


# Process environment variables
de = find_dotenv()
if de is not None:
    load_dotenv(de)

name = os.environ['AUTHORIZE_NAME']
transactionKey = os.environ['AUTHORIZE_TRANSACTION_KEY']
url = os.environ['AUTHORIZE_URL']

kms_client = boto3.client('kms')

try:
    name = kms_client.decrypt(
        CiphertextBlob=name.decode('base64')
    )['Plaintext']
    transactionKey = kms_client.decrypt(
        CiphertextBlob=transactionKey.decode('base64')
    )['Plaintext']
    url = kms_client.decrypt(
        CiphertextBlob=url.decode('base64')
    )['Plaintext']
except:
    pass


def handle(event, context):
    # validate request
    for c in ['amount', 'dataDescriptor', 'dataValue']:
        if c not in event:
            raise Exception('Invalid request')

    # set up payload data
    amount = event['amount']
    dataDescriptor = event['dataDescriptor']
    dataValue = event['dataValue']

    # create authorize.net payload
#     payload = '''<?xml version="1.0" encoding="UTF-8"?>
# <createTransactionRequest xmlns="AnetApi/xml/v1/schema/AnetApiSchema.xsd">
#       <merchantAuthentication>
#          <name>{}</name>
#          <transactionKey>{}</transactionKey>
#       </merchantAuthentication>
#       <transactionRequest>
#          <transactionType>authCaptureTransaction</transactionType>
#          <amount>{}</amount>
#          <currencyCode>USD</currencyCode>
#          <payment>
#             <opaqueData>
#                <dataDescriptor>{}</dataDescriptor>
#                <dataValue>{}</dataValue>
#             </opaqueData>
#          </payment>
#       </transactionRequest>
# </createTransactionRequest>'''.format(name, transactionKey, amount, dataDescriptor, dataValue)
#
#     headers = {
#         'Content-Type': 'application/xml'
#     }
#
#     # send payload to authorize.net
#
#     response = requests.post(url=url, data=payload, headers=headers)
#
#     # return response to web app
#     if response.status_code == 200:
#         return response.content
#     else:
#         raise Exception('Failed to make payment')
