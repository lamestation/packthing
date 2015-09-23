#!/bin/bash
set -e

DEFAULT_DIR=/opt/
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

INSTALL_DIR=$DEFAULT_DIR

usage()
{
    echo "Usage: $0 [--prefix DIR]"
    echo "    --prefix DIR   install ${APPLICATION} to the specified location."
    echo "                   default: ${DEFAULT_DIR}"
    exit 0
}

while true
do
    case "$1" in
    --prefix)
        INSTALL_DIR=$2
        if ! shift 2; then usage; exit 1; fi
        ;;
    -h | --help)
	usage
	;;
    -*)
	echo Unknown command: "$1"
	usage
	;;
    *)
	break
	;;
    esac
done

if [ -z $INSTALL_DIR ] ; then usage ; exit 1; fi

NEWDIR=`basename $DIR | cut -d'-' -f 1`


echo "${APPLICATION} will install to: $INSTALL_DIR"
echo -n "Are you sure you want to continue? (y/N): "

read yesno

if [[ "$yesno" != "y" ]] ; then echo "Aborting."; exit 0; fi

pushd $DIR >/dev/null
mkdir -p $INSTALL_DIR/$NEWDIR
cp -r * $INSTALL_DIR/$NEWDIR
popd >/dev/null

echo "${APPLICATION} ${VERSION} has been installed to $INSTALL_DIR."
