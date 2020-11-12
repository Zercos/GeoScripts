# field-interpolation
Script that predict the position of near address point.

### Versions of script. 

1) The first one "interpolation-script" add coordinates where they are null. It finds the nearest houses and calculate the approximately location. There are two options: 
    - you can find location between two similar houses;
    - you can find location, if there is only one of them - connect to it if the distance not over limit;
  
2) Onother one "interpolation-approximately" add coordinates where they are null also checking the approximately similar columns. You provide the accurancy of columns. Also you should provide the position(index) of needed columns. Everything else is such as the first scripts.

### Prerequisites

*Python >=3.6*

### Usage

Run script:
```
python3 interpolation-approximately.py/interpolation-script-2.0.py
```