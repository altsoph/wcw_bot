# WebCamWatcher bot

## What's is?
WebCamWatcher is a project designated to spectate a list of public open webcams, to spot some interesting objects and to send notifications about spotted things to various channels.

Currently, WCW bot 
  * tracks several nature parks webcams and sends photos of animals to the [special telegram channel](https://t.me/s/WebCamWatcher),
  * tracks some cameras on russian rivers banks and sends photos of boats to another [telegram channel](https://t.me/s/wcw_boats),
  * tracks a camera on a river ship, Obrazcov, and sends photos of random encounters to the [third telegram channel](https://t.me/s/WCW_Caryatid).

![Demo pics](https://github.com/altsoph/wcw_bot/blob/master/shots.png)

Some more details on the origins of this project are available in [my medium post](https://medium.com/altsoph/webcamwatcher-ff3c80e77b95).

In this repo one can find the current pack of scripts which supports all the logic behind these processes.

## Installation

To run WCW bot one needs **python3** with several additional libraries:
  * [urllib.request](https://docs.python.org/3/library/urllib.request.html) -- should be a part of standart python libraries
  * PIL ([Pillow](https://pypi.org/project/Pillow/)) -- also usually goes with the standart python libraries, I think
  * cv2 ([opencv-python](https://pypi.org/project/opencv-python/))
  * telegram.ext ([python-telegram-bot](https://pypi.org/project/python-telegram-bot/))
  * [yaml](https://pyyaml.org/)
*Note, the list of requirements depends on used modules, so it could be shorter or longer in a concrete case.*

Finally, to run it one will need a [yoloV3 pretrained network](https://pjreddie.com/darknet/yolo/), since current version of WCW bot uses it as a main image recognizer. Please, downoad and put in a main directory the following 3 files: *yolov3.cfg, yolov3.txt, yolov3.weights*.

## General structure

The WCW bot has a flexible modular structure, so it can be expanded and re-configured in a different ways.
To leverage it, one should understand several main principles. 

The general way to setup and configure a bot is to use *config.yaml* file with the all options bot needs to run.
The configuration is divided into five major sections:
  * *general* settings
  * the *sources* section consists of a list of webcams under the surveillance
  * the *targets* section holds of a list of publishing channels (mainly, telegram channels for now)
  * the *chains* section specifies processing pipelines -- how to process them each cameras' images and where to send them
  * the virtual *secrets* section doesn't exists in *config.yaml*, but there is a second file *secrets.yaml* which maps into the 'secret' section of config during the initializaton (just to keep secrets out of repository).

Let's consider these sections more detailed.

### Sources
### Targets
### Chains

![Chain config scheme](https://github.com/altsoph/wcw_bot/blob/master/config_scheme.png)

## Available modules


## TBD

