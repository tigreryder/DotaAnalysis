import json
import requests
import numpy as np
import pandas as pd
import argparse
import time

parser = argparse.ArgumentParser(description="Pulls Dota 2 API information on matches")
parser.add_argument("-k", "--key", help="Steam API key", required=True)
args = parser.parse_args()

key = args.key                        #personal Steam WebAPI key
playerID = '46667982'                 #enter Steam playerID to only find matches for that player

def retrieve_match_IDs_by_hero(playerID,key,heroID,startAtMatch='0'):
    '''
    Retrieves match history information for a player in json format and then returns
    a list of matchIDs the player was involved in to be used to retrieve match details
    
    Regardless of parameters enetered, WebAPI will only return the 500 most recent matches
    (100 at a time maximum); to get around this, implement a for loop to search matches
    by hero played assuming no hero has been played more than 500 times.
    
    Parameters
    -----------
    playerID (str): Numerical Steam playerID
    key (str): Personal Steam WebAPI key
    startAtMatch (str): Tells API what match to start at and returns descending matches
                        Disables when 0. When non-zero, take the latest matchID found and subtract
                        one to be used in function recursion.
    heroID (str): Hero numerical identifier to serach matches where playerID played heroID.
                  Default of 0 searches by any hero.
    '''
    
    r = requests.get('https://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/V001/?matches_requested=100&account_id=%s&key=%s&start_at_match_id=%s&hero_id=%s' % (playerID, key, startAtMatch, heroID))
    resultJ = json.loads(r.text)
    matchIDList = []
    for match in resultJ['result']['matches']:
        matchIDList.append(match['match_id'])
    
    if len(resultJ['result']['matches']) == 100:    #if pulled full 100 matches, request next set of 100 until all matches retrieved
        newStart = matchIDList[-1]-1
        matchIDList = matchIDList + retrieve_match_IDs_by_hero(playerID,key,heroID,newStart)
        time.sleep(1)        #to avoid rejection from calling API too often
    
    return matchIDList


def retrieve_all_match_IDs(playerID,key):
    '''
    Uses retrieve_match_IDs_by_hero and parses through every hero currently in the game
    110 heroes currently with IDs ranging from 1 to 112 as of October 2015
    '''
    
    matchIDList = []
    heroRange = list(range(1,113))   #heroIDs range from 1 to 112 currently
    heroRange.remove(24)             #no hero with ID 24... strangely
    heroRange.remove(108)            #no hero with ID 108 yet, probably Pitlord or Arc Warden
    
    for hero in heroRange:
        matchIDList = matchIDList + retrieve_match_IDs_by_hero(playerID,key,str(hero),'0')
        
    return matchIDList

def create_dota_dataframe(matchDetailsList):
    
    '''
    Takes in list of match detail json strings and converts
    into a pandas dataframe for easier statistical manipulation
    '''

    playerID = []                 #initialize lists for stats of interest
    playerSlot = []
    playerKills = []
    playerDeaths = []
    playerAssists = []
    playerGPM = []
    playerXPM = []
    playerHeroDamage = []
    playerTowerDamage = []
    playerLevel = []
    playerHeroID = []
    gameWonStatus = []
    matchID = []
    matchLength = []
    matchCounter = []
    gameStartTime = []

    for match in matchDetailsList:    #construct lists
        for player in match['result']['players']:
            playerID.append(player['account_id'])
            playerSlot.append(player['player_slot'])
            playerKills.append(player['kills'])
            playerDeaths.append(player['deaths'])
            playerAssists.append(player['assists'])
            playerGPM.append(player['gold_per_min'])
            playerXPM.append(player['xp_per_min'])
            playerHeroDamage.append(player['hero_damage'])
            playerTowerDamage.append(player['tower_damage'])
            playerLevel.append(player['level'])
            playerHeroID.append(player['hero_id'])
            if ((player['player_slot'] == 0) or (player['player_slot'] == 1) or (player['player_slot'] == 2) or (player['player_slot'] == 3) or (player['player_slot'] == 4)) and match['result']['radiant_win'] == True:
                gameWonStatus.append(1)
            elif ((player['player_slot'] == 128) or (player['player_slot'] == 129) or (player['player_slot'] == 130) or (player['player_slot'] == 131) or (player['player_slot'] == 132)) and match['result']['radiant_win'] == False:
                gameWonStatus.append(1)
            else:
                gameWonStatus.append(0)
            matchID.append(match['result']['match_id'])
            matchLength.append(match['result']['duration'])
            matchCounter.append(1)
            gameStartTime.append(match['result']['start_time'])

    #construct dictionary to build data frame
    referenceDict = {'Player ID': playerID, 'Player Slot': playerSlot, 'Kills': playerKills, 'Deaths': playerDeaths, 'Assists': playerAssists, 'GPM': playerGPM, 'XPM': playerXPM, 'Hero Damage': playerHeroDamage, 'Tower Damage': playerTowerDamage, 'Level': playerLevel, 'Hero ID': playerHeroID, 'Win Y/N': gameWonStatus, 'Match ID': matchID, 'Match Length (s)': matchLength, 'Match Counter': matchCounter, 'Game Start Time': gameStartTime}
    dataFrameSummary = pd.DataFrame(data=referenceDict)

    return dataFrameSummary

