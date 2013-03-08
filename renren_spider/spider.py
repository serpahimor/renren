import time
import logging

import browser 
# import parse

default_storage=None
importlib=None
def set_repo(mode='repo_mysql'):
	global importlib
	if importlib is None:
		import importlib
	global default_storage
	try:
		default_storage=getattr(importlib.__import__(mode),mode)
	except AttributeError:
		print("class name in the module should be: {}".format(mode))
	except ImportError:
		print("module name '{}' not found".format(mode))

def runlog(tt='run'):
		logfile='run.log'
		logger=logging.getLogger(tt)
		hdlr=logging.FileHandler(logfile)
		formatter=logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
		hdlr.setFormatter(formatter)
		logger.addHandler(hdlr)
		logger.setLevel(20)#20 info, 40 error
		return logger

pf_sleep=2

class spider:
	def __init__(self,repo_name='test',user='yyttrr3242342@163.com',passwd=None):
		self.dl=browser.browser(user,passwd)
		if default_storage is None:
			set_repo()
		self.repo=default_storage(repo_name)
		print('storage mode: {}'.format(self.repo))
		self.log=runlog('spider')

		self.searched=dict()
		self.searched['friendList']=self.repo.getSearched('friendList')
		#self.searched['status']=self.repo.getSearched('status')
		#self.searched['profile']={}#self.repo.getSearched('profile')

	def login(self):
		return self.dl.login()

	def getStatus_friend(self,orig_id='410941086'):
		pageStyle='status'
		if pageStyle not in self.searched:
			self.searched[pageStyle]=self.repo.getSearched(pageStyle)
		if orig_id not in self.searched['friendList']:
			self.seq_process(orig_id,'friendList')
		friends=self.repo.getFriendList(orig_id)
		toSearch=(friends|{orig_id})-self.searched[pageStyle]
		self.log.info('{} of {},toSearch/total:{}/{}'.format('friends\' status',orig_id,len(toSearch),len(friends)))
		print('{} {} of {},toSearch/total:{}/{}'.format(time.strftime('%H:%M:%S',time.localtime()),'friends\' status',orig_id,len(toSearch),len(friends)))
		self.seq_process(toSearch,pageStyle)

	def getProfile_friend(self,orig_id='410941086'):
		pageStyle='profile'
		if pageStyle not in self.searched:
			self.searched[pageStyle]=self.repo.getSearched(pageStyle)
		if orig_id not in self.searched['friendList']:
			self.seq_process(orig_id,pageStyle)
		friends=self.repo.getFriendList(orig_id)
		toSearch=(friends|{orig_id})-self.searched[pageStyle]
		self.log.info('{} of {},toSearch/total:{}/{}'.format('friends\' profile',orig_id,len(toSearch),len(friends)))
		print('{} {} of {},toSearch/total:{}/{}'.format(time.strftime('%H:%M:%S',time.localtime()),'friends\' profile',orig_id,len(toSearch),len(friends)))
		self.seq_process(toSearch,pageStyle)

	def getNet2(self,orig_id='410941086'):
		pageStyle='friendList'
		if orig_id not in self.searched[pageStyle]:
			self.seq_process(orig_id,pageStyle)
		friends=self.repo.getFriendList(orig_id)
		toSearch=friends-self.searched[pageStyle]
		self.log.info('get net2 of {},toSearch/total:{}/{}'.format(orig_id,len(toSearch),len(friends)))
		print('{} get net2 of {},toSearch/total:{}/{}'.format(time.strftime('%H:%M:%S',time.localtime()),orig_id,len(toSearch),len(friends)))
		self.seq_process(toSearch,'friendList')

	def seq_process(self,toSearch,pageStyle):
		"""download and save record of `toSearch` in target pageStyle"""
		if isinstance(toSearch,str):
			toSearch={toSearch}
		for i,rid in zip(range(1,len(toSearch)+1),toSearch):
			meth_download=getattr(browser.browser,pageStyle)
			record,run_info=meth_download(self.dl,rid)
			if record is None:
				self.log.error('{},{},error info:{}'.format(rid,pageStyle,run_info))
			else:
				meth_save=getattr(repo_mysql.repo_mysql,'save_{}'.format(pageStyle))
				n=meth_save(self.repo,record,rid,run_info)
				log_text='{}/{},saved/download:{}/{},{} of {}, time={}'.format(i,len(toSearch),n,len(record),pageStyle,rid,run_info)
				if pageStyle=='profile':
					self.log.info('{}/{},{} {} record of {}'.format(i,len(toSearch),pageStyle,len(record),rid))
				elif n<len(record):
					self.log.error(log_text)
				else:
					self.log.info(log_text)
					self.searched[pageStyle].add(rid)
			# speed control
			if pageStyle == 'profile':
				time.sleep(pf_sleep)
