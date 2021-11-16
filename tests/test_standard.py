# https://realpython.com/python-testing/
# https://mattsegal.dev/pytest-on-github-actions.html


from Products.zms import standard


def test_encrypt_password():
	sha1_v = '40bd001563085fc35165329ea1ff5c5ecbdbbeef'
	assert standard.encrypt_password(pw='123', algorithm='sha1',hex=True) == sha1_v, 'SHA1-Hash not correct'

if __name__ == "__main__":
	test_encrypt_password()
	print('Passed')