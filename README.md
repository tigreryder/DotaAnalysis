Dota 2 is a multiplayer team computer game in which two teams of 5 battle it out. Each player can pick from one of 111 heroes (as of writing), with on the order of 10^16 possible matchup combinations. The publisher of Dota 2, Valve, makes match information available to be called from their API. In this repository, I used machine learning to predict the winner of a match of Dota 2.

Since each of the heroes in Dota 2 is unique in its own way, there is a widespread belief that in different situations, some heroes are better than others, effectively behaving in a rock-paper-scissors sort of manner. The stage where the heroes are picked is called the "draft", and there is a widespread belief that the outcome of a game is effectively determined by the draft. I created my own mathematical model to attempt to predict the winner of a game based purely on the draft by looking at empirical winrates of heroes by themselves, winrates of heroes when on a team with specific other heroes, and winrates of heroes when playing against specific heroes on the other team. My model has a promising amount of success, roughly 65%. This model can be found at:
https://github.com/tigreryder/DotaAnalysis/blob/master/Model_for_Predicting_Dota_2_Winner.ipynb

While coming up with my own mathematical model to determine draft winners was interesting, I also wanted to utilize a machine learning algorithm that I was familiar with. Considering that win/loss is a two-state switch, logistic regression could be applied, resulting in roughly a 65% correct prediction rate. That model can be found at:
https://github.com/tigreryder/DotaAnalysis/blob/master/Logistic_Regression_for_Predicting_Dota_2_Winner.ipynb

I was also curious in looking at my own statistics to see how I've done at this video game, how I could improve, and how I've done when playing with friends.
https://github.com/tigreryder/DotaAnalysis/blob/master/Win_Rates_Against_Match_Length_and_Prior_Match_Results.ipynb

Use dota_request for requesting match data (may take a few hours depending on number of matches); will save data locally so that it does not need to be requested in the future unless more matches have been played

Note: For mining the matches of a specific player, PlayerID refers to a player's Steam 3 ID for both calling the API (to request a specific player's matches) and for data sorting purposes (player participants listed by ID). Steam 3 IDs can be found using steamidfinder.com by searching the player's name.
