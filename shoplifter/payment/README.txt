"""
========
Moneris:
========

Notes for Interac transactions:

*Card type should be "P" for Interac. -> That may only be for returned data.
Data to display in receipt:
	 	Amount - (charge_total)
		Transaction Type - (trans_name)
		Date and Time - (date_stamp & time_stamp)
		Authorisation Code - (bank_approval_code)
		Response Code - (response_code)
		ISO Code - (iso_code)
		Response Message - (message)
		Reference Number - (bank_transaction_id)
		Goods and Services Order - (description of the products / services ordered)
		Merchant Name - (Your Business Name – should be same as what you registered with
		Moneris Solutions)
		Merchant URL - (Your business website)
		Cardholder Name - (cardholder – not required for INTERAC Online)
		Issuer Name (ISSNAME) – required only for INTERAC Online transactions
		Issuer Confirmation (ISSCONF) – required only for INTERAC Online transactions


1- Payment confirmation should be done within 30 minutes of pre-authorization.
2- Payment is authorized when AXCSYS does a post-back to our site.
   -If the post back is to the "NOT FUNDED" url, this means the payment has failed. Details included in POST.
   -If the post back is to the "FUNDED" url, this means the payment has succeeded. Details included in POST.
3- After the post back, the system should confirm the payment using the moneris API.
4- Data to send to moneris may look like this: cc_num=”3728024906540591206=01121122334455000
5- Basically: cc_num="%(cardnum)s=%(idebit_track2)s" % (card_number, IDEBIT_TRACK2) the latter being part of the POST data sent back from payment gateway.

==========
Beanstream:
==========
https://www.beanstream.com/scripts/process_transaction.asp?

P: Purchase - One time transaction
Request:
{
    'merchant_id': '123456789',
    'requestType': 'BACKEND',
    'trnType': 'P',
    'trnOrderNumber': '1234TEST',
    'trnAmount': '5.00',
    'trnCardOwner': 'Joe+Test',
    'trnCardNumber': '4030000010001234',
    'trnExpMonth': '10',
    'trnExpYear': '10',
    'ordName': 'Joe+Test',
    'ordAddress1': '123+Test+Street',
    'ordCity': 'Victoria',
    'ordProvince': 'BC',
    'ordCountry': 'CA',
    'ordPostalCode': 'V8T2E7',
    'ordPhoneNumber': '5555555555',
    'ordEmailAddress': 'joe%40testemail.com',
}
Response:
{'authCode': ['TEST'],
 'avsAddrMatch': ['0'],
 'avsId': ['0'],
 'avsMessage': ['Address Verification not performed for this transaction.'],
 'avsPostalMatch': ['0'],
 'avsProcessed': ['0'],
 'avsResult': ['0'],
 'cardType': ['VI'],
 'errorType': ['N'],
 'messageId': ['1'],

 'messageText': ['Approved'],
 'paymentMethod': ['CC'],
 'responseType': ['T'],
  'trnAmount': ['5.00'],
 'trnApproved': ['1'],
 'trnDate': ['7/31/2009 11:57:12 AM'],
 'trnId': ['10001364'],
 'trnOrderNumber': ['1234TEST'],
 'trnType': ['P']}

PA: Pre-Authorization
Request:
{'merchant_id': ['123456789'],
 'ordAddress1': ['123 Test Street'],
 'ordCity': ['Victoria'],
 'ordCountry': ['CA'],
 'ordEmailAddress': ['joe@testemail.com'],
 'ordName': ['Joe Test'],
 'ordPhoneNumber': ['5555555555'],
 'ordPostalCode': ['V8T2E7'],
 'ordProvince': ['BC'],
 'paymentMethod': ['CC'],
 'requestType': ['BACKEND'],
 'trnAmount': ['5.00'],
 'trnCardNumber': ['4030000010001234'],
 'trnCardOwner': ['Joe Test'],
 'trnExpMonth': ['10'],
 'trnExpYear': ['10'],
 'trnOrderNumber': ['1234TEST'],
 'trnType': ['PA']}
Response:
{'authCode': ['TEST'],
 'avsAddrMatch': ['0'],
 'avsId': ['0'],
 'avsMessage': ['Address Verification not performed for this transaction.'],
 'avsPostalMatch': ['0'],
 'avsProcessed': ['0'],
 'avsResult': ['0'],
 'cardType': ['VI'],
 'errorType': ['N'],
 'messageId': ['1'],
 'messageText': ['Approved'],
 'paymentMethod': ['CC'],
 'responseType': ['T'],
 'trnAmount': ['5.00'],
 'trnApproved': ['1'],
 'trnDate': ['7/31/2009 11:57:12 AM'],
 'trnId': ['10001364'],
 'trnOrderNumber': ['1234TEST'],
 'trnType': ['P']}


PAC: Payment Authorization Capture (It's actually an adjustment)
Request:
{'adjId': ['10002115'], # References a trnId
 'merchant_id': ['123456789'],
 'password': ['pass1234'],
 'requestType': ['BACKEND'],
 'trnAmount': ['1.00'],
 'trnOrderNumber': ['1234'],
 'trnType': ['R'],
 'username': ['user1234']}
Response:
{'authCode': ['TEST'],
 'avsAddrMatch': ['0'],
 'avsId': ['0'],
 'avsMessage': ['Address Verification not performed for this transaction.'],
 'avsPostalMatch': ['0'],
 'avsProcessed': ['0'],
 'avsResult': ['0'],
 'cardType': ['VI'],
 'errorType': ['N'],
 'messageId': ['1'],
 'messageText': ['Approved'],
 'paymentMethod': ['CC'],
 'responseType': ['T'],
 'trnAmount': ['1.00'],
 'trnApproved': ['1'],
 'trnDate': ['8/17/2009 1:44:56 PM'],
 'trnId': ['10002118'],
 'trnOrderNumber': ['1234R'],
 'trnType': ['R']}

Cancellation: Cancellation (It's actually an adjustment), avail for
Canada VISA or TD Visa merchant accounts
Do a PAC with trnAmount set to 0.00

Refund:
All adjustment, can be of type:
R (Return) or VP (Void Purchase)
*Will only be approved on same-day <=11:59PMEST
*Refund Can do a full or partial refund, use trnAmount
*Void is removal of entire amount, I think it also needs trnAmount

=======
moneris
=======
... works similarly, When making a completion (capture), you need to
specify a transaction ID, order_id and an amount.
"""

