import hashlib
import json
import os
import time
from collections import OrderedDict
from decimal import *

import boto3
import requests
from dotenv import find_dotenv, load_dotenv

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


endpoint = 'https://apitest.authorize.net/xml/v1/request.api'
if (os.environ.has_key('PRODUCTION') and os.environ['PRODUCTION'] is 1):
    endpoint = 'https://api.authorize.net/xml/v1/request.api'


def generate_invoice_number(customerEmail, amount):
    return hashlib.sha1('{}:{}:{}'.format(time.time(), customerEmail, amount)).hexdigest()[:12].upper()


def build_paypal_transaction_payload(amount, successUrl, cancelUrl):
    '''
    {
        "createTransactionRequest": {
            "merchantAuthentication": {
                "name": "77rGC5zF",
                "transactionKey": "9Gdkre9dS33d88MZ"
            },
            "transactionRequest": {
                "transactionType": "authOnlyTransaction",
                "amount": "5",
                "payment": {
                    "payPal": {
                        "successUrl": "https://my.server.com/success.html",
                        "cancelUrl": "https://my.server.com/cancel.html"
                    }
                }
            }
        }
    }
    '''
    return {
        'createTransactionRequest': OrderedDict([
            ('merchantAuthentication', OrderedDict([
                ('name', name),
                ('transactionKey', transactionKey)
            ])),
            ('transactionRequest', OrderedDict([
                ('transactionType', 'authOnlyTransaction'),
                ('amount', amount),
                ('payment', OrderedDict([
                    ('paypal', OrderedDict([
                        ('successUrl', successUrl),
                        ('cancelUrl', cancelUrl)
                    ]))
                ]))
            ]))
        ])
    }


def build_accept_transaction_payload(amount,
                                     dataDescriptor,
                                     dataValue,
                                     customerEmail,
                                     customerFirstName,
                                     customerLastName,
                                     customerAddress,
                                     customerCity,
                                     customerState,
                                     customerZip,
                                     invoiceNumber,
                                     items):
    lineItems = [OrderedDict([
        ('itemId', '{}-{}'.format(item['name'],
                                  item['selectedOptions']['Size'])),
        ('name', item['name']),
        ('description', item['selectedOptions']['Size']),
        ('quantity', item['quantity']),
        ('unitPrice', float(item['basePrice']) + item['adjustments']['Price'])
    ]) for item in items]

    return {
        'createTransactionRequest': OrderedDict([
            ('merchantAuthentication', OrderedDict([
                ('name', name),
                ('transactionKey', transactionKey)
            ])),
            # ('refId', requestID),
            ('transactionRequest', OrderedDict([
                ('transactionType', 'authCaptureTransaction'),
                ('amount', amount),
                ('payment', OrderedDict([
                    ('opaqueData', OrderedDict([
                        ('dataDescriptor', dataDescriptor),
                        ('dataValue', dataValue)
                    ]))
                ])),
                ('order', OrderedDict([
                    ('invoiceNumber', invoiceNumber)
                ])),
                ('lineItems', OrderedDict([
                    ('lineItem', lineItems)
                ])),
                ('customer', OrderedDict([
                    ('email', customerEmail)
                ])),
                ('shipTo', OrderedDict([
                    ('firstName', customerFirstName),
                    ('lastName', customerLastName),
                    ('address', customerAddress),
                    ('city', customerCity),
                    ('state', customerState),
                    ('zip', customerZip)
                ]))
            ]))
        ])
    }


def handle(event, context):
    try:
        command = event['command']
    except TypeError:
        raise Exception('Invalid request')

    if command == 'payWithCard':
        expectedEventsFields = [
            'amount', 'dataDescriptor', 'dataValue', 'items', 'tax', 'shippingCost', 'customerInfo']
        # validate request
        for c in expectedEventsFields:
            if c not in event:
                raise Exception('Invalid request')

        payload = build_accept_transaction_payload(event['amount'],
                                                   event['dataDescriptor'],
                                                   event['dataValue'],
                                                   event['customerInfo'][
                                                       'email'],
                                                   event['customerInfo'][
                                                       'firstName'],
                                                   event['customerInfo'][
                                                       'lastName'],
                                                   event['customerInfo'][
                                                       'address'],
                                                   event['customerInfo'][
                                                       'city'],
                                                   event['customerInfo'][
                                                       'state'],
                                                   event['customerInfo'][
                                                       'zip'],
                                                   invoiceNumber,
                                                   event['items'])

        payload = json.dumps(payload)
        response = requests.post(
            endpoint, headers={'Content-Type': 'application/json'}, data=payload)

        return {'payload': payload, 'response': response.text}
    elif command == 'paypal':
        expectedEventsFields = [
            'amount', 'successUrl', 'cancelUrl']
        # validate request
        for c in expectedEventsFields:
            if c not in event:
                raise Exception('Invalid request')

        payload = build_paypal_transaction_payload(event['amount'],
                                                   event['successUrl'],
                                                   event['cancelUrl'])
        payload = json.dumps(payload)
        response = requests.post(
            endpoint, headers={'Content-Type': 'application/json'}, data=payload)

        return {'payload': payload, 'response': response.text}
    else:
        raise Exception('No command found')
