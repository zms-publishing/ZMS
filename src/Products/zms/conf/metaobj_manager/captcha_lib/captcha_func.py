from PIL import Image, ImageDraw, ImageFont
import hashlib
import random
from datetime import datetime, timedelta
import json
import base64
from io import BytesIO

# #############################################
# GLOBALS: DEFAULT PARAMETERS
# Overwritten by correponding ZMS Conf Property
# #############################################
# ZMS.captcha.secret_key
secret_key='uiwe#sdfj$%sdfj'
# ZMS.captcha.life_time
life_time=120
# ZMS.captcha.font_path
font_path = "/usr/share/fonts/dejavu/DejaVuSansMono-Bold.ttf" 
# ZMS.captcha.log_path
log_path = "/tmp/zms_captcha.log"

#############################################
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
	enc = None
	if algorithm in list(hashlib.algorithms_available):
		h = hashlib.new(algorithm)
		h.update(pw.encode())
		if hex:
			enc = h.hexdigest()
		else:
			enc = h.digest()
	return enc

# [3] Write captcha data to a file
# 	- add the new captcha string to the log list
# 	- return True if the captcha is new to the list and can be added
# 	- return False if the captcha was used before and could not be added
def write_captcha_data(captcha_str, file_path):
	was_used = True
	with open(file_path, 'r') as file_read:
		l = [line.strip() for line in file_read.readlines()]  # remove line breaks
		if captcha_str not in l:
			# add the new captcha to the list
			l.append(captcha_str)
			with open(file_path, 'w') as file_write:
				file_write.write('\n'.join(l))
			was_used = False
	return not(was_used)

# [4] Read captcha data from a file
def read_captcha_data(file_path):
	l = []
	try:
		with open(file_path, 'r') as file:
			l = [int(line.strip()) for line in file.readlines()]  # remove line breaks
		# keep only the last 100 entries
		if len(l) > 100:
			l = l[-100:]
			with open(file_path, 'w') as file:
				file.write('\n'.join([str(i) for i in l]))
		return l
	except FileNotFoundError:
		with open(file_path, 'w') as file:
			file.write('')
		return l

# [5] Exclude the logged list of numbers from a random number generator
def randint_exclude(start, end, exclude):
	while True:
		rand_num = random.randint(start, end)
		if rand_num not in exclude:
			return rand_num

# #############################################
# MAIN FUNCTIONS
# #############################################
# [A] Create Captcha with global constants:
#	@secret_key
#	@life_time
def captcha_create(secret_key='uiwe#sdfj$%sdfj', life_time=600):
	# Generate a random string that is not in the log file
	l = read_captcha_data(log_path)
	captcha_str = str(randint_exclude(1000, 9999, l))
	# Create a timestamp
	timestamp_create = int(datetime.timestamp(datetime.now()) * 1000)
	# Create a signature key from the secret key, captcha string and timestamp
	signature = encrypt_password(secret_key + captcha_str + str(timestamp_create), 'sha256', True)
	# Create captcha image as data-uri
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
#	@submitted: the flag whether the captcha was submitted or just validated by async by the client
def captcha_validate(signature, secret_key, captcha_str, timestamp_create, life_time, submitted):
	dt_create = datetime.utcfromtimestamp(float(timestamp_create) / 1e3)
	dt_receive = datetime.utcfromtimestamp((datetime.timestamp(datetime.now()) * 1000) / 1e3)
	is_intime = (dt_receive - dt_create).total_seconds() < int(life_time)
	is_valid = signature == encrypt_password(secret_key + str(captcha_str) + str(timestamp_create), 'sha256', True)
	if is_intime and is_valid:
		if submitted:
			# check whether captcha_str can be added as a new item to log file
			# means it was not used before
			if write_captcha_data(captcha_str, log_path):
				return True
			else:
				return False
		else:
			return True
	else:
		return False

# #############################################
# ZOPE-API-CALL captcha(create|validate)
# #############################################
def captcha_func(self, do):
	request = self.REQUEST

	# Getting/setting global parameters
	global secret_key
	global life_time
	global font_path
	global log_path
	secret_key = self.content.getConfProperty('ZMS.captcha.secret_key') or secret_key
	life_time = self.content.getConfProperty('ZMS.captcha.life_time') or life_time
	font_path = self.content.getConfProperty('ZMS.captcha.font_path') or font_path
	log_path = self.content.getConfProperty('ZMS.captcha.log_path') or log_path

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
		for k in ['signature','captcha_str','timestamp_create','submitted']:
			req_data[k] = request.get(k,0)
		# Validate the captcha data
		captcha_is_valid = captcha_validate(req_data.get('signature'), secret_key, req_data.get('captcha_str'), req_data.get('timestamp_create'), life_time, req_data.get('submitted'))
		return captcha_is_valid and json.dumps({'captcha_is_valid':True}) or json.dumps({'captcha_is_valid':False})
