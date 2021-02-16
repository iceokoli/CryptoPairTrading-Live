# CryptoPairTrading-Live

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

- At 01:00 the strategy is kicked off
    ```zsh
    30 1 * * * python3 run.py
    ```

- At 23:45 the strategy is stopped
    ```zsh
    30 1 * * * sudo pkill python
    ```