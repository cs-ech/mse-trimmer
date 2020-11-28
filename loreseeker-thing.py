import zipfile, os, sys
import regex as re
def main():
	script, set_path = sys.argv	
#	set_path=input("Enter the path to the .mse-set file you want trimmed: ")
	try:
		set_archive=zipfile.ZipFile(set_path,"r",zipfile.ZIP_DEFLATED)
		print("Opened "+set_path+".")
	except:
		print("This file doesn\'t exist, try again.")
		main()
	else:	
		try:
			set_archive.extract("set")
		except:
			print("This file isn\'t a valid set file.")
			main()
		else:
			set_file=open("set","r",encoding="utf-8-sig")
			set_str=set_file.read()
			set_file.close()
			os.remove("set")
			mega_pattern=re.compile(r"ard:(?:\n\tstylesheet: (.*?))?\n.*?\n\tnotes:.(.*?)\n\ttime created: (.*?)\n\ttime modified: (.*?)\n.*?\n\timage: (.*?)\n.*?(?:[^(?:flavor|card code)]*? text:(.*?)\n\t\w.*?)(?:age 2: (.*?)\n).*?mainframe image 2|\nstyling:\n(.*?)\nc|(keyword:\n.*?mode:.*?)\n|\bstylesheet: (.*?)\n|game: (.*?)\n",flags=re.DOTALL)
			rt_pattern=re.compile(r"<kw-[aA]>.*?<nospellcheck>(.*?)</nospellcheck>.*?</kw-[aA]>",flags=re.DOTALL)
			kw_pattern=re.compile(r"\tkeyword:.*?\n\tmatch: (.*?)\n",flags=re.DOTALL)
			style_pattern=re.compile(r"[^\t]?\t(\w.*?):\n.*?overlay:.*?(?:\n|$)",flags=re.DOTALL)
			anti_tag_pattern=re.compile(r"<(.*?param.*?)>.*?</\1>")
			note_cmd_pattern=re.compile(r"(?:^|\t\t)([^!\t].*?)(?:\n|$)")
			used_kw_set=set([])
			defined_kw_dict={}
			img_set=set([])
			used_style_set=set([])
			defined_style_dict={}
			to_delete=[]
			to_genericize=[]
			for fi in re.finditer(mega_pattern,set_str):
				for i in range(1,12):
					if fi.group(i):
						if i==1:
							used_style_set.add(fi.group(i))
						elif i==2:
							for noteline in re.finditer(note_cmd_pattern,fi.group(i)):
								to_delete.append((fi.start(i)+noteline.start(1),fi.start(i)+noteline.end(1)-1))
						elif i in [3,4]:
							to_genericize.append((fi.start(i),fi.end(i)-1))
						elif i in [5,7]:
							img_set.add(fi.group(i))
						elif i==6:
							for cap in fi.captures(i):
								for kw in re.finditer(rt_pattern,cap):
									used_kw_set.add(re.sub(anti_tag_pattern,"?",kw.group(1).lower()))
						elif i==8:
							for style in re.finditer(game_style_pattern,fi.group(i)):
								defined_style_dict[style.group(1)]=(fi.start(i)+style.start(),fi.start(i)+style.end()-1)
						elif i==9:
							defined_kw_dict[re.sub(anti_tag_pattern,"?",re.search(kw_pattern,fi.group(i)).group(1)).lower()]=fi.span(i)
						elif i==10:
							used_style_set.add(fi.group(i))
						elif i==11:
							game_style_pattern=re.compile(r"[^\t]?\t"+fi.group(i)+r"-(.*?):\n.*?overlay:.*?(?:\n|$)",flags=re.DOTALL)
			unused_kw_set=set([item for item in list(defined_kw_dict.keys()) if item not in used_kw_set])
			unused_style_set=set([item for item in list(defined_style_dict.keys()) if item not in used_style_set])
			used_img_set=set([item for item in set_archive.namelist() if item in img_set])
			for unused_style in unused_style_set:
				to_delete.append(defined_style_dict[unused_style])
			for unused_kw in unused_kw_set:
				to_delete.append(defined_kw_dict[unused_kw])
			to_genericize=sorted(to_genericize, key=lambda x: x[1], reverse=True)
			for tg in to_genericize:
				set_str = set_str[0: tg[0]:] + "1970-01-01 00:00:00" + set_str[tg[1] + 1::]
			to_delete=sorted(to_delete, key=lambda x: x[1], reverse=True)
			for td in to_delete:
				set_str = set_str[0: td[0]:] + set_str[td[1] + 1::]
			trimmed_path=set_path.replace(".mse-set","-trimmed.mse-set")
			output_archive=zipfile.ZipFile(trimmed_path,"w",zipfile.ZIP_DEFLATED)
			for file in set_archive.namelist():
				if file in used_img_set or re.fullmatch(re.compile(r".*\.mse-symbol"),file):
					set_archive.extract(file)
					output_archive.write(file)
					os.remove(file)
			output_archive.writestr("set",set_str)
			set_archive.close()
			output_archive.close()
			print("Finished as "+trimmed_path+".")
#			if input("More (Y/N)? ").lower() == "y":
#				main()
main()