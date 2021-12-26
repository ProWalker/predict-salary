# Programming vacancies compare

Script for comparing salaries of vacancies by programming language.  
At the moment script takes in account 10 programming languages:  
* Javascript
* Python
* Ruby
* PHP
* C++
* C#
* C
* Go
* Objective-C

Comparison takes place on two sites: [HeadHunter](https://hh.ru) and [SuperJob](https://superjob.ru).  
Vacancies are listed in Moscow.  

### How to install

    pip install -r requirements.txt  

Create file .env in script root folder.  
In .env file create the environment variable SUPERJOB_API_KEY.  
Register your app in SuperJob site [here](https://api.superjob.ru/)  
After you get API key, assign it to the environment variable SUPERJOB_API_KEY.  

### Project Goals

The code is written for educational purposes on online-course for web-developers [dvmn.org](https://dvmn.org/).