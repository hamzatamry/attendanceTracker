#   pip3 install firebase_admin
import firebase_admin
from firebase_admin import db

cred_obj = firebase_admin.credentials.Certificate('attendancetracker-5e615-firebase-adminsdk-gk4m6-ffc1325573.json')
default_app = firebase_admin.initialize_app(cred_obj, {
	'databaseURL':'https://attendancetracker-5e615-default-rtdb.europe-west1.firebasedatabase.app'
	})

db = db.reference("/places")

db_places = db.get()

places = [
	{
		'idPlace': 1,
		'estOccupee': True
	},
	{
		'idPlace': 2,
		'estOccupee': False
	},
	{
		'idPlace': 3,
		'estOccupee': False
	},
]

"""
for key, value in db_places.items():
	for place in places:
		if value['idPlace'] == place['idPlace']:
			db.child(key).update({'estOccupee': place['estOccupee']})
"""

bus_num = 3
keys = list(db_places.keys())
values = [value['idEtudiant'] for value in db_places.values()]
db.child(keys[values.index(bus_num)]).update({})



