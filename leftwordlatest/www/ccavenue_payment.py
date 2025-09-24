import frappe
import base64
from hashlib import md5
from Crypto.Cipher import AES
from Crypto import Random
from string import Template
import requests
import json
from Crypto.Random import get_random_bytes
no_cache = 1
def get_context(context):
	context.no_cache = True
	ccavenue = frappe.get_doc("CCAvenue Settings")
	workingKey = ccavenue.working_key
	access_code = ccavenue.access_code
	p_merchant_id = ccavenue.merchant_id
	p_order_id = frappe.form_dict.order_id
	p_currency = frappe.form_dict.currency
	p_amount = frappe.form_dict.amount
	p_language = "EN"
	p_redirect_url = ccavenue.redirect_url + "?token={0}".format(frappe.form_dict.token_id)
	p_cancel_url = "https://leftword.com/ccavenue_cancel"
	p_billing_name = frappe.session.user
	p_billing_email = frappe.session.user
	p_billing_address = frappe.for_dict.street
	p_billing_city = frappe.form_dict.town
	p_billing_state = frappe.form_dict.state
	p_billing_zip = frappe.form_dict.zipcode
	p_billing_country = "India"
	p_billing_tel = frappe.form_dict.phone
	p_delivery_name = "Sam"
	p_delivery_address = "Vile Parle"
	p_delivery_city = "Mumbai"
	p_delivery_state ="Maharashtra"
	p_delivery_zip = "400038"
	p_delivery_country = "India"
	p_delivery_tel = "0221234321"
	p_merchant_param1 = "additional Info."
	p_merchant_param2 = "additional Info."
	p_merchant_param3 = "additional Info."
	p_merchant_param4 = "additional Info."
	p_merchant_param5 = "additional Info."
	p_promo_code = ""
	p_customer_identifier = ""
	merchant_data='merchant_id='+p_merchant_id+'&'+'order_id='+p_order_id + '&' + "currency=" + p_currency + '&' + 'amount=' + p_amount+'&'+'redirect_url='+p_redirect_url+'&'+'cancel_url='+p_cancel_url+'&'+'language='+p_language+'&'+'billing_name='+p_billing_name+'&'+'billing_email='+p_billing_email+'&'+'billing_address='+p_billing_address+'&'+'billing_city='+p_billing_city+'&'+'billing_state='+p_billing_state+'&'+'billing_zip='+p_billing_zip+'&'+'billing_country='+p_billing_country+'&'+'billing_tel='+p_billing_tel+'&'
	# merchant_data='merchant_id='+p_merchant_id+'&'+'order_id='+p_order_id + '&' + "currency=" + p_currency + '&' + 'amount=' + p_amount+'&'+'redirect_url='+p_redirect_url+'&'+'cancel_url='+p_cancel_url+'&'+'language='+p_language+'&'+'billing_name='+p_billing_name+'&'+'billing_address='+p_billing_address+'&'+'billing_city='+p_billing_city+'&'+'billing_state='+p_billing_state+'&'+'billing_zip='+p_billing_zip+'&'+'billing_country='+p_billing_country+'&'+'billing_tel='+p_billing_tel+'&'+'billing_email='+p_billing_email+'&'+'delivery_name='+p_delivery_name+'&'+'delivery_address='+p_delivery_address+'&'+'delivery_city='+p_delivery_city+'&'+'delivery_state='+p_delivery_state+'&'+'delivery_zip='+p_delivery_zip+'&'+'delivery_country='+p_delivery_country+'&'+'delivery_tel='+p_delivery_tel+'&'+'merchant_param1='+p_merchant_param1+'&'+'merchant_param2='+p_merchant_param2+'&'+'merchant_param3='+p_merchant_param3+'&'+'merchant_param4='+p_merchant_param4+'&'+'merchant_param5='+p_merchant_param5+'&'+'promo_code='+p_promo_code+'&'+'customer_identifier='+p_customer_identifier+'&'
	# merchant_data = 'merchant_id=' + p_merchant_id + '&order_id=' + p_order_id + "&currency=" + p_currency + '&amount=' + p_amount + '&redirect_url=' + p_redirect_url+ '&cancel_url=' + p_cancel_url + '&language='+p_language+'&'
	encryption = encrypt(merchant_data,workingKey)
	context.access_code = access_code
	context.merchant_id = p_merchant_id
	context.workingKey = workingKey
	context.encRequest = encryption


def encrypt(plainText,workingKey):
	iv = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
	plainText = pad(plainText)
	encDigest = md5(workingKey.encode())
	enc_cipher = AES.new(encDigest.digest(), AES.MODE_CBC, iv)
	encryptedText = enc_cipher.encrypt(plainText).hex()
	return encryptedText

@frappe.whitelist()
def decrypt(cipherText,workingKey):
    iv = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
    decDigest = md5(workingKey.encode())
    encryptedText = bytes.fromhex(cipherText)
    dec_cipher = AES.new(decDigest.digest(), AES.MODE_CBC, iv)
    decryptedText = dec_cipher.decrypt(encryptedText)
    return decryptedText.decode('utf-8')

def pad(data):
	length = 16 - (len(data) % 16)
	data += chr(length)*length
	return data.encode('utf-8')

@frappe.whitelist()
def payment_redirect(resp=None):
	callback_data = frappe.request.get_data(as_text=True)
	login_data = {
		'usr': "Administrator",
		'pwd': "Admin@fc2022"
	}
	login = requests.post("https://dev.lawbazar.com" + '/api/method/login', json=login_data)
	header = {
		"full_name":login.cookies.get('full_name'),
		"sid":login.cookies.get('sid'),
		"system_user":login.cookies.get('system_user'),
		"user_id":login.cookies.get('user_id'),
		"user_image":login.cookies.get('user_image'),
		"Cookie":f"""full_name={login.cookies.get('full_name')};sid={login.cookies.get('sid')};system_user={login.cookies.get('system_user')};user_id={login.cookies.get('user_id')};user_image={login.cookies.get('user_image')}"""
	}
	resp = requests.post("https://dev.lawbazar.com" + '/api/method/frappe.auth.get_logged_user', headers=header)
	# frappe.local.response["resp"] = resp
	frappe.local.response["full_name"] = login.cookies.get('full_name')
	frappe.local.response["sid"] = login.cookies.get('sid')
	frappe.local.response["system_user"] = login.cookies.get('system_user')
	frappe.local.response["user_id"] = login.cookies.get('user_id')
	frappe.local.response["user_image"] = login.cookies.get('user_image')
	frappe.local.response["callback_data"] = resp.cookies.get("user_id")
