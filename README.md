# CryptoPairTrading-Live

## Context & Back Testing

https://github.com/iceokoli/CryptoPairTrading-BackTest

## Set up

Deplyed on an AWS EC2 instance
```zsh
sudo apt-get install python3-pip --yes
pip install -r requirments.txt
```

## Operations

Handled by cron jobs.

- At 00:30 batch aggreagates required for the strategy are calculated by

    ```zsh
    30 0 * * * python3 batch_aggreagates.py
    ```

- At 01:30 the strategy is kicked off
    ```zsh
    30 1 * * * python3 run.py
    ```

- At 23:50 the strategy is stopped
    ```zsh
    50 23 * * * sudo pkill python
    ```
