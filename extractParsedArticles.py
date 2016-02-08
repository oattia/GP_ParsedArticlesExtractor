#!/usr/bin/python

import sys, getopt, os, subprocess, shutil
import mysql.connector #Need to be installed in linux
from subprocess import call

def main(argv):
	lang = ''
	ifile = ''
	try:
		opts, args = getopt.getopt(argv,"hl:i:",["lang=","ifile="])
	except getopt.GetoptError:
		print("separate.py -l <language>")
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print("separate.py -l <language>")
			sys.exit()
		elif opt in ("-l", "--lang"):
			lang = arg
		elif opt in ("-i", "--ifile"):
			ifile = arg

	print ('Lang is '+ lang)

	if not os.path.exists(lang):
		os.makedirs(lang)
    
	os.chdir(lang)

	#Split big file to an article-per-file files
	call(["csplit", "-s","-z","-n","11","-f",lang+"_","-b","%011d.txt","../"+ifile,"/#Article:/","{*}"])


	cnx = mysql.connector.connect(user='root', database='wikipedia')
	cursor = cnx.cursor()	


	query = ("SELECT id_"+lang+",title_"+lang+"  FROM en_ar_map")
	cursor.execute(query)
	rows = cursor.fetchall()
	
	cursor.close()
	cnx.close()
	map = dict()
	for row in rows:
		map[row[1].decode("utf-8")]=row[0]

	# print (map[25])
	#Rename Files 
	counter =0
	missed =0
	files=os.listdir(os.getcwd())
	files.sort()
	isZeroFile=0
	# print(type(files))
	for i in files:
		if isZeroFile==0:
			isZeroFile=1
			continue

		src=open(i, 'r')
		title=src.readline().rstrip()


		# proc = subprocess.check_output(["head","-1",i]).rstrip().decode("utf-8")
		# print(title)
		title = title.split(' ', 1)[1]
		# print(title)
		
		# call(["sed","-i","1s/.*/"+title+"/",i])
		# sed -i "1s/.*/$title/" $file
		 
		if title in map:
			ID=map[title]
			counter= counter+1
			target=open(lang+"_"+str(ID)+".txt", 'w')
			target.write(title+"\n")

			#check if secind line is #Type:
			second=src.readline().rstrip()
			splitted_second = second.split(' ', 1)[0]
			if splitted_second != "#Type:":
				target.write(second+"\n")
			##############################
			shutil.copyfileobj(src,target)
			target.close()
			os.remove(i)
			
		else:
			missed=missed+1
			# print(title+" Not Found")
	print("Articles Successfully done : "+str(counter)+"\nArticles not found : "+str(missed))
		

if __name__ == "__main__":
   main(sys.argv[1:])