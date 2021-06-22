import pyrebase
import os
import glob

config = {
'apiKey': "AIzaSyAKOB4wJmHgMWEC6DxYbjkWMCaAHKgKTkw",
'authDomain': "imageset-ds-upe.firebaseapp.com",
"databaseURL": "https://imageset-ds-upe.firebaseio.com",
'projectId': "imageset-ds-upe",
'storageBucket': "imageset-ds-upe.appspot.com",
'messagingSenderId': "965093506402",
'appId': "1:965093506402:web:bc3f21b8b980e26f66c03b",
'measurementId': "G-J6H57Y366K"
}
path = "/USBDRIVE/"

config["serviceAccount"] = "serviceAccountCredentials.json"

firebase = pyrebase.initialize_app(config)
storage = firebase.storage()
db = firebase.database()

if (os.path.ismount('/USBDRIVE/')):
  print('PenDrive OK')
else:
  print('PenDrive não foi encontrado')
    
ArquivosBanco = []
for blob in list(storage.list_files()):
    ArquivosBanco.append(blob.name)
print(len(ArquivosBanco), " Arquivos no banco")

ArquivosLocal = []
for filename in glob.iglob(path+'**/*.png',recursive = True):
    ArquivosLocal.append(filename[len(path):].replace("\\","/"))

print(len(ArquivosLocal), " Arquivos no PenDrive")
    
ArquivosFaltando = [item for item in ArquivosLocal if item not in ArquivosBanco]

config = {
'apiKey': "AIzaSyAKOB4wJmHgMWEC6DxYbjkWMCaAHKgKTkw",
'authDomain': "imageset-ds-upe.firebaseapp.com",
"databaseURL": "https://imageset-ds-upe.firebaseio.com",
'projectId': "imageset-ds-upe",
'storageBucket': "imageset-ds-upe.appspot.com",
'messagingSenderId': "965093506402",
'appId': "1:965093506402:web:bc3f21b8b980e26f66c03b",
'measurementId': "G-J6H57Y366K"
}

firebase = pyrebase.initialize_app(config)
storage = firebase.storage()
db = firebase.database()

NArquivos = len(ArquivosFaltando)
print(str(NArquivos)+" arquivos para serem carregados")
for i,Arquivo in enumerate(ArquivosFaltando):
    print("Carregando: "+str(round(((i+1)/NArquivos)*100,2))+" %")
    storage.child(Arquivo).put(path+Arquivo)
