
export VIRTUALENV_NAMESPACE='.trig_egamma_frame-env'
export LOGURU_LEVEL=INFO
export VIRTUALENV_PATH=$PWD/$VIRTUALENV_NAMESPACE

export CERN_DATA="/mnt/shared/storage03/projects/cern/data"

if [ -d "$VIRTUALENV_PATH" ]; then
    echo "$VIRTUALENV_PATH exists."
    source $VIRTUALENV_PATH/bin/activate
else
    virtualenv -p python ${VIRTUALENV_PATH}
    source $VIRTUALENV_PATH/bin/activate
    pip install -e .
fi
