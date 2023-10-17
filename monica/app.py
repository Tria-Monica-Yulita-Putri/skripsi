from flask import Flask, render_template, request
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import joblib

app = Flask(__name__)
app.config['FAVICON'] = 'favicon.ico'

labels = ["SMPN 42","SMPN 50","SMPN 25","SMPN 3","SMPN 4"]
data=[]

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/rekomendasi')
def index():
    return render_template('index.html')

@app.route('/cekrekomendasi', methods=['POST'])
def cek():

    mtk = int(request.form['mtk'])
    bhs_indo = int(request.form['bhs_indo'])
    ipa = int(request.form['ipa'])
    address = request.form['address']
    lat , long = geocode(address)
    
    smp42 = calculate_distance(lat, long,-7.245035,112.718095)
    smp50 = calculate_distance(lat, long,-7.26214,112.696383)
    smp25 = calculate_distance(lat, long,-7.272261,112.703384)
    smp3 = calculate_distance(lat, long,-7.25597,112.73566)
    smp4 = calculate_distance(lat, long,-7.257318,112.736541)
    
    data=[[mtk,bhs_indo,ipa,lat,long,smp42,smp50,smp25,smp3,smp4]]
    
    classifier = joblib.load('classifier_randomforest.joblib')
    predictions = classifier.predict(data)

    if mtk >= 70 and bhs_indo >= 70 and ipa >= 70:
        recommended_smp = ['SMP_Negeri 42', 'SMP_Negeri 25', 'SMP_Negeri 50', 'SMP_Negeri 3', 'SMP_Negeri 4']
        jarak_smp = [smp42, smp50, smp25, smp3, smp4]
        recommended_smp_pred = [(smp) for smp in zip(jarak_smp, recommended_smp)]
        recommended_smp_pred = sorted(recommended_smp_pred, reverse=False)
        
        result = 'Rekomendasi SMP Negeri Yang Dapat Siswa Pilih Yaitu: <br>'
        for i, (smp) in enumerate(recommended_smp_pred[:5]):
            result += f'{i+1}. {smp}<br>'

        return render_template('result.html', result=result, recommended_smp_pred=recommended_smp_pred, jarak=jarak_smp, smp=recommended_smp)
    else:
        result = "MOHON MAAF SISWA TIDAK DITERIMA DI SMP NEGERI"
        return render_template('result.html', resultt=result, status='false')

# RUMUS MENCARI LONG LAT DISTANCE
def calculate_distance(start_latitude, start_longitude, destination_latitude, destination_longitude):
    start_point = (start_latitude, start_longitude)
    destination_point = (destination_latitude, destination_longitude)
    distance = geodesic(start_point, destination_point).kilometers
    return distance

def geocode(address):
    address = request.form['address']
    geolocator = Nominatim(user_agent='geocoding_app')
    location = geolocator.geocode(address)

    if location is not None:
        latitude = location.latitude
        longitude = location.longitude
        return latitude,longitude
    else:
        return 'Gagal mendapatkan koordinat'

if __name__ == '__main__':
    app.run(debug="true")

