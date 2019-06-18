# WebCamWatcher bot

## What's it?
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

### General

The general section contains main parameters for a WCW bot, such configuration paramaters are available to each module in each chain (but you can override them by a module's config if you want). 
The current list of paramters is:
  * *iteration_time* -- a pause (is secs) between main iterations of a bot
  * *cache_time* -- for how long (in secs) store images received from a camera (useful if you know what camera updates its image evety X minutes)
  * *modules_dir* -- describes locations of different modules
  * *filtering* section contains:
    * *ignore_tags* -- a list of tags which will not trigger notifications
    * *min_confidence* and *nms_threshold* -- confidence parameters of yoloV3 image recognizer
  * *annotation.template* -- a general alert message template
  * *sender.retries_num* and *sender.retries_pause* -- parameters of a sender retrying strategy in case of network problems
  * *class_colors* -- a collection of color specifications for the detected tags (a default color is black)

### Sources

This section contains a dictionary of available sources (almost each source is a webcam) described by several parameters:
  * *id* -- a unique id of the source
  * *url* -- URL of the current image from the camera (one can use URIs like http, https, ftp)
  * *substitutions* -- a dictionary for substitution in the alert notification, usually contains *title* and *browser_url* parameters
  * one can specify some values to override parameters from the *general* section:
    * *min_confidence*
    * *nms_threshold* 
    * *replace_ignore_tags*
    * *add_ignore_tags*
    * *cache_time*
Note the special source *dbg_source* which can be used for debug using a *mod_fakedownloader* downloader module.

### Targets

This section contains a dictionary of available target channels (almost each them is a telegram channel now). Usually it's just a channel id, also one can override the general alert template with a channel specific one. Also, check the special target *dbg_folder* which can be used for debug using a *mod_saversender* sender module.

### Chains

The core idea of the WCW pipeline is chain. Each chain pulls images from one or more sources, runs a detector module over them, then filters resulting tags, decorates images, generates texts for the alerts and sends them to one or more target channels.

Here is a principal scheme of a typical chain:

![Chain config scheme](https://github.com/altsoph/wcw_bot/blob/master/config_scheme.png)

Take a look on a simple example of a chain config:
```
chains:
  simple_chain:
    sources:
      - 
        module: mod_simpledownloader # use a simpledownloader module
        source: boathead_obrazcov    # to get an image from this source
        parameters:
          check_period: 300          # re-check the webcam not more often than each 300 sec

    detector: mod_yolo3detector      # run yolo detector on a current image
    filters:                         
      -
        module: mod_conffilter       # remove tags with a confidence level lower than a threshold 
                                     # (from general parameters or from a source config)
      -
        module: mod_tagfilter        # remove tags specified in 'ignore_tags' list 
                                     # (from general and source configs)
      - 
        module: mod_manualfilter     # remove tags from a given area and a given subset
        parameters:
          suppress_list:
            - ['boathead_obrazcov',[55,690,1850,1100],['some','boat']]
      -
        module: mod_repeatfilter     # suppress alerts if the same tags were found in the same image last time
        parameters:
          storage: boathead
          suppress_period: 300
    enhancers:
      -
        module: mod_boxerenhancer    # draw boxes and tag names
    senders:
      - 
        sender_module: mod_tgsender  # if any tags are left send the resulting image via telegram
        annotator_module: mod_templateannotator  # use this module to generate some text of alert
        target: tg_debug             # use this target channel as a receiver
        parameters: {}
```

## Available modules

Here is a list of already available modules divided by classes:
   * downloaders
     * mod_simpledownloader.py -- a main downloader, gets an image from URL given in a source config (use #random# in URL to put a random substring for cache breaking, use *random_len* parameter in a source config to specify the length of a random substring).
     * mod_fakedownloader.py -- a debug downloader, gets a random image from *raw_tests/* subfolder.
     * mod_speclaplanddownloader.py -- an example of a more complicated downloader, it gets some json first then uses it to construct an image URL, then gets an image from the constructed URL.
   * filters
     * mod_conffilter.py -- filters out tags with a confidence less than *min_confidence* value (this threshold value can be specified in general / source / filter parameters).
     * mod_tagfilter.py -- filters out tags by a list, calculated based on *ignore_tags* from general parameters plus *replace_ignore_tags* and *add_ignore_tags* from source and filter parameters.
     * mod_sizefilter.py -- filters out tags from a list and with the area in given range.
     * mod_manualfilter.py -- filters out tags from a list and from a given area of image.
     * mod_repeatfilter.py -- suppresses tags if they are the same as previous time.
   * annotators
     * mod_templateannotator.py -- a basic annotator module, takes a template (from general / source / annotator parameters), fills in substitutions (again, from general / source / annotator parameters) and found tags.
   * enhancers
     * mod_boxerenhancer.py -- a basic enhancer module, just draws boxes around detected items and writes tag labels.
   * senders
     * mod_tgsender.py -- a telegram sender, uses a *secrets.tgsender.BOT_KEY* parameter as an API key, plus *general.sender.retries_num* or target's *retries_num* and *general.sender.retries_pause* / target's *retries_pause* parameters.
     * mod_saversender.py -- a debug sender, saves a resulting image to a file in a local directory (target's *path*) before enhancement (with a '\_raw' suffix) and after enhancement (with a target's *suffix* suffix).

## TBD

Just a backlog of possible improvements:
  * video-stream / youtube-steam screenshot downloaders
  * image auto-annotation with a neural network approach
  * add enhancers with instagram-style auto filters
  * autocrop enhancer
  * senders to twitter / instagram / ...
  * use some feedback signal from channels readers
  * try other detectors and/or retrain the current one
