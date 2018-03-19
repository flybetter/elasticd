#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@project= elasticd
@file= logstash
@author= wubingyu
@create_time= 2018/3/16 上午10:30
"""
import elasticd


def open_settings():
	settings = elasticd.query_db('select * from settings order BY id ')
	with open(elasticd.app.config['logstash_path'], mode='wr') as f:
		for setting in settings:
			f.write(setting['content'])

		f.write('\noutput{\n'
				'	elasticsearch{\n'
				'		index => "testdb"\n'
				'		document_type => "%{type}"   # <- use the type from each input\n'
				'		hosts => "localhost:9200"\n'
				'		document_id => "%{threadid}"\n'
				'	}\n'
				'}\n')


if __name__ == '__main__':
	open_settings()
