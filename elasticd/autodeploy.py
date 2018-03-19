#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@project= elasticd
@file= autodeploy
@author= wubingyu
@create_time= 2018/3/16 下午2:22
"""
import paramiko
import os
import shutil
import elasticd


def get_servers():
	global servers
	servers = elasticd.query_db('select * from servers ORDER by id ')

