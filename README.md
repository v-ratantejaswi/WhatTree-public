# WhatTree

WhatTree is an interactive web platform for exploring and learning about various tree species globally. Users can contribute by uploading tree photos with location data, and the platform maps these locations and provides insights into the ecological significance of the trees.

## Link to WhatTree

https://whattree.azurewebsites.net/

## Functional Description

The uploaded image's metadata is searched for latitude, longitude and the capture time and date. Then, the image is compressed and then sent to Gemini Pro Vision API, which then gives the details of the tree/plant in the image. Then, the image is stored in Azure Blob and a link to that is generated, which is stored in MongoDb alongside other plant details. Folium and Leaflet.js are used to show the map and mark the markers and their clusters. The TreeView page lets the user cycle through all the tree/plant uploads letting the user see all the details of the tree. The backend functionalities are written in Flask(Python) and JavaScript.

## Features

- Interactive global map with tree locations
- Tree photo upload functionality
- Information about trees, including common and scientific names, descriptions, and best viewing seasons
- User-contributed content and comments

## Technologies Used

- Flask (Python Web Framework)
- MongoDB (Database)
- Leaflet.js (Interactive Maps)
- Azure Blob Storage (Image Hosting)
- OpenStreetMap (Map Tiles)
- Folium (Python library to generate Leaflet maps)
- Google Generative AI (To determine tree details)

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

What you need to install the software:

- Python 3.6+
- MongoDB
- Azure Storage Account

### Installing

A step-by-step series of examples that tell you how to get a development environment running:

- Clone the repository:

```bash
git clone https://github.com/your-username/WhatTree.git
cd WhatTree
```
- Install the required python packages

```bash
pip install -r requirements.txt
```

- Set up your environment variables in a .env file. This should include your MongoDB URI, Azure Blob Storage connection string, and your Google API key.

- Run the Flask application.
```bash
python3 app.py
```

## Usage
Navigate through the web app using the navbar. You can view the map of trees, add a new tree photo, and browse through the tree view which displays all uploaded trees.

## Contributing
If you would like to contribute to the development of WhatTree, please contact Ratan Tejaswi Vadapalli at:
- Email: ratantejaswi@gmail.com
- LinkedIn: https://www.linkedin.com/in/ratan-tejaswi-vadapalli/

## Acknowledgements

- All contributors who spend time to help this project grow
- The open-source community for continuous inspiration and guidance

## Forking
- If you fork or use this project as a part of your own, please give appropriate attribution by linking back to the original repository and citing the author's work.
- Remember to replace the placeholders with your actual GitHub username and other relevant information. Also, you should create the `CONTRIBUTING.md` files withi your GitHub repository to provide detailed information on how to contribute and the terms of using your project, respectively.

