# Recaptcha v2 solver
A simple program to bypass recaptcha version 2 using audio verification method. <br>
This program only demonstrates how to bypass recaptcha on https://www.google.com/recaptcha/api2/demo<br>
You need to readapt this program to work on other websites. It is difficult to make the code general as websites are built differently.<br>
If you have a great idea, do let me know!<br>

## OS support
1. Windows
2. Mac

## Dependencies
1. selenium
2. pydub
3. speech recognition
4. ffmpeg
5. ffmpy
6. stem

## Usage
python recaptcha_solver.py<br>

## Updates
[23 Sept 21] Auto detection of recaptcha. With this functionality, this script may work for other pages. <br>
[28 Nov  21] Using Tor connection to randomise your IP address. <br>
This technique is used to bypass "Your Computer or Network May Be Sending Automated Queries."<br> 
It can be activated by setting "activate_tor = True". <br>
As the Tor ip address is shared, some other users may use it for same purpose, which causes the IP address to be blacklisted.<br> 
The success rate of using this technique is about 10%.<br>


## Common errors
Q1. NameError: name 'sample_audio' is not defined <br>
A1. Try installing ffmpeg manually, http://blog.gregzaal.com/how-to-install-ffmpeg-on-windows/<br>
Q2. Your Computer or Network May Be Sending Automated Queries. <br>
A2. Change activate_tor = True, you may be able to bypass it after a few tries.<br>

## Video tutorial
https://www.youtube.com/watch?v=Fdu81T9GgMA

## Medium
https://ohyicong.medium.com/how-to-bypass-recaptcha-with-python-1d77a87a00d7
