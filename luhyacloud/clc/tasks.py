# coding=UTF-8

from __future__ import absolute_import

from celery import task, current_task

from time import sleep
from celery import shared_task
from celery.utils.log import get_task_logger

from clc.models import *
from luhyaapi import *
from django.core.exceptions import ObjectDoesNotExist
import random, pickle, pexpect, os, base64, shutil, time
from datetime import datetime

logger = get_task_logger(__name__)
NUM_OBJ_TO_CREATE = 100
SERVER_TMP_ROOT = "/storage/tmp"
SERVER_ROOT     = "/storage"
SNAPSHOT_NAME   = "luhyaVM"


