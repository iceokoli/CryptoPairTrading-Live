check_process(){
    # check the args
    if [ "$1" = "" ];
    then
        return 0
    fi
    
    #PROCESS_NUM => get the process number regarding the given thread name
    PROCESS_NUM=$(ps -ef | grep "$1" | grep -v "grep" | wc -l)
    # for degbuging...
    $PROCESS_NUM
    if [ $PROCESS_NUM -eq 1 ];
    then
        return 1
    else
        return 0
    fi
}


echo 'begin checking...'
check_process "python3 CryptoPairTrading-Live/run.py" # the thread name
CHECK_RET = $?
if [ $CHECK_RET -eq 0 ]; # none exist
then
    python3 ~/CryptoPairTrading-Live/run.py
fi
