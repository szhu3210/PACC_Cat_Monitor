#!/usr/bin/env python
from bs4 import BeautifulSoup as Soup
import urllib
import smtplib
import time
from email.Message import Message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


ADDR = 'YOUR EMAIL ADDRESS: e.g. abc@def.org'
FROMADDR = 'FROM ADDRESS: e.g. abc@def.org'
TOADDR_1 = 'TO ADDRESS: e.g. ghi@jkl.com'
TOADDR_2 = 'ANOTHER TO ADDRESS: e.g. mno@pqr.edu'
USERNAME = 'YOUR EMAIL ACCOUNT'
PASSWORD = 'YOUR EMAIL PASSWORD'
SERVER_ADDRESS = 'EMAIL SERVER ADDRESS: e.g. smtp.gmail.com:587'


class CatMonitor():

	def __init__(self):
		self.selected_info_old = []
		self.selected_cats_old = []
		self.url = 'http://petharbor.com/results.asp?searchtype=ADOPT&start=4&stylesheet=include/default.css&frontdoor=1&grid=1&friends=1&samaritans=1&nosuccess=0&orderby=Age&rows=128&imght=120&imgres=thumb&tWidth=200&view=sysadm.v_animal&nomax=1&fontface=arial&fontsize=10&zip=85745&miles=50&shelterlist=%27PIMA%27&atype=cat&where=type_CAT&NewOrderBy=Age&PAGE=1'
		self.start()

	def get_cats(self):
		soup = Soup(urllib.urlopen(self.url), "html.parser")
		cats = soup.find_all('div', class_="gridResult")
		# print cats[0]
		selected_cats = []
		selected_info = []
		for cat in cats:
			acat = [attr.text for attr in cat.find_all('div')]
			if len(acat)<7:
				raise 'Cat info error! Not enough information.'
			color = acat[2]
			# print color
			age = acat[4]
			# print age
			favored_colors = ['orange', 'cream', 'org', 'crm']
			if any([clr in color.lower() for clr in favored_colors]): # check color
				if len(age)>=24 and age[:2]=='00' and int(age[8:10])<5: # check age
					selected_info.append(acat)
					selected_cats.append(cat)
		# for info in selected_info:
		# 	print info
		return selected_info, selected_cats

	def find_new(self, selected_cats):
		return list(set(selected_cats)-set(self.selected_cats_old))
		
	def gen_message(self, selected_info, selected_cats):

		if selected_info == self.selected_info_old:
			res = 'No update.'
			signal = 0
		else:
			res = 'New selected cats found!\n\nLink:\n' + self.url +'\n\nNew cats:\n' 
			
			new_cats = self.find_new(selected_cats)
			for i,new_cat in enumerate(new_cats):
				res += '%5s. ' % str(i+1) + str(new_cat.div.text) + '\n'

			signal = 1
			self.selected_info_old = selected_info
			self.selected_cats_old = selected_cats

		return res, signal

	def start(self):
		while 1:

			print 'Get cats... (' + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + ')'
			selected_info, selected_cats = self.get_cats()
			# try:
			# 	selected_info, selected_cats = self.get_cats()
			# except:
			# 	print 'Get cats failed! Retry in 10 seconds.'
			# 	time.sleep(10)
			# 	continue
			current = 'Current selected cats: \n'
			for info in selected_info:
				p = []
				for i, element in enumerate(info):
					p.append((('%20s' % element) if not i else element) + '  \t')
				current += ''.join(p) + '\n'
			print current

			message, signal = self.gen_message(selected_info, selected_cats)

			if signal == 1:
				print 'Sending email...'
				self.send_email("New cat(s) found!", message + '\n' + current)
				# try:
				# 	self.send_email("New cat(s) found!", message)
				# 	print "Email sent successfully!"
				# except:
				# 	print "Email not sent!"
			else:
				print 'No need to send email.'

			time.sleep(3600)

	def send_email(self, title, message):

		addr = ADDR
		fromaddr = FROMADDR
		toaddrs  = [TOADDR_1, TOADDR_2]

		username = USERNAME
		password = PASSWORD

		server = smtplib.SMTP(SERVER_ADDRESS)
		server.starttls()
		server.ehlo()
		server.login(username,password)

		msg = MIMEMultipart('alternative')

		m = Message()
		m['From'] = addr
		m['To'] = addr
		m['X-Priority'] = '1'
		m['Subject'] = title
		m.set_payload(message)

		server.sendmail(fromaddr, toaddrs, m.as_string())
		server.quit()


if __name__ == "__main__":
    # execute only if run as a script
    monitor = CatMonitor()
