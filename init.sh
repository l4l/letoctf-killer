#!/bin/sh

python gen.py - aims.dat
rm -f t.db
cat db.sql | sqlite3 t.db
