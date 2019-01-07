# CONVENIENT PRESENTATION OF INFORMATION FROM VARIOUS WEATHER WEBSITES
### MAIN PURPOSE
> The main purpose of this project is to obtain real knowledge and practice of solving real problem.
### IDEA
> Combine and present information from different weather websites in one place and be able to view and compare them.
### GOALS:
1. Collect information from different weather websites.
2. A simple interface to use the program. 
3. Adding a new resource, feature will not change the implementation of the main functionality.
4. Possibility of further development of the program.

*RESOURCES:* [AccuWeather](https://www.accuweather.com/), [Rp5](http://rp5.ua/), etc.\
*TOOLS:* Python3, ...
***
### Commands for the weather application:
* Run the weather application for all providers\
`python3 app.py`
* Get a list of all providers\
`python3 app.py providers`
* Get weather information from a specific provider\
`python3 app.py [provider id]`
* Update cache\
`python3 app.py --refresh`\
or\
`python3 app.py [provider id] --refresh`
* Clear cache\
`python3 app.py clear-cache`
* Save the weather information to the file\
`python3 app.py save-to-csv [provider id]`
* Customize your location to get weather information\
`python3 app.py config [provider id]`
* To see the full traceback in the case of error, use --debug command\
`python3 app.py --debug, python3 app.py config accu --debug, etc.`