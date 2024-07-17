BALANCE=~/Desktop/balance.txt
DIVIDEND=~/Desktop/dividend.txt
PNL=~/Desktop/pnl.txt

#cd ~/Projects/assetsdev
python3 -m assets.update --provider finam
python3 -m assets.balancereport | tee $BALANCE
python3 -m assets.dividendreport | tee $DIVIDEND
python3 -m assets.pnlreport | tee $PNL
