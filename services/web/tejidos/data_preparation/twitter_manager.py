from __future__ import annotations
import os
import re
from dataclasses import dataclass
from typing import List

import tweepy


@dataclass(frozen=True)
class Earthquake:
    magnitude: float
    latitude: float
    longitude: float

    def to_dict(self):
        return self.__dict__

class TwitterManager:

    _instance = None

    def __init__(self, client: tweepy.AppAuthHandler):
        self.client = client

    @classmethod
    def instance(cls) -> TwitterManager:
        if cls._instance is None:
            auth = tweepy.AppAuthHandler(consumer_key=os.getenv("TWITTER_CONSUMER_KEY"),
                                         consumer_secret=os.getenv("TWITTER_CONSUMER_SECRET"))

            cls._instance = TwitterManager(client=tweepy.API(auth))
        return cls._instance

    def fetch_earthquake(self, number) -> List[Earthquake]:

        result = []

        for i, tweet in enumerate(tweepy.Cursor(self.client.search,
                              q='SISMO Magnitud Loc.',
                              id="SismologicoMX",
                              exclude_replies=True,
                              include_rts=False,
                              count=number).items(limit=number)):

            regex_result = re.match(r".*Magnitud ([0-9\.]+).*Lat ([-0-9\.]+) Lon ([-0-9\.]+).*", tweet.text)
            if regex_result:
                result.append(Earthquake(magnitude=regex_result.group(1),
                                         latitude=regex_result.group(2),
                                         longitude=regex_result.group(3)))
        return result

if __name__ == '__main__':
    earthquakes = TwitterManager.instance().fetch_earthquake(number=10)
    import json
    print(json.dumps([earthquake.to_dict() for earthquake in earthquakes], indent=4))
