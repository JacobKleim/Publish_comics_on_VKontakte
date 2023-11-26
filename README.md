# Publish_comics_on_VKontakte

## Project Description
 - The program allows you to publish a random comic in a VK group. Interaction with VK API is configured
 - To publish entries in a group, you need to [create a VK application](https://dev.vk.com/ru)

## Technologies and tools
 - Python 3.9.10

## Setup
 Clone this repository and go to the project folder:
   ```bash
   cd /c/project_folder
   ```
   ```bash
   git clone git@github.com:JacobKleim/Publish_comics_on_VKontakte.git
   ```
   ```bash
   cd /c/project_folder/Publish_comics_on_VKontakte 
   ```
## Environment      
 Сreate and activate a virtual environment  
   ```
   python -m venv venv
   ```
   ```bash
   source venv/Scripts/activate
   ```
## Requirements
 Install dependencies:
   ```
   python -m pip install --upgrade pip
   ```
   ```
   pip install -r requirements.txt
   ```

## Environment variables
 Create a .env file with parameters:
   ```
   VK_API_USER_TOKEN=Your api token. 
   ``` 
   ```
   VK_USER_ID=Your user id
   ```
   ```
   GROUP_ID=Group id
   ```
   #### How to get VK_API_USER_TOKEN
   [Instructions](https://dev.vk.com/ru/api/access-token/implicit-flow-user) for obtaining a user access key

## Run:
   ```
   python main.py
   ```   