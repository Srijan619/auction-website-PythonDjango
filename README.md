# YAAS- Yet Another Auction System

### Landing page: http://chapssrijan.pythonanywhere.com/auction/

## Implemented Functionalities

- [x] UC1: Create user
- [x] UC2: Edit user
- [x] UC3: Create auction
- [x] UC4: Edit auction's description
- [x] UC5: Browse & Search
- [x] UC6: Bid
- [x] UC7: Ban auction
- [x] UC8: Resolve auction
- [x] UC9: Language switching
- [x] UC10: Concurrency
- [x] UC11: Currency exchange
- [x] WS1: Browse & Search API
- [x] WS2: Bid API
- [x] REQ9.3: Store language preference  
- [x] REQ3.5: Send seller auction link
- [x] TREQ4.1.1 Test Implemented for REQ 9
- [x] TREQ4.1.2 Test Implemented for REQ 3
- [x] TREQ4.2: Implemented random data generation program  
- [x] TREQ4.1.3: Test Implemented for REQ 10

## Browser Used: ***Chrome for Windows***


## List of python packages

* jango 2.2.6
* Django 2.2.5
* requests 2.22.0
* djangorestframework 3.10.2
* freezegun 0.3.12
* Faker	2.0.3
* certifi	2019.9.11
* chardet	3.0.4
* django-user-language-middleware	0.0.3
* djangorestframework	3.10.2
* freezegun	0.3.12
* idna	2.8
* manage.py	0.2.10
* pip	19.3.1
* python-dateutil	2.8.0
* python-gettext
* pytz	2019.3
* requests	2.22.0
* setuptools	41.2.0
* six	1.12.0
* sqlparse	0.3.0
* text-unidecode
* urllib3	1.25.6
* wheel	0.33.6

##### * Some of the packages were used for the test purpose

### Bugs and crashes

* Random data generation works completely fine for the first time with all unique usernames but on the second generation it creates some similar usernames which doesn't matches the unique_username constraints.
* Additional test is included in test.py
* Sending email is for test purpose 'EMAIL_BACKEND' is used

