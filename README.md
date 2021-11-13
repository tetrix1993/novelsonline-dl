# Novels Online Downloader
Download novels from the website [Novels Online](https://novelsonline.net/). Written in Python 3.7.

## Setting Up
Run the following command to install all the packages required to run the program.
```
pip install -r requirements.txt
```

## Running the Program
```
python novelsonline.py -id <novel-id>
```

For example, if you want to download the novel [Sword Art Online - Progressive](https://novelsonline.net/sword-art-online-progressive), the `novel-id` will be `sword-art-online-progressive`. You may also enter the entire URL. Both commands below are valid:
```
python novelsonline.py -id sword-art-online-progressive
python novelsonline.py -id https://novelsonline.net/sword-art-online-progressive
```

The downloaded chapters will be saved as a `.txt` file. Images will be downloaded as well if available.

Note: You might want to run the same command again in case some chapters are not properly downloaded.
