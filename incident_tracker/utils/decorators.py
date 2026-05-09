
import functools
import time
import logging

def log_call(func):
	@functools.wraps(func)
	def wrapper(*args, **kwargs):
		logging.info(f'Calling {func.__name__}')
		result = func(*args, **kwargs)
		logging.info(f'{func.__name__} completed')
		return result
	return wrapper

def retry(times=3, delay=1):
	def decorator(func):
		@functools.wraps(func)
		def wrapper(*args, **kwargs):
			for attempt in range(1, times + 1):
				try:
					return func(*args, **kwargs)
				except Exception as e:
					if attempt == times:
						raise
					time.sleep(delay)
		return wrapper
	return decorator
