# NEO2D

An agent that learns information and builds associations between objects in its environment. NOW IN AMAZING 2D!

NEO is an attempt to simulate how people learn from experience with objects in the real world and how we can replicate that understanding
within machines. This project is a continuation of our Society's previous project 
[NEO_LEARNING_SOFTBOT](https://github.com/sai-byui/NEO_Learning_Softbot), which placed NEO in a 1d text-based
environment. For this semester project Neo will be moving within a 2D visual environment. The project combines our pathfinding work from 
[Bot-Arena-3](https://github.com/sai-byui/bot-arena-3) and our database architecture from NEO version 1.

If you would like to read a high level description of the natural language aspect of the project and it's various components, please see the [NEO NLP Project Documentation.docx](https://github.com/sai-byui/NEO2D/blob/master/documentation/NEO%20NLP%20Project%20Documentation.docx) file in this repo. 

This program runs off of python 3.6+ code. You will need to install 3.6 or higher to run the project.
The project also uses the pygame library to create the visuals and pyttsx3 to generate Neo's voice. Both libraries will need to be 
installed to run NEO2D.

### update: The speech generation and recognition functions have been commented out of the project in order to make it easier to setup. You will only need to install the pygame library to run the project. The setup instructions will be left here for anyone that wants to install all of the necessary libraries to use all features of the project.

## Setup Instructions(For Windows/Linux users)

1. follow the directions outlined on [this page](https://github.com/sai-byui/python_resources/blob/master/Python_links/Python-links.md) to install python, pycharm, and pygame 
2. install the pyttsx3 library through the command line: pip install pyttsx3</br>
2a. for windows users, you may have to open your terminal as an admin to run this command. To do this, first Click your Start button.</br>
2b. In the Start Search box, type cmd, and then press CTRL+SHIFT+ENTER.</br>
2c. If the User Account Control dialog box appears, click Continue. Your terminal will open and you can then run the pip command in step 2

3. For Windows users, you will also need to install the Pypiwin32 package using this command: python -m pip install pypiwin32 
4. select the "clone or download button" and download the zip file of this repository onto your machine (We recommend creating a folder on your desktop to save this into so you will have easy access to it) then unzip the file.
5. open Pycharm
6. select open project
7. open the folder that you saved the file in from step 4. Select the folder "NEO2D" and select ok.
8. after the project is completely loaded into pycharm, drop down the "NEO2D" folder to view the files located in this project
9. Right click "main_manager.py" and select "Run 'main_manager'". If everything was installed correctly the program should begin running.

