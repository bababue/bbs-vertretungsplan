# Vertretungsplan

Live instance: [bbsfts.de](https://bbsfts.de/)

Reformatting of the WebUntis Monitor view  
Built with flask, htmx and postgresql

## Usage
### Scraping
1. Create nescessary table (schema.sql)
2. Set enviroment variables for database connections
3. Run main.py with the date range that should be scraped

Example:
```python
python main.py 0 5 #This will scrape dates starting today, 5 days into the future
python main.py -5 3 #This will scrape dates starting 5 days ago, up until in 3 days
```

### Flask Server
1. Set enviroment variables for database connection
2. Start flask app in a production enviroment, preferrably gunicorn