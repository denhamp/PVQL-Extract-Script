# PVQL-Extract-Script
 
This script is used to extract the data from the PVQL database.

## Usage

python pvql_extract.py config.yml


## Requirements

* Python 3.6
* requests

## Input

config.yml file defines:
     The URL for the SPA tenant.
     Username for the SPA user
     PVQL query string to be used in the request
     Output csv file name to store the extracted data

## Output

* The output is a csv file with the metrics and categorical defined in the PVQL query.