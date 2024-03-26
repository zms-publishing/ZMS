from PIL import Image, ImageDraw, ImageFont
import hashlib
import random
from datetime import datetime, timedelta
import json
import base64
from io import BytesIO

# GLOBAL CONSTANTS
secret_key='uiwe#sdfj$%sdfj'
life_time=120
font_path = "/usr/share/fonts/truetype/freefont/DejaVuSansMono-Bold.ttf"

# HELPER FUNCTIONS
# [1] Create an image object from a given text of 4 digits
def create_image(text):
	# create an image with the given text
	image = Image.new("RGB", (100, 38), (0, 0, 0))
	# create a drawing object
	draw = ImageDraw.Draw(image)
	# set the font of the text
	font = ImageFont.truetype(font_path, 36)
	# draw the text on the image
	draw.text((5, -3), text, font=font, fill=(255, 255, 255))
	# draw.line((0,8, 100,30), fill=(0,0,0), width=3)
	# draw.line((0,30, 80,0), fill=(255,255,255), width=3)
	# create a BytesIO object
	buffered = BytesIO()
	# save image to the BytesIO object
	image.save(buffered, format="PNG")
	# get the value of the BytesIO object
	image_bytes = buffered.getvalue()
	image_str = base64.b64encode(image_bytes).decode("utf-8")
	# return data_uri
	return f"data:image/png;base64,{image_str}"


# [2] Create hash of a given string
def encrypt_password(pw, algorithm='sha256', hex=False):
	algorithm = algorithm.lower()
	algorithm = algorithm=='sha-1' and 'sha1' or algorithm
	enc = None
	if algorithm in list(hashlib.algorithms_available):
		h = hashlib.new(algorithm)
		h.update(pw.encode())
		if hex:
			enc = h.hexdigest()
		else:
			enc = h.digest()
	return enc

# #############################
# MAIN FUNCTIONS
# ##############################
# [A] Create Captcha with global constants:
#	@secret_key
#	@life_time
def captcha_create(secret_key='uiwe#sdfj$%sdfj', life_time=600):
	# generate a random string
	captcha_str = str(random.randint(1000, 9999))
	# create a timestamp
	timestamp_create = int(datetime.timestamp(datetime.now()) * 1000)
	# create a crypto signature from the secret key and the captcha string
	signature = encrypt_password(secret_key + captcha_str + str(timestamp_create), 'sha256', True)
	# create captcha image as data-uri
	captcha_data_uri = create_image(captcha_str)

	# create a dictionary to store the captcha data
	captcha_dict = {
		'signature': signature,					# Used to validate the captcha
		# '_captcha_str': captcha_str, 			# Private: to be entered by the user
		'timestamp_create': timestamp_create,	# Used to validate the lifetime
		'life_time': life_time, 				# Needed to refresh the captcha after this time
		'captcha_data_uri': captcha_data_uri 	# Used to display the captcha image
	}
	return captcha_dict

# [B] Validate Captcha:
#	@signature: the public signature of the captcha
#	@secret_key: the secret key of the captcha
#	@captcha_str: the captcha string entered by the user
#	@timestamp_create: the timestamp when the captcha was created
#	@life_time: the life time of the captcha
def captcha_validate(signature, secret_key, captcha_str, timestamp_create, life_time):
	dt_create = datetime.utcfromtimestamp(float(timestamp_create) / 1e3)
	dt_receive = datetime.utcfromtimestamp((datetime.timestamp(datetime.now()) * 1000) / 1e3)
	is_intime = (dt_receive - dt_create).total_seconds() < life_time
	is_valid = signature == encrypt_password(secret_key + str(captcha_str) + str(timestamp_create), 'sha256', True)
	return is_intime and is_valid

# ##############################
# ZOPE-API-CALL captcha(create|validate)
# ##############################
def captcha_func(self, do):
	request = self.REQUEST
	if do == 'create':
		# Create a captcha
		captcha_data = captcha_create(secret_key, life_time)
		# Create a JSON object from the captcha_dict
		captcha_data_json = json.dumps(captcha_data, indent=4)
		# Send the captcha_data_json to the client
		return captcha_data_json
	elif do == 'validate':
		req_data = {}
		# Get the relevant captcha data from the client request
		for k in ['signature','captcha_str','timestamp_create']:
			req_data[k] = request.get(k,0)
		# Validate the captcha data
		captcha_is_valid = captcha_validate(req_data.get('signature'), secret_key, req_data.get('captcha_str'), req_data.get('timestamp_create'), life_time)
		return captcha_is_valid and json.dumps({'captcha_is_valid':True}) or json.dumps({'captcha_is_valid':False})
v