#!/usr/bin/python3
print("importing libs")
import os,sys
import json
import imaplib,email
#from io import BytesIO
#TODO: change from temp file to BytesIO once the Piwigo lib supports it (Issue is already filed)
from time import sleep
from piwigo import Piwigo
import re

print("loading config")
curdir=os.path.abspath(os.path.dirname(__file__))
os.chdir(curdir)
with open("./conf.json","r") as f:
	CONFIG=json.load(f)
MAILDATA=CONFIG["maildata"]
PIWIDATA=CONFIG["piwigo"]
WAIT=CONFIG["wait"]
tagexp=re.compile("tags=\\[,?(([^\\],]+,?)+)\\]")#regexp for finding and parsing tags - check at regex101.com
#valid:
#	tags=[a,b,c,d] → produces the tags 'a','b','c','d'
#	tags=[ ,ab,a b,c,] → produces the tags 'ab','a b','c'
#	tags=[a] → produces the tags 'a'
#invalid:
#	tags=[,] → doesn't get cought
#	tags=[] → doesn't get cought
#	tags=[a,b,c,,d] → doesn't get cought
#	tags = [a,b,c,d] → doesn't get cought
#	[a,b,c,d] → doesn't get cought

def get_text(msg):#i have no idea why, but this is the only way, where there are no decoding errors present.
	if msg.is_multipart():
		return get_text(msg.get_payload(0))
	else:
		return msg.get_payload(None,decode=True)

print("connecting to piwigo server")
piwi=Piwigo(PIWIDATA["serv"])
piwi.pwg.session.login(username=PIWIDATA["usr"],password=PIWIDATA["pass"])
print("connecting to mailserver")
sess=imaplib.IMAP4_SSL(MAILDATA["serv"],MAILDATA["port"])
sess.login(MAILDATA["usr"],MAILDATA["pass"])
sess.select("INBOX")
try:
	while True:
		print("getting mail")
		retcode,data=sess.search(None,"(UNSEEN)")
		if retcode=="OK":
			for num in data[0].split():
				print("Processing mail '%s'"%num.decode())
				typ,data=sess.fetch(num,"(RFC822)")
				body=data[0][1]
				mail=email.message_from_bytes(body)
				body=get_text(mail).decode("utf-8")
				print("Got mail from %s with subject '%s'"%(mail["From"],mail["Subject"]))
				expsearch=tagexp.search(body)
				if '-v' in sys.argv:
					print("Body:",body,sep="\n")
				if expsearch:#if regex matched
					tags=[tag.strip() for tag in expsearch.group(1).split(",")]#split tags with , and remove trailing or leading spaces
					tags=[tag for tag in tags if len(tag)>0]#removes all empty tags
				else:
					tags=[]
				print("tags=%s"%tags)
				try:
					sess.store(num,"+FLAGS","\\Seen")
				except:
					print("Couldn't mark mail as seen")
				else:
					if mail.get_content_maintype()!="multipart":#if no attachment is present
						print("No attachments")
						continue
					else:
						for part in mail.walk():
							if part.get_content_maintype()=="multipart" or part.get("Content-Disposition")==None:
								continue
							else:
								fn=part.get_filename()
								ext=os.path.splitext(fn)[-1].lower()
								if ext in (".jpg",".jpeg",".png",".gif"):
									print("sending image %s"%fn)
									fp=os.path.join("./.tmp",fn)#ensure nothing gets overwritten by putting it into hidden tmp folder
									img=part.get_payload(decode=True)
									with open(fp,"wb+") as f:
										f.write(img)
									piwi.pwg.images.addSimple(image=fp,tags=tags,category=PIWIDATA["categoryid"])
									os.remove(fp)
								else:
									print("invalid filetype: %s"%fn)
		else:
			print("Error while polling mail: \033[41m%s\033[0m"%retcode)
		try:
			for i in range(WAIT,0,-1):
				print("\rTrying again in %i minutes"%i,end="")
				sleep(60)
		except KeyboardInterrupt:
			c=input("\nContinue? y/n\n")[0].lower()
			if c in ("y","j"):
				pass
			else:
				print("bye")
				break
		else:
			print(end="\r\033[2K")
finally:
	sess.logout()
	piwi.pwg.session.logout()
