#!/bin/sh


_proyect_root=$(pwd)
_dblpdataset_uri="http://dblp.uni-trier.de/xml/dblp.xml.gz"
_dblpdataset_folder="dblpdataset2"

# echo "Downloading DBLP dataset from ${_dblpdataset_uri}"
# cd ${_dblpdataset_folder}
# curl -O ${_dblpdataset_uri}
# gzip -d dblp.xml.gz
# cd ${_proyect_root}
# sudo pip install -r data-crawler/requriments.txt
# sudo pip install -r preprocessing/requirements.txt
# cd ${_dblpdataset_folder}

DIRS=`ls -l ${_dblpdataset_folder} | grep '^d'`
for DIR in $DIRS
do
	echo ${DIR}
done