def get_stats(interestedPlayer, dataSummary):
    '''
    Reads in a dataframe and pumps out interesting/funny statistics about a player
    
    Parameters
    ----------
    interestedPlayer (str): numerical player ID as stored by steam API information
    dataSummary (dataframe): dataframe of data compiled from match history information
    
    Returns nothing, but prints out:
        Average deaths per minute in losses
        Average deaths per minute in wins
        Win-loss record when playing with me
        Average game length of wins (with me)
        Average game length of losses (with me)
        Average KDA over all games as Blue player (player slot 0)
        Total number of deaths over all games as Pink player (player slot 128)
    
    '''
    
    tempDF = dataSummary.groupby(['Player ID', 'Win Y/N']).aggregate(sum)
    averageDPMinWin = float(tempDF.loc[interestedPlayer, 1]['Deaths'])/tempDF.loc[interestedPlayer, 1]['Match Length (s)'] * 60.0
    averageDPMinLoss = float(tempDF.loc[interestedPlayer, 0]['Deaths'])/tempDF.loc[interestedPlayer, 0]['Match Length (s)'] * 60.0
    averageWinLength = tempDF.loc[interestedPlayer, 1]['Match Length (s)']/tempDF.loc[interestedPlayer, 1]['Match Counter']
    averageLossLength = tempDF.loc[interestedPlayer, 0]['Match Length (s)']/tempDF.loc[interestedPlayer, 0]['Match Counter']
    
    tempDF2 = dataSummary.groupby(['Player ID', 'Player Slot']).aggregate(sum)
    blueKDA = (tempDF2.loc[interestedPlayer, 0]['Kills']+tempDF2.loc[interestedPlayer, 0]['Assists'])/tempDF2.loc[interestedPlayer, 0]['Deaths']
    pinkTotalDeaths = tempDF2.loc[interestedPlayer, 0]['Deaths']
    
    print('Player\'s ID: %s' % interestedPlayer)
    print('Player\'s win-loss when playing with you: ' + str(tempDF.loc[interestedPlayer,1]['Match Counter']) + '-' + str(tempDF.loc[interestedPlayer,0]['Match Counter']) + ' (' + str(tempDF.loc[interestedPlayer,1]['Match Counter']/(tempDF.loc[interestedPlayer,1]['Match Counter']+tempDF.loc[interestedPlayer,0]['Match Counter'])) + ')')
    print('Player\'s average deaths per minute in wins is %s over %s matches' % (averageDPMinWin, tempDF.loc[interestedPlayer, 1]['Match Counter']))
    print('Player\'s average deaths per minute in losses is %s over %s matches' % (averageDPMinLoss, tempDF.loc[interestedPlayer, 0]['Match Counter']))
    print('Player\'s average game length when winning with you: %s seconds' %averageWinLength)
    print('Player\'s average game length when losing with you: %s seconds' %averageLossLength)
    print('Player\'s average KDA as Blue: %s' % blueKDA)
    print('Player\'s total deaths as Pink: %s' % pinkTotalDeaths)

    return None



matchIDList = retrieve_all_match_IDs(playerID,key)

matchDetails = []
for match in matchIDList:
    rTemp = requests.get('https://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/V001/?match_id=%s&key=%s' % (match, key))
    matchDetails.append(json.loads(rTemp.text))
    time.sleep(1)

matchDetails[:] = [match for match in matchDetails if ('result' in match)]             #removes erroneous matches as some are special matches
matchDetails[:] = [match for match in matchDetails if ('players' in match['result'])]  #without the same dictionary entries

dotaDataFrame = create_dota_dataframe(matchDetails)

with open('matchdetails.txt', 'w') as text:                 #save raw json data so we don't have to call the API again for same data
    json.dump(matchDetails, text)

dotaDataFrame.to_csv('matchhistory.csv', encoding='utf-8')   #save filtered match summary information

get_stats(30999748,dotaDataFrame)    #get some fun stats about player '30999748' aka feeder