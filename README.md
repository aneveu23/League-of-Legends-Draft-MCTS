# League-of-Legends-Draft-MCTS
This is a personal project in which I will be assembling a dataset of high elo League of Legends games using Riot Games' API. I will then use this data to train a model (GBDT or NN) to assign a win probability to each team in a League of Legends game, based on the champions they have selected. Finally, I will apply the model to rollouts of a Monte Carlo Tree Search as a reward function, in order to determine the best pick/ban at each stage of a League of Legends draft.

## Data Acquisition
Riot Games' API does not allow users to get games for a desired rank directly. Nevertheless, there is a specific sequence of actions that one can take to accomplish this task. The steps are as follows:

### Acquiring Summoner IDs
Riot's League v4 API allows users to get information about individual ranks, including an encrypted summoner ID of every single player in that rank. For Challenger, Grandmaster, or Master, the user is allowed to request information about the entire rank simultaneously. For any other rank, the user is only allowed to get information about a single page of a rank; to circumvent this issue, one can simply iterate through page values until observing an empty page. I opted to get the summoner ID for all Diamond II + players on the North America, Europe West, and Korea servers. Note that summoner IDs are unique within each region.

### Converting Summoner IDs to PUUIDs
Riot's Match v5 API allows users to get up to 100 games played by a given player in a specified time period and queue type. However, this API call depends on a summoner's PUUID, which is a globally unique id assigned to each summoner. To address this, Riot's Summoner v4 allows users to get summoner-specific information, including PUUID, based on an input summoner ID. I opted to retrieve/assign the PUUID for/to each summoner ID that I stored previously.
