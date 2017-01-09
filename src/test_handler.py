from handler import handle


def test_handle_card_payment():
    dataDescriptor = 'COMMON.ACCEPT.INAPP.PAYMENT'
    dataValue = '9471471570959063005001'
    amount = 151

    print handle({
        'dataDescriptor': dataDescriptor,
        'dataValue': dataValue,
        'amount': amount,
        'command': 'payWithCard'
    })


def test_handle_paypal():
    amount = 151
    successUrl = 'https://localhost:8443/paypal-success'
    cancelUrl = 'https://localhost:8443/paypal-cancel'

    print handle({
        'command': 'paypal',
        'amount': amount,
        'successUrl': successUrl,
        'cancelUrl': cancelUrl
    })
