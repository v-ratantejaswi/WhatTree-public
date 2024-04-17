from flask import Flask, redirect, url_for, render_template, request, flash
from PIL import Image
from pymongo import MongoClient
import os
import requests
import folium
from folium.plugins import MarkerCluster
from azure.storage.blob import BlobServiceClient
import io
import base64
import google.generativeai as genai
import PIL.Image
from datetime import datetime
import json



app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']

GOOGLE_API_KEY=os.getenv('GOOGLE_API_KEY_WT')
genai.configure(api_key=GOOGLE_API_KEY)


# Setup MongoDB connection
mongo_uri = os.environ['MONGO_URI']
client = MongoClient(mongo_uri)
db = client[os.environ['MONGO_DB']]
collection = db[os.environ['MONGO_COLL']]

blob_service_client = BlobServiceClient.from_connection_string(os.environ['BLOB_CONNSTRING'])
container_client = blob_service_client.get_container_client('tree-image-container')


# PIL Compress Method - Compresses the image.
def compress_and_resize_image_pil(file_stream, target_size=(600, 600), quality=20):
    image = Image.open(file_stream)
    image.thumbnail(target_size, Image.LANCZOS)
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG', optimize=True, quality=quality)
    img_byte_arr.seek(0)
    return img_byte_arr

#Uploads the passed image to Azure Blob Storage and returns the URL.
def upload_blob(blob_name, data):
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(data, overwrite=True)
    return blob_client.url


#Fetches the name and details of the plant passed
def get_plant(image_data):
    compressed_image = PIL.Image.open(image_data)
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content(["Give the details of the main plant/tree in the image. Give the common name, scientific name, season, 2-3 sentence description of the tree/plant. Just give those details in Json format. Try very hard as if you have all the knowledge in the world about trees/plants. If you dont know the tree name, just say Unknown in the name. If there is no tree/plant in the image, just say No Tree Found.", compressed_image],
                                      generation_config={
                                                "max_output_tokens": 2048,
                                                "temperature": 0,
                                                "top_p": 1,
                                                "top_k": 32
                                            },)
    return response.text


#Route to test MonoDB connection
@app.route("/test-db")
def test_db():
    try:
        document = collection.find_one()
        return f"Connection successful: {document}"
    except Exception as e:
        return f"Error connecting to DB: {str(e)}"

#Route to home page
@app.route("/")
def home():
    photos = list(collection.find({}, {'_id': 0}))
    map = folium.Map(location=[0, 0], zoom_start=2, control_scale=True)

    marker_cluster = MarkerCluster( disableClusteringAtZoom=16).add_to(map)

    for photo in photos:
        folium.Marker(
            location=[photo['Latitude'], photo['Longitude']],
            popup=folium.Popup(f"{photo['Name']}", parse_html=True)
        ).add_to(marker_cluster)

    map_html = map._repr_html_()
    return render_template("index.html", map_html=map_html, photos=photos)



#Route to About Page
@app.route("/about")
def about():
    return render_template("about.html")



#Route to add a tree photo page
@app.route("/add_photo", methods=["GET", "POST"])
def add_photo():
    if request.method == "POST":
        now = datetime.now()
        file = request.files["photo"]
        
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        try:
            image = Image.open(file)
            exif_data = image._getexif()
            
            if exif_data:
                lat = exif_data.get(34853, {}).get(2)
                latref = exif_data.get(34853, {}).get(1)
                lon = exif_data.get(34853, {}).get(4)
                lonref = exif_data.get(34853, {}).get(3)
                img_datetime = exif_data.get(306)
                img_date, img_time = None, None
                if img_datetime:
                    parts = img_datetime.split(' ')
                    if len(parts) == 2:
                        img_date, img_time = parts

                upload_date = now.strftime("%Y-%m-%d")
                upload_time = now.strftime("%H:%M:%S")

                
                def dms_to_dd(dms, direction):
                    degrees, minutes, seconds = dms
                    dd = degrees + minutes / 60 + seconds / 3600
                    if direction in ['S', 'W']:
                        dd *= -1
                    return dd
                
                
                latitude_decimal = dms_to_dd(lat, latref)
                longitude_decimal = dms_to_dd(lon, lonref)

                
                latitude_decimal, longitude_decimal = float(latitude_decimal), float(longitude_decimal)
                
                compressed_image = compress_and_resize_image_pil(file)
                
                plant_details = get_plant(compressed_image)
                plant_details = plant_details.strip().replace("```json", "").replace("```", "")
                plant_details = json.loads(plant_details)

                name = plant_details.get("name")
                scientific_name = plant_details.get("scientific_name")
                season = plant_details.get("season")
                description = plant_details.get("description")
                if "No Tree Found" in name:
                    flash("The uploaded image doesnt contain a tree/plant.")
                    return redirect(request.url)
                image_url = upload_blob(name+"_"+str(latitude_decimal)+"_"+str(longitude_decimal), compressed_image.getvalue())
                if image_url:
                    comments = request.form.get("comments")
                    try:
                        collection.insert_one({
                            "Name": name, "Latitude": latitude_decimal, "Longitude": longitude_decimal, "Scientific_name": scientific_name,
                            "Season": season, "Details": description ,"Comments": comments, "ImageUrl": image_url, "Cap_date": img_date,
                            "Cap_time": img_time, "Upl_date": upload_date, "Upl_time": upload_time
                        })
                    except Exception as e:
                        flash("Error: Couldn't add image. Please try again!")
                        return redirect(request.url)
                return redirect(url_for("home"))
            else:
                flash(f"An error occurred while processing the image: Image metadata not found.")
                flash(f"Please make sure your location is turned on and image is captured on the camera app.")
                return redirect(request.url)

        except Exception as e:
            flash(f"An error occurred while processing the image: Image metadata not found.")
            flash(f"Please make sure your location is turned on and image is captured on the camera app.")
            return redirect(request.url)
    return render_template("add_photo.html")

#Route to Tree View page
@app.route("/tree_view")
def tree_view():
    photos = list(collection.find({}, {'_id': 0}))
    if not photos:
        flash("No photos available")
        return redirect(url_for('home'))
    return render_template("tree.html", photos=photos)


if __name__ == "__main__":
    app.run(debug=True)