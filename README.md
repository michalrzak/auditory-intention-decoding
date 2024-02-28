This is quick README for this project: TODO extend

Potential problems when installing:
wxPython => needs gtk devel tools (libgtk-3-devel on ubuntu)
https://wxpython.org/blog/2017-08-17-builds-for-linux-with-pip/index.html

On Linux systems with system.d don't forget:
sudo groupadd --force psychopy
sudo usermod -a -G psychopy $USER

sudo nano /etc/security/limits.d/99-psychopylimits.conf and copy/paste in the following text to that file:

@psychopy   -  nice       -20
@psychopy   -  rtprio     50
@psychopy   -  memlock    unlimited

And then restart the computer
