import shutil
import os
print("This is for osu!stable.")
print("Enter your osu! Dictionary: ")
osuSrc = input()

if(osuSrc.endswith("/")):
	osuSrc = osuSrc[:len(osuSrc)-1]

if os.path.isdir(osuSrc+"/ExportSongs") == False:
	os.mkdir(os.path.join(osuSrc,"ExportSongs"))

for dirs in os.listdir(osuSrc + "/Songs/"):
	for r,d,f in os.walk(osuSrc + "/Songs/" + dirs):

		maps = []

		for i in f: #find every beatmap file
			if i.endswith(".osu"):
				print("Found "+ i )
				maps.append(i)

		musics = []

		for i in maps: #read every beatmap file and get the used music (since the folder can contain skins, storyboards etc.)
			file = open(osuSrc+"/Songs/"+dirs+"/"+i, mode="r", encoding="utf-8")
			while True:
				line = file.readline()
				if line.startswith("AudioFilename: "):
					musics.append(line[15:len(line)-1])
					break
			file.close()

		musics = list(set(musics)) #remove duplicate files

		for i in musics: #copy files
			try:
				print("Exporting "+osuSrc+"/Songs/"+dirs+"/"+i)
				shutil.copy(osuSrc+"/Songs/"+dirs+"/"+i,osuSrc+"/ExportSongs/"+i)
				os.rename(osuSrc+"/ExportSongs/"+i,osuSrc+"/ExportSongs/"+dirs+" - "+i)
			except:
				print("Unable to export "+osuSrc+"/Songs/"+dirs+"/"+i)