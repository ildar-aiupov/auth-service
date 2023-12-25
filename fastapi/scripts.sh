#!/bin/bash

alembic upgrade head
python createsuperuser.py admin admin
python main.py
