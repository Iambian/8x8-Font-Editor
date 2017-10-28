Escheron Cutscene Editor - DCS Font Editor Component - ReadME
-----------------------------------------------------------------------------


Because maybe it could be useful for people who want to use the
DCS7 text renderer routine and supply their own font tables.


_______________________________________
 ..:: Pre-Usage ::..
 
This is a Python 2.7 application.
You'll need to install the following on your computer:

* Python 2.7.x    https://www.python.org/
* Pillow          https://python-pillow.org/

NOTICE: It has to be Python 2.x. You must NOT use/install Python 3.x

        If you already have Python installed but not Pillow, you can
        do that easily by opening the console window and use pip.
        
        If you don't know if pip is up to date, type in the CLI:
          pip install pip --upgrade
          
        After you're sure pip is up to date, type the following:
          pip install Pillow
       
_______________________________________
 ..:: Usage ::..

Double-click main.py or execute it from the command line prompt.
Let's assume that at this point, you're seeing a Tk window
containing the interface. After that, just follow this advice:

 1. Have an ASCII table handy. Google for your favorite.
 2. Play around. Click stuff. You'll know pretty quick
    if you've messed up
 3. The input boxes require you to hit Enter/Return to
    make anything stick. Once it sticks, you'll know.
 4. As long as you don't save over the original font
    file, you don't have to worry about any mistakes.
    So feel free to make them.
 5. These .dcf files are just text files. Open them in
    a text editor and paste them over the DCS font table
    for use.

 6. That "Start from Scratch" button has to be clicked
    repeatedly. This is an anti-accident feature.
    
_______________________________________
 ..:: Troubleshooting ::..
 
If you're using Windows, click an empty spot in the folder containing main.py,
Shift+RightClick, then click the option "Open command window here"

Type the following: python main.py

See if that gets you anywhere. If it doesn't, Google the errors you're
getting. If you think it's an error in my application, pass me a note either
on IRC (irc.efnet.org/#cemetech) or in a PM on www.cemetech.net
 
If you're NOT using Windows, idk what to tell you
aside from "Google might still be able to help."

_______________________________________
 ..:: Thanks ::..
 
Geekboy1011 - Gives cherries
KermMartian - Awesome guy
Sorunome    - Fox pics
Zera        - Best storyboarder

_______________________________________
 ..:: Notes ::..

This is just pieces of the ECE project glued together into a single file.
The majority of that glue is at the top of the Application class.

This application was cobbled together with lots of LOVE.
