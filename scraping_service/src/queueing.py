import copy
from typing import List
from urllib.parse import urlparse

def count_domains(url_list: List[str]) -> dict:
	hosts = {}

	for url in url_list:
		url_obj = urlparse(url)
		if url_obj.hostname not in hosts:
			hosts[url_obj.hostname] = 1
		else:
			hosts[url_obj.hostname] += 1

	return hosts


def generate_request_queue(host_count: dict, url_list: List[str]) -> List[str]:

	"""
	Provisions request queue

	It will sort the batches by num hosts per requests. As urls run out it will dial it down.

	EX: 20 hosts -> creates a batch of 20 requests for each url.
	"""

	host_count_copy = copy.deepcopy(host_count)	
	batches = [] # end batches
	while url_list: # while theres urls in the list
		batch = []
		batch_tracker = {}
		for url in url_list:
			host = urlparse(url).hostname

			if host not in batch_tracker and host_count_copy.get(host) > 0: 
				batch.append(url) # append to batch
				batch_tracker[host] = True # track batch change for host
				url_list.remove(url) # remove from list
				host_count_copy[host] -= 1  # decrement host count

			remaining_hosts = [k for k,v in host_count_copy.items() if v > 0]
			
			if list(batch_tracker.keys()) == remaining_hosts: # check if at end of batch
				batches.append(batch)
				break
	return batches