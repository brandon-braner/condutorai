# ConductorAI Challenge

## Overview

This repository contains the code and resources for the ConductorAI Challenge. The challenge involves extracting numerical data from a given PDF document.

## Problem Statement

[Here is a large pdf document](https://www.saffm.hq.af.mil/Portals/84/documents/FY25/FY25%20Air%20Force%20Working%20Capital%20Fund.pdf?ver=sHG_i4Lg0IGZBCHxgPY01g%3d%3d). We want to find the largest number in this document. The unit is not important (could be dollars, years, pounds, etc), we're just looking for the greatest numerical value in the document.

For a bonus challenge if you have time, take natural language guidance from the document into consideration. For example, where the document states that values are listed in millions, a value of 3.15 would be considered to be 3,150,000 instead of 3.15.

## What you need to do

1. Read the instructions above describing the desired behavior. Your solution should output the greatest numerical value it can find in the document. Feel free to download the document manually and reference it locally instead of fetching it over the internet in your code.
2. Implement a solution in software. You can use any language you want. If you don't have a preference, use python. You can use any open source dependencies you want, but your software must be self-contained, meaning it cannot call to any external APIs. When developing, you can use *anything* (except another human) to help you, including Google, Copilot, ChatGPT, etc.
3. Put your software solution somewhere where you can link it to us, a public git repo is probably easiest. Provide a README with a brief description of how to run your software.
4. Email someone at ConductorAI (the person who gave you this project) with a link to your code.

## Solution


I have provided two solutions to this problem. This first is an internal solution that only uses Python and a couple libraries to extract the numbers from the PDF. The second is an external solution that uses ai to extract the numbers from the PDF. To avoid having you setup local ai with something like Ollama, I have the ai solution using Gemini 2.0 Flash.

Both can be run from the cli.

### Installing Dependencies

This project us `uv` to manage its dependencies. To install `uv` follow the instructions [here](https://docs.astral.sh/uv/getting-started/installation/)
To run the local version will need to install `ghostscript`, instructions are [here](https://camelot-py.readthedocs.io/en/master/user/install-deps.html). 

### Enviroment

Copy the .env.example file to .env and add your Gemini API key. You can get a Gemini API Key [here](https://aistudio.google.com/prompts/new_chat)

### Internal Solution

The internal solution which is located in the `numai` directory in a file called `numinternal.py`.

You can run it by running `uv run python main.py "FY25 Air Force Working Capital Fund.pdf" ` where the argument is the name of the file located in the data directory.

### AI Solution

The ai solution which is located in the `numai` directory in a file called `numai.py`.


You can run it by running `uv run python main.py "FY25 Air Force Working Capital Fund.pdf" --ai` where the argument is the name of the file located in the data directory and the ai flag tells it to use the ai solution. You will need to have added an api key to the .env file.
