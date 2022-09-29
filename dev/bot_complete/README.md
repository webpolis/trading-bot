# Short-bot
Automatic short strategy following big crypto wallets

## Idea:
For the most traded tokens, we'll follow X% (ex X = 30%) of most important wallets (in terms of market participation in that token) in order to identify the sell pressure and its velocity.

Our hypothesis is that the movement of these whales could iniciate/intensify a fall in the token (short opportunity).
Analogously for a long strategy.

------------------------------------------------------------

### Methodology:
1) Select a token from the top ranking of coingecko that is able to be shorted in any CEX available in USA (ex Kucoin)
2) Track X% of top holding addresses for that token (we could probably build a database with top addresses for several tokens) and give them a weight according to its market share
3) Follow (using a scrapper that takes info from the token address + blockchain scanner, for ex) the txs made by these top addresses 
 - Idea: for every tx (in the blockchain scanner) find those that came from any of the top addresses
   - load the txs made by the top addresses in the last T minutes (for some T); save the total sold amount; assing a weight to the wallet according to the sell size with respect to the wallet's market share
   - define the analysis (first theoretically, later algorithmically) that the scrapper has to do
   - we have to define the frequency at which the scanner will check new txs and trigger the analysis [ex: every 3hs, every day (ex. today wallet Y sold 1Musd, tomorrow 1.30Musd (30%+), etc)] --> THE IDEA IS TO TRACK THE VELOCITY OF SELLING
4) In parallel we should follow the token price
 - check if its trend reflects whales actions 
  - subject to market sentiment (if for ex ADA is going up but the whole market is crashing and the whales are/were selling, then the recent ADA movement shouldnt be a contradictory signal)

------------------------------------------------------------

### Scoring inputs:
- wallets' selling relative to their market participation
- price movement
- market sentiment


