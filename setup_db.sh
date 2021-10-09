#!/bin/sh

clear
python -c "from webapp import db; db.create_all()"