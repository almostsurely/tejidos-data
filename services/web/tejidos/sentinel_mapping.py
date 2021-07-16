from __future__ import annotations

from datetime import datetime
from typing import List, Dict
from heapq import heapify
import random

SENTINEL_IMAGES = ["2020/1/12/0/R60m/",
				   "2020/1/17/0/R60m/",
				   "2020/1/2/0/R60m/",
				   "2020/1/22/0/R60m/",
				   "2020/1/27/0/R60m/",
				   "2020/1/7/0/R60m/",
				   "2020/10/13/0/R60m/",
				   "2020/10/18/0/R60m/",
				   "2020/10/23/0/R60m/",
				   "2020/10/28/0/R60m/",
				   "2020/10/3/0/R60m/",
				   "2020/10/8/0/R60m/",
				   "2020/11/12/0/R60m/",
				   "2020/11/17/0/R60m/",
				   "2020/11/2/0/R60m/",
				   "2020/11/22/0/R60m/",
				   "2020/11/27/0/R60m/",
				   "2020/11/7/0/R60m/",
				   "2020/12/12/0/R60m/",
				   "2020/12/17/0/R60m/",
				   "2020/12/2/0/R60m/",
				   "2020/12/22/0/R60m/",
				   "2020/12/27/0/R60m/",
				   "2020/12/7/0/R60m/",
				   "2020/2/1/0/R60m/",
				   "2020/2/11/0/R60m/",
				   "2020/2/16/0/R60m/",
				   "2020/2/16/1/R60m/",
				   "2020/2/21/0/R60m/",
				   "2020/2/26/0/R60m/",
				   "2020/2/6/0/R60m/",
				   "2020/3/12/0/R60m/",
				   "2020/3/17/0/R60m/",
				   "2020/3/2/0/R60m/",
				   "2020/3/22/0/R60m/",
				   "2020/3/27/0/R60m/",
				   "2020/3/7/0/R60m/",
				   "2020/4/1/0/R60m/",
				   "2020/4/11/0/R60m/",
				   "2020/4/16/0/R60m/",
				   "2020/4/21/0/R60m/",
				   "2020/4/21/1/R60m/",
				   "2020/4/26/0/R60m/",
				   "2020/4/6/0/R60m/",
				   "2020/5/1/0/R60m/",
				   "2020/5/11/0/R60m/",
				   "2020/5/11/1/R60m/",
				   "2020/5/16/0/R60m/",
				   "2020/5/21/0/R60m/",
				   "2020/5/21/1/R60m/",
				   "2020/5/26/0/R60m/",
				   "2020/5/26/1/R60m/",
				   "2020/5/31/0/R60m/",
				   "2020/5/6/0/R60m/",
				   "2020/6/10/0/R60m/",
				   "2020/6/15/0/R60m/",
				   "2020/6/20/0/R60m/",
				   "2020/6/25/0/R60m/",
				   "2020/6/30/0/R60m/",
				   "2020/6/5/0/R60m/",
				   "2020/7/10/0/R60m/",
				   "2020/7/15/0/R60m/",
				   "2020/7/20/0/R60m/",
				   "2020/7/25/0/R60m/",
				   "2020/7/30/0/R60m/",
				   "2020/7/30/1/R60m/",
				   "2020/7/5/0/R60m/",
				   "2020/8/14/0/R60m/",
				   "2020/8/19/0/R60m/",
				   "2020/8/24/0/R60m/",
				   "2020/8/29/0/R60m/",
				   "2020/8/4/0/R60m/",
				   "2020/8/9/0/R60m/",
				   "2020/8/9/1/R60m/",
				   "2020/9/13/0/R60m/",
				   "2020/9/18/0/R60m/",
				   "2020/9/23/0/R60m/",
				   "2020/9/28/0/R60m/",
				   "2020/9/3/0/R60m/",
				   "2020/9/8/0/R60m/",
				   ]

class SentinelMapper:

	_instance = None

	@classmethod
	def instance(cls) -> SentinelMapper:
		if cls._instance is None:
			cls._instance = SentinelMapper(image_directory_list=SENTINEL_IMAGES)
		return cls._instance


	def __init__(self, image_directory_list: List[str]):
		self.mapping = self.create_mapping(image_directory_list=image_directory_list)


	@staticmethod
	def create_mapping(image_directory_list: List[str]) -> Dict:
		mapping = {}
		for directory in image_directory_list:
			[year, month, day, image_num, _, _] = directory.split("/")
			date = datetime(year=int(year), month=int(month), day=int(day))
			if not date in mapping:
				mapping.update({date: []})
			mapping.get(date).append(directory)
		return mapping

	def get_directory_from_date(self, date: datetime) -> str:
		deltas = []
		for key_date in self.mapping.keys():
			delta = key_date - date
			deltas.append((abs(delta.total_seconds()), key_date))
		heapify(deltas)
		_, key = deltas[0]
		return random.choice(self.mapping.get(key))

	def get_directory_from_day_month(self, month: int, day: int) -> str:
		assert 1 <= month <= 12
		assert 1 <= day <= 31
		return self.get_directory_from_date(datetime(year=2020, month=month, day=day))


if __name__ == '__main__':
	now = datetime.now()

	print(now.day)
	print(now.month)

	today_in_target_year = datetime(year=2020, month=3, day=26)
	print(SentinelMapper.instance().get_directory_from_day_month(month=3, day=26))









