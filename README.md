# Weather Scraper and MongoDB Storage

This project is designed to scrape weather data for a week from all 81 provinces in Turkey and store the collected data in a MongoDB database.

## Technologies Used

- Python
- BeautifulSoup
- Requests
- MongoDB

## Project Description

- Weather data for each province is obtained by scraping [havadurumux.net](https://www.havadurumux.net/).
- The collected data is stored in a MongoDB collection named 'hava_durumu_koleksiyonu'.
- If a record already exists, it will not be added again to avoid duplication.
- Threading is implemented to speed up the data retrieval process.

## Usage

1. The `plaka_kodlari.json` file should contain province plate codes and names.
2. The project can be executed by running the `main()` function.

## Notes

- A local MongoDB server is used for the database connection.
- MongoDB connection details (`localhost`, `27017`) should be updated according to the project requirements.

**Note:** Before running the project, make sure to install the necessary dependencies.